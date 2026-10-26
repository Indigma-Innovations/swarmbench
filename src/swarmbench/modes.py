"""The three benchmark modes.

* ``solo``           each listed entry plays alone against the three supplied
                     bots (4 nodes): the original challenge setting. Other
                     opponents (e.g. the held-out set) can replace the bots.
* ``head-to-head``   every unordered pair of listed entries (agents or bots)
                     plays in a market of exactly those two.
* ``all-together``   every listed entry in one market.

Each mode returns per-participant rows (see engine.EpisodeResult) for every
episode; :func:`run_mode` runs them in parallel and can resume from a partial
results file.
"""

from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import multiprocessing
from pathlib import Path
from typing import Callable, Iterable

from . import catalog
from .catalog import get_spec, resolve
from .engine import Market, seat

MODES = ("solo", "head-to-head", "all-together")
BOTS = ("naive-max", "even-split", "proportional")


def jobs(mode: str, entries: list[str], seeds: Iterable[int], focus: Iterable[str] = ()) -> list[tuple]:
    """(mode, table, seed) tuples; ``table`` is a tuple of agent keys.

    ``focus`` (head-to-head): keep only the pairs that involve one of these entries,
    e.g. to add reference points to an existing tournament."""
    seeds, focus = list(seeds), set(focus)
    if mode == "solo":
        return [(mode, (key,), s) for key in entries for s in seeds]
    if mode == "head-to-head":
        pairs = [(a, b) for i, a in enumerate(entries) for b in entries[i + 1:]
                 if not focus or a in focus or b in focus]
        return [(mode, pair, s) for pair in pairs for s in seeds]
    if mode == "all-together":
        return [(mode, tuple(entries), s) for s in seeds]
    raise ValueError(f"mode must be one of {MODES}")


def play(job: tuple, scenario: str = "graded", rounds: int | None = None,
         opponents: tuple = BOTS, capacity_scale: float | str = 1.0) -> list[dict]:
    """Play one job ``(mode, table, seed)`` and return its participant rows.

    In solo mode only the entry under test is returned (with ``bots_score``,
    the opponents' total); otherwise every participant. ``capacity_scale="auto"``
    sizes the pools for the market (``n / 4`` for ``n`` nodes)."""
    mode, table, seed = job
    if capacity_scale == "auto":          # pools sized for the market: 4 nodes -> 1.0
        size = 2 if mode == "head-to-head" else len(table) + (len(opponents) if mode == "solo" else 0)
        capacity_scale = size / 4
    market = Market(scenario=scenario, rounds=rounds, capacity_scale=float(capacity_scale))
    if mode == "solo":
        # The entry under test takes the seat a team takes in the challenge;
        # the three bots keep their real names. A bot under test is renamed
        # so that it is one more participant, not a duplicate registration.
        # Held-out opponents (not the supplied bots) play under neutral names.
        seats = [seat(get_spec(b)) if b in BOTS else seat(get_spec(b), team=f"heldout-{b}", baseline=False)
                 for b in opponents]
        subject = get_spec(table[0])
        seats.append(seat(subject, team=f"agent-{subject.key}", baseline=False))
        rows = market.play(seed, seats).rows
        rows = [r for r in rows if r["team"] == f"agent-{subject.key}"]
        # in solo mode "others" are the three bots
        for r in rows:
            r["bots_score"] = r["others_score"]
    else:
        seats = [seat(get_spec(k)) for k in table]
        rows = market.play(seed, seats).rows
    for r in rows:
        r.update(mode=mode, table="|".join(table))
    return rows


def job_key(job: tuple) -> str:
    """The resume key of a job: ``mode:table:seed``."""
    return f"{job[0]}:{'|'.join(job[1])}:{job[2]}"


def run_mode(mode: str, agents: list[str], seeds: Iterable[int], workers: int = 4,
             output: Path | None = None, scenario: str = "graded", rounds: int | None = None,
             progress: Callable[[int, int], None] | None = None, opponents: tuple = BOTS,
             capacity_scale: float | str = 1.0, focus: Iterable[str] = ()) -> list[dict]:
    """Run a mode; rows are appended to ``output`` (JSON lines) as jobs finish.

    ``agents`` takes catalog keys and groups (see :func:`swarmbench.resolve`).
    Jobs already present in ``output`` are skipped, so an interrupted run
    resumes. With ``workers > 1`` jobs run in forked worker processes, which
    inherit agents registered in this process."""
    entries = [s.key for s in resolve(agents)]
    todo = jobs(mode, entries, seeds, focus)
    rows: list[dict] = []
    done: set[str] = set()
    if output and output.exists():
        for line in output.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                rows.append(row)
                done.add(f"{row['mode']}:{row['table']}:{row['seed']}")
    todo = [j for j in todo if job_key(j) not in done]
    total, finished = len(todo) + len(done), len(done)
    handle = output.open("a", encoding="utf-8") if output else None
    try:
        if workers <= 1:
            results = ((j, play(j, scenario, rounds, opponents, capacity_scale)) for j in todo)
            for _job, result in results:
                finished = _store(result, rows, handle, finished, total, progress)
        else:
            # fork lets workers inherit agents registered at run time; where it is
            # unavailable (Windows) workers re-import the modules given to import_agents
            if "fork" in multiprocessing.get_all_start_methods():
                context, initargs = multiprocessing.get_context("fork"), ()
            else:
                context, initargs = multiprocessing.get_context(), tuple(catalog._IMPORTED)
            with ProcessPoolExecutor(workers, mp_context=context, initializer=catalog.import_agents,
                                     initargs=initargs) as pool:
                futures = {pool.submit(play, j, scenario, rounds, opponents, capacity_scale): j for j in todo}
                for future in as_completed(futures):
                    finished = _store(future.result(), rows, handle, finished, total, progress)
    finally:
        if handle:
            handle.close()
    return rows


def _store(result: list[dict], rows: list, handle, finished: int, total: int, progress) -> int:
    rows.extend(result)
    if handle:
        for row in result:
            handle.write(json.dumps(row) + "\n")
        handle.flush()
    finished += 1
    if progress:
        progress(finished, total)
    return finished
