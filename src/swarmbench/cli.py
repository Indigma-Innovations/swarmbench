"""Command line: list the catalog, run a mode, reproduce the stored results, write reports.

    swarmbench --list
    swarmbench --mode solo --agents cycle-aware identified-robust --seeds 100
    swarmbench --mode head-to-head --agents template kelly naive-max proportional --seeds 20
    swarmbench --mode all-together --agents realistic bots --seeds 10
    swarmbench --mode solo --agents realistic --opponents energy-hoarder contrarian random
    swarmbench --reproduce                          # the three main experiments, checked bit for bit
    swarmbench --reproduce --mode solo --seeds 5    # quick check on the first 5 seeds
    swarmbench --reproduce --experiments all        # every stored experiment
    swarmbench --report runs/swarmbench/solo
    swarmbench --metagame results/paper/head-to-head   # Nash averaging (needs the analysis extra)
    swarmbench --import my_agents --mode solo --agents my-agent cycle-aware

Agent lists accept catalog keys and the groups ``paper`` (all 36 roster
entries), ``agents``, ``bots``, ``realistic`` and ``distinct``.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import time

from . import __version__
from .catalog import import_agents, ordered, resolve
from .modes import BOTS, MODES, jobs, run_mode

RESULTS = Path("results") / "paper"       # stored results, relative to the current directory
RUNS = Path("runs")                       # default output folder for new runs


def _progress(label: str):
    started = time.time()
    tty = sys.stdout.isatty()

    def report(done: int, total: int) -> None:
        if done == total or done % max(1, total // 100) == 0:
            elapsed = time.time() - started
            eta = elapsed / max(1, done) * (total - done)
            end = "" if tty and done < total else "\n"
            prefix = "\r" if tty else ""
            print(f"{prefix}{label}: {done}/{total} episodes  "
                  f"elapsed {elapsed / 60:.1f} min  eta {eta / 60:.1f} min", end=end, flush=True)
    return report


def list_agents() -> None:
    """Print the catalog in idea order."""
    print(f"{'#':>3}  {'key':24} {'realistic':9}  {'family':28} name")
    for i, spec in enumerate(ordered(), start=1):
        tag = "yes" if spec.realistic else "no"
        note = f"  [{spec.note}]" if spec.note else ""
        print(f"{i:>3}  {spec.key:24} {tag:9}  {spec.family:28} {spec.name}{note}")


def run(mode: str, agents: list[str], seeds: int, seed_start: int, workers: int, output: Path,
        rounds: int | None = None, opponents: list[str] | None = None,
        capacity_scale: float | str = 1.0, focus: list[str] | None = None, name: str | None = None) -> Path:
    """Run a mode into ``output`` (spec.json, episodes.jsonl) and write its report."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    entries = [s.key for s in resolve(agents)]
    opponents = tuple(s.key for s in resolve(opponents)) if opponents else BOTS
    spec = {"mode": mode, "agents": entries, "seed_start": seed_start, "seeds": seeds,
            "scenario": "graded", "rounds": rounds or 60, "workers": workers, "python": sys.version.split()[0]}
    if opponents != BOTS:
        spec["opponents"] = list(opponents)
    if capacity_scale != 1.0:
        spec["capacity_scale"] = capacity_scale
    if focus:
        spec["focus"] = [s.key for s in resolve(focus)]
    if name:
        spec["name"] = name
    (output / "spec.json").write_text(json.dumps(spec, indent=1), encoding="utf-8")
    run_mode(mode, entries, range(seed_start, seed_start + seeds), workers=workers,
             output=output / "episodes.jsonl", rounds=rounds, progress=_progress(mode),
             opponents=opponents, capacity_scale=capacity_scale,
             focus=[s.key for s in resolve(focus)] if focus else ())
    from .report import write_report
    write_report(output)
    print(f"results and report: {output}")
    return output


def _stored_name(spec: dict) -> str:
    name = spec.get("name") or spec["mode"]
    if not spec.get("name"):
        if spec.get("opponents"):
            name = f"{name}-heldout"
        if spec.get("capacity_scale", 1.0) != 1.0:
            name = f"{name}-scaled"
    return name


def publish(folder: Path, results: Path = RESULTS) -> Path:
    """Store a finished run in compact form: ``<results>/<name>`` with spec, csv.gz, summary, report."""
    from .report import export_compact, load_rows, write_report
    folder = Path(folder)
    spec = json.loads((folder / "spec.json").read_text(encoding="utf-8"))
    name = _stored_name(spec)
    expected = len(jobs(spec["mode"], spec["agents"], range(spec["seeds"]), spec.get("focus") or ()))
    found = len({(r["table"], r["seed"]) for r in load_rows(folder)})
    if found < expected:
        raise SystemExit(f"{folder}: {found}/{expected} episodes; the run is not finished")
    target = export_compact(folder, Path(results) / name)
    write_report(target)
    print(f"published {name}: {target}")
    return target


def stored_experiments(results: Path = RESULTS) -> list[str]:
    """Names of the stored experiments in ``results``."""
    return sorted(p.parent.name for p in Path(results).glob("*/spec.json"))


def reproduce(names: list[str], seeds: int | None, workers: int, output: Path, results: Path = RESULTS) -> int:
    """Re-run stored experiments (or their first ``seeds`` seeds) and compare every score bit for bit.

    Returns 0 when every participant score is identical, 1 otherwise."""
    from .report import load_rows
    results, output = Path(results), Path(output)
    if not results.is_dir():
        raise SystemExit(f"no stored results at {results}; pass --results DIR "
                         "(the repository's results/paper folder)")
    failures = 0
    for name in names:
        stored_dir = results / name
        if not (stored_dir / "spec.json").exists():
            raise SystemExit(f"no stored experiment {name!r} in {results}; "
                             f"available: {', '.join(stored_experiments(results))}")
        spec = json.loads((stored_dir / "spec.json").read_text(encoding="utf-8"))
        count = seeds or spec["seeds"]
        target = output / name
        if target.exists():
            shutil.rmtree(target)       # never resume a comparison from an earlier, possibly partial run
        run(spec["mode"], spec["agents"], count, spec["seed_start"], workers, target, spec.get("rounds"),
            spec.get("opponents"), spec.get("capacity_scale", 1.0), spec.get("focus"), spec.get("name"))
        stored = {(r["table"], r["seed"], r["agent"]): r["score"] for r in load_rows(stored_dir)}
        fresh = load_rows(target)
        same = sum(1 for r in fresh if stored.get((r["table"], r["seed"], r["agent"])) == r["score"])
        print(f"{name}: {same}/{len(fresh)} participant scores identical to {stored_dir}")
        failures += same != len(fresh)
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    """Entry point of the ``swarmbench`` command."""
    parser = argparse.ArgumentParser(prog="swarmbench", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--list", action="store_true", help="list the agent catalog")
    parser.add_argument("--mode", choices=MODES, help="solo, head-to-head or all-together")
    parser.add_argument("--agents", nargs="+", default=["paper"], help="catalog keys or groups (default: paper)")
    parser.add_argument("--seeds", type=int, help="number of seeds (default 100; all stored seeds for --reproduce)")
    parser.add_argument("--seed-start", type=int, default=70001, help="first seed (default 70001)")
    parser.add_argument("--rounds", type=int, help="override the 60-round graded run (testing only)")
    parser.add_argument("--opponents", nargs="+",
                        help="solo mode: replace the three supplied bots (e.g. the held-out set: "
                             "energy-hoarder contrarian random)")
    parser.add_argument("--focus", nargs="+",
                        help="head-to-head: only the pairs involving these entries (e.g. reference points)")
    parser.add_argument("--capacity-scale", default="1.0",
                        help="multiply pool capacities; 'auto' sizes them for the market (n/4)")
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 1,
                        help="parallel worker processes (default: all CPUs)")
    parser.add_argument("--output", type=Path, help="output folder (default runs/swarmbench/<mode>, "
                                                    "runs/reproduce for --reproduce)")
    parser.add_argument("--name", help="name of the experiment, used by --publish (results/<name>)")
    parser.add_argument("--import", dest="imports", action="append", default=[], metavar="MODULE",
                        help="import a module that registers agents (repeatable)")
    parser.add_argument("--reproduce", action="store_true",
                        help="re-run stored experiments and compare every score bit for bit")
    parser.add_argument("--experiments", nargs="+",
                        help="--reproduce: stored experiment names, or 'all' (default: the --mode "
                             "experiment, else solo, head-to-head and all-together)")
    parser.add_argument("--results", type=Path, default=RESULTS,
                        help="folder of stored results (default: results/paper in the current directory)")
    parser.add_argument("--report", type=Path, help="write the report for a results folder")
    parser.add_argument("--publish", type=Path, help="store a finished run in compact form under --results")
    parser.add_argument("--metagame", type=Path, metavar="FOLDER",
                        help="Nash averaging of a head-to-head results folder (needs scipy)")
    args = parser.parse_args(argv)
    import_agents(*args.imports)
    if args.list:
        list_agents()
        return 0
    if args.report:
        from .report import write_report
        print(write_report(args.report))
        return 0
    if args.publish:
        publish(args.publish, args.results)
        return 0
    if args.metagame:
        from .metagame import metagame
        result = metagame(args.metagame)
        for name, res in result.items():
            if name == "references":
                print("references:", res)
                continue
            top = sorted(res["rating"].items(), key=lambda kv: -kv[1])[:8]
            print(f"{name}: support {res['support']}, exploitability {res['exploitability']}")
            print("  top ratings:", ", ".join(f"{k} {v:+.3f}" for k, v in top))
        print(f"written: {args.metagame / 'metagame.json'}")
        return 0
    if args.reproduce:
        if args.experiments == ["all"]:
            names = stored_experiments(args.results)
        else:
            names = args.experiments or ([args.mode] if args.mode else list(MODES))
        return reproduce(names, args.seeds, args.workers, args.output or RUNS / "reproduce", args.results)
    if not args.mode:
        parser.error("choose --mode, --reproduce, --list, --report, --publish or --metagame")
    scale = args.capacity_scale if args.capacity_scale == "auto" else float(args.capacity_scale)
    run(args.mode, args.agents, args.seeds or 100, args.seed_start, args.workers,
        args.output or RUNS / "swarmbench" / args.mode, args.rounds, args.opponents, scale, args.focus,
        args.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
