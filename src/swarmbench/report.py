"""Metrics, Markdown reports and figures for a results folder.

A results folder holds ``spec.json`` and ``episodes.jsonl`` (or the compact
``episodes.csv.gz`` of the stored results). :func:`write_report` adds
``summary.json``, ``report.md`` and, when matplotlib is installed (the
``report`` extra), ``figure.png``.
"""

import csv
import gzip
import io
import json
import math
from pathlib import Path
import statistics

from .catalog import FAMILIES, get_spec

REFERENCE = "cycle-aware"   # the selected submission, for paired comparisons in solo mode
COLUMNS = ["mode", "table", "seed", "agent", "team", "bot", "score", "rank", "nodes", "beat_all",
           "participated", "idle", "missed", "floors", "exceptions", "decisions", "ms_mean", "ms_max",
           "others_score", "lsw_total", "welfare"]
NUMERIC = {"seed", "score", "rank", "nodes", "participated", "idle", "missed", "floors", "exceptions",
           "decisions", "ms_mean", "ms_max", "others_score", "lsw_total", "welfare"}


# ---------------------------------------------------------------------------
# Loading and exporting
# ---------------------------------------------------------------------------
def load_rows(folder: Path) -> list[dict]:
    """The participant rows of a results folder (``episodes.jsonl`` or ``episodes.csv.gz``)."""
    folder = Path(folder)
    if (folder / "episodes.jsonl").exists():
        return [json.loads(line) for line in (folder / "episodes.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()]
    if (folder / "episodes.csv.gz").exists():
        with gzip.open(folder / "episodes.csv.gz", "rt", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            for key in NUMERIC:
                if key in row and row[key] != "":
                    value = float(row[key])
                    row[key] = int(value) if key in ("seed", "rank", "nodes", "participated", "idle", "missed",
                                                    "floors", "exceptions", "decisions") else value
            for key in ("bot", "beat_all"):
                row[key] = row.get(key) in ("True", "true", "1")
        return rows
    return []


def export_compact(folder: Path, target: Path) -> Path:
    """Write the committed form of a results folder: spec, csv.gz, summary, report."""
    folder, target = Path(folder), Path(target)
    target.mkdir(parents=True, exist_ok=True)
    rows = load_rows(folder)
    rows.sort(key=lambda r: (r["table"], r["seed"], r["agent"]))
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        # scores keep full precision so --reproduce can compare them bit for bit
        writer.writerow({k: (round(row[k], 6) if isinstance(row.get(k), float) and k != "score" else row.get(k))
                         for k in COLUMNS})
    with gzip.GzipFile(target / "episodes.csv.gz", "wb", mtime=0) as handle:
        handle.write(buffer.getvalue().encode("utf-8"))
    (target / "spec.json").write_text((folder / "spec.json").read_text(encoding="utf-8"), encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
def ci95(values: list) -> float:
    """Half-width of the normal 95% confidence interval of the mean."""
    return 1.96 * statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else 0.0


def meta(key: str) -> dict:
    """Catalog metadata of an entry, as stored in summaries."""
    spec = get_spec(key)
    return {"key": spec.key, "name": spec.name, "family": spec.family, "order": spec.order,
            "realistic": spec.realistic, "bot": spec.bot}


def _falls_back(key: str) -> str | None:
    """The catalog entry this agent plays exactly as among unnamed rivals, if any."""
    try:
        return get_spec(key).falls_back_to
    except KeyError:
        return None


def _is_reference(key: str) -> bool:
    """Reference points and held-out opponents, which are not counted as opponents."""
    try:
        return get_spec(key).family == FAMILIES[-1]
    except KeyError:
        return False


def summarize(rows: list[dict], mode: str) -> dict:
    """Per-entry metrics of a mode's rows.

    Every entry gets mean score with a 95% interval, ranks, first places,
    idle rounds, floor violations, exceptions, ms per decision, welfare and
    log social welfare. Solo mode adds the paired gain over ``cycle-aware``;
    head-to-head adds win rate, the win rate over distinct opponents (an
    opponent that plays exactly as another participant of the run counts once,
    and reference points are not counted),
    opponents beaten, margin and the pairwise matrix under ``_matrix``."""
    by: dict = {}
    for row in rows:
        by.setdefault(row["agent"], []).append(row)
    out = {}
    reference = {r["seed"]: r["score"] for r in by.get(REFERENCE, [])} if mode == "solo" else {}
    for key, items in by.items():
        scores = [r["score"] for r in items]
        decisions = sum(r["decisions"] for r in items)
        entry = {**meta(key), "episodes": len(items), "mean_score": statistics.fmean(scores),
                 "ci95": ci95(scores), "mean_rank": statistics.fmean(r["rank"] for r in items),
                 "first": sum(r["rank"] == 1 for r in items),
                 "beat_all": sum(bool(r["beat_all"]) for r in items),
                 "idle": statistics.fmean(r["idle"] for r in items),
                 "floors": statistics.fmean(r["floors"] for r in items),
                 "missed": sum(r["missed"] for r in items),
                 "exceptions": sum(r["exceptions"] for r in items),
                 "ms_mean": (sum(r["ms_mean"] * r["decisions"] for r in items) / decisions) if decisions else 0.0,
                 "ms_max": max(r["ms_max"] for r in items),
                 "lsw": statistics.fmean(r["lsw_total"] for r in items),
                 "welfare": statistics.fmean(r["welfare"] for r in items),
                 "others_score": statistics.fmean(r["others_score"] for r in items)}
        if reference and key != REFERENCE:
            paired = [(r["score"], reference[r["seed"]]) for r in items if r["seed"] in reference]
            gains = [100 * (a / b - 1) for a, b in paired if b > 0]
            entry.update(gain_vs_reference=statistics.fmean(gains), gain_ci95=ci95(gains),
                         wins_vs_reference=sum(a > b for a, b in paired),
                         losses_vs_reference=sum(a < b for a, b in paired))
        out[key] = entry
    if mode == "head-to-head":
        matrix = pairwise(rows)
        for key, row in matrix.items():
            wins = [w for w, _ in row.values()]
            games = sum(n for _, n in row.values())
            out[key]["win_rate"] = sum(w * n for w, n in row.values()) / games if games else float("nan")
            out[key]["opponents_beaten"] = sum(w > 0.5 for w in wins)
            margins = [r["score"] - r["others_score"] for r in by[key]]
            out[key]["margin"] = statistics.fmean(margins)
        out["_matrix"] = {a: {b: w for b, (w, _) in row.items()} for a, row in matrix.items()}
        present = set(matrix) | {b for row in matrix.values() for b in row}
        duplicates = {b for b in present if _falls_back(b) in present or _is_reference(b)}
        for key, row in matrix.items():
            distinct = [w for b, (w, _) in row.items() if b not in duplicates]
            out[key]["win_rate_distinct"] = statistics.fmean(distinct) if distinct else float("nan")
    ranking = sorted((k for k in out if not k.startswith("_")), key=lambda k: -out[k]["mean_score"])
    for position, key in enumerate(ranking, start=1):
        out[key]["score_rank"] = position
    if mode == "head-to-head":
        ranking = sorted((k for k in out if not k.startswith("_")), key=lambda k: -out[k]["win_rate"])
        for position, key in enumerate(ranking, start=1):
            out[key]["win_rank"] = position
    return out


def pairwise(rows: list[dict]) -> dict:
    """``matrix[a][b] = (share of a-vs-b episodes a won, ties count 1/2; episodes)``."""
    tables: dict = {}
    for row in rows:
        tables.setdefault((row["table"], row["seed"]), []).append(row)
    tally: dict = {}
    for items in tables.values():
        for x in items:
            for y in items:
                if x["agent"] == y["agent"]:
                    continue
                cell = tally.setdefault(x["agent"], {}).setdefault(y["agent"], [0.0, 0])
                cell[0] += 1.0 if x["score"] > y["score"] else 0.5 if x["score"] == y["score"] else 0.0
                cell[1] += 1
    return {a: {b: (w / n, n) for b, (w, n) in row.items()} for a, row in tally.items()}


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------
TITLES = {"solo": "Solo: each entry against the three supplied bots",
          "head-to-head": "Head-to-head: every pair of entries, alone in a market",
          "all-together": "All together: every entry in one market"}


def _ms(x: float) -> str:
    return f"{x:.3f}" if x < 1 else f"{x:.1f}" if x < 100 else f"{x:.0f}"


def _yes(flag: bool) -> str:
    return "yes" if flag else "no"


def _title(spec: dict, mode: str) -> str:
    title = TITLES[mode]
    if spec.get("opponents"):
        title = f"Solo: each entry against held-out opponents ({', '.join(spec['opponents'])})"
    if spec.get("capacity_scale", 1.0) != 1.0:
        title += f" (capacity scale {spec['capacity_scale']})"
    return title


def markdown(summary: dict, spec: dict, mode: str, figure: str | None) -> str:
    """The Markdown report of a summary."""
    agents = sorted((k for k in summary if not k.startswith("_")), key=lambda k: summary[k]["order"])
    seeds = spec["seeds"]
    title = _title(spec, mode)
    lines = [f"# {title}", "",
             f"Seeds {spec['seed_start']}–{spec['seed_start'] + seeds - 1} ({seeds}), `graded` scenario, "
             f"{spec.get('rounds', 60)} rounds, unchanged arena engine in-process. Every participant has the "
             "same device (minted from the seed and a fixed device label). Agents are listed in idea order: "
             "traditional rules, optimization, model-based planning, machine learning. **Realistic** = never "
             "uses the bots' names or code, so it can face unnamed opponents.", ""]
    if figure:
        lines += [f"![{title}]({figure})", ""]
    if mode == "solo":
        lines += ["| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | "
                  f"Δ vs {REFERENCE} (paired) | W/L vs {REFERENCE} | Beat all bots | Mean rank (of 4) | Idle | "
                  "Floors | Exceptions | ms mean | ms max | Log social welfare | Bots' score | Welfare (Σ scores) |",
                  "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for i, key in enumerate(agents, start=1):
            s = summary[key]
            gain = (f"{s['gain_vs_reference']:+.2f}% ±{s['gain_ci95']:.2f}" if "gain_vs_reference" in s
                    else "reference" if key == REFERENCE else "—")
            wl = f"{s['wins_vs_reference']}/{s['losses_vs_reference']}" if "wins_vs_reference" in s else "—"
            lines.append(
                f"| {i} | {s['name']} (`{key}`) | {s['family']} | {_yes(s['realistic'])} | "
                f"{s['mean_score']:.3f} | {s['ci95']:.3f} | {s['score_rank']} | {gain} | {wl} | "
                f"{s['beat_all']}/{s['episodes']} | {s['mean_rank']:.2f} | {s['idle']:.1f} | {s['floors']:.2f} | "
                f"{s['exceptions']} | {_ms(s['ms_mean'])} | {_ms(s['ms_max'])} | {s['lsw']:.1f} | "
                f"{s['others_score']:.2f} | {s['welfare']:.2f} |")
        lines += ["", "Log social welfare is the arena's Σ_i log u_i summed over rounds for the 4-node market; "
                  "welfare is the sum of all four final scores. Δ is the mean per-seed relative gain with a "
                  "normal 95% interval; W/L counts seeds with a strictly higher/lower score."]
    elif mode == "head-to-head":
        lines += ["| # | Agent | Family | Realistic | Matches | Win rate | Win rate (distinct) | Win rank | "
                  "Opponents beaten (>50%) | Mean score | Mean margin | Idle | Floors | Exceptions | "
                  "ms mean | ms max | "
                  "Log social welfare | Welfare (Σ scores) |",
                  "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        n = len(agents)
        for i, key in enumerate(agents, start=1):
            s = summary[key]
            lines.append(
                f"| {i} | {s['name']} (`{key}`) | {s['family']} | {_yes(s['realistic'])} | "
                f"{s['episodes']} | {s['win_rate']:.3f} | {s.get('win_rate_distinct', float('nan')):.3f} | "
                f"{s['win_rank']} | {s['opponents_beaten']}/{n - 1} | "
                f"{s['mean_score']:.3f} | {s['margin']:+.3f} | {s['idle']:.1f} | {s['floors']:.2f} | "
                f"{s['exceptions']} | {_ms(s['ms_mean'])} | {_ms(s['ms_max'])} | {s['lsw']:.1f} | "
                f"{s['welfare']:.2f} |")
        lines += ["", "Each pair plays every seed alone in a 2-node market. Win rate: share of all matches won "
                  "(ties ½); win rate (distinct): mean over opponents that do not play exactly as another "
                  "participant (catalog fallbacks), so duplicates count once, and reference points are not "
                  "counted; margin: own score minus the opponent's; welfare and log social welfare are means "
                  "over the agent's matches. The full pairwise matrix is in `summary.json` (`_matrix`)."]
    else:
        lines += ["| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | "
                  f"Mean rank (of {summary[agents[0]]['episodes'] and len(agents)}) | First places | Idle | "
                  "Floors | Exceptions | ms mean | ms max |",
                  "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for i, key in enumerate(agents, start=1):
            s = summary[key]
            lines.append(
                f"| {i} | {s['name']} (`{key}`) | {s['family']} | {_yes(s['realistic'])} | "
                f"{s['mean_score']:.3f} | {s['ci95']:.3f} | {s['score_rank']} | {s['mean_rank']:.2f} | "
                f"{s['first']} | {s['idle']:.1f} | {s['floors']:.2f} | {s['exceptions']} | "
                f"{_ms(s['ms_mean'])} | {_ms(s['ms_max'])} |")
        first = summary[agents[0]]
        lines += ["", f"Market-level, per episode: log social welfare **{first['lsw']:.1f}**, welfare "
                  f"(Σ of all {len(agents)} scores) **{first['welfare']:.2f}**."]
    workers = spec.get("workers")
    setting = f" ({workers} parallel workers)" if workers else ""
    lines += ["", f"Times are wall-clock milliseconds per decision measured inside the run{setting}, so they "
              "include contention; they are comparable across agents, not portable.", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
FAMILY_COLORS = dict(zip(FAMILIES, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#7c7b77"]))


def figure(summary: dict, mode: str, path: Path, title: str | None = None) -> bool:
    """Draw the report figure to ``path``; False when matplotlib is not installed."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        from matplotlib.colors import LinearSegmentedColormap
        from matplotlib.patches import Patch
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    surface, ink, ink2, grid = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
    plt.rcParams.update({"font.size": 9, "text.color": ink, "axes.labelcolor": ink2, "xtick.color": ink2,
                         "ytick.color": ink2, "axes.edgecolor": grid})
    agents = sorted((k for k in summary if not k.startswith("_")), key=lambda k: summary[k]["order"])
    labels = [f"{summary[k]['name']}" for k in agents]
    colors = [FAMILY_COLORS[summary[k]["family"]] for k in agents]
    hatches = ["" if summary[k]["realistic"] else "////" for k in agents]
    widths = [1.15, 0.8] if mode != "head-to-head" else [1.0, 1.25]
    height = 0.28 * len(agents) + (2.6 if mode == "head-to-head" else 1.6)
    fig, axes = plt.subplots(1, 2, figsize=(17, height), facecolor=surface,
                             gridspec_kw={"width_ratios": widths, "wspace": 0.08 if mode != "head-to-head" else 0.5})

    def bars(ax, values, xlabel, log=False, fmt="{:.2f}", shown=None):
        y = range(len(agents))
        ax.barh(y, values, height=0.68, color=colors, hatch=hatches, edgecolor=surface, linewidth=0.6)
        for i, v in enumerate(values):
            text = fmt(shown[i]) if callable(fmt) else fmt.format(v)
            ax.text(v * (1.04 if log else 1) + (0 if log else max(values) * 0.008), i, " " + text,
                    va="center", fontsize=7.5, color=ink2)
        ax.set_yticks(list(y), labels)
        ax.invert_yaxis()
        ax.set_facecolor(surface)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.tick_params(length=0)
        ax.xaxis.grid(True, color=grid, linewidth=0.7)
        ax.set_axisbelow(True)
        ax.set_xlabel(xlabel)
        if log:
            ax.set_xscale("log")
        else:
            ax.set_xlim(0, max(values) * 1.13)

    if mode == "head-to-head":
        bars(axes[0], [summary[k]["win_rate"] for k in agents], "head-to-head win rate", fmt="{:.3f}")
        matrix = summary["_matrix"]
        grid_values = [[matrix.get(a, {}).get(b, float("nan")) for b in agents] for a in agents]
        cmap = LinearSegmentedColormap.from_list("div", ["#e34948", "#f0efec", "#2a78d6"]).with_extremes(bad=surface)
        image = axes[1].imshow(grid_values, cmap=cmap, vmin=0, vmax=1)
        axes[1].set_xticks(range(len(agents)), [summary[k]["key"] for k in agents], rotation=90, fontsize=7)
        axes[1].set_yticks(range(len(agents)), [summary[k]["key"] for k in agents], fontsize=7)
        axes[1].tick_params(length=0)
        for spine in axes[1].spines.values():
            spine.set_visible(False)
        axes[1].set_title("row beats column (share of 100 seeds)", loc="left", fontsize=10)
        bar = fig.colorbar(image, ax=axes[1], fraction=0.035, pad=0.02)
        bar.outline.set_visible(False)
    else:
        bars(axes[0], [summary[k]["mean_score"] for k in agents], "mean score per 60-round run")
        bars(axes[1], [max(0.001, summary[k]["ms_mean"]) for k in agents], "ms per decision (log scale)",
             log=True, fmt=_ms, shown=[summary[k]["ms_mean"] for k in agents])
        axes[1].set_yticks([])
    handles = [Patch(facecolor=c, label=f) for f, c in FAMILY_COLORS.items()]
    handles.append(Patch(facecolor="white", edgecolor=ink2, hatch="////", label="not realistic (uses bot names)"))
    fig.subplots_adjust(top=1 - 0.45 / height, bottom=(1.6 if mode == "head-to-head" else 0.95) / height)
    fig.legend(handles=handles, loc="lower center", ncol=6, frameon=False, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))
    fig.suptitle(title or TITLES[mode], x=0.01, y=1 - 0.12 / height, ha="left", fontsize=12)
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor=surface)
    plt.close(fig)
    return True


def write_report(folder: Path, figure_path: Path | None = None, figure_link: str | None = None) -> Path:
    """Write ``summary.json``, ``report.md`` and (with matplotlib) ``figure.png`` for a results folder."""
    folder = Path(folder)
    spec = json.loads((folder / "spec.json").read_text(encoding="utf-8"))
    rows = load_rows(folder)
    mode = spec["mode"]
    summary = summarize(rows, mode)
    (folder / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    figure_path = figure_path or folder / "figure.png"
    drawn = figure(summary, mode, figure_path, _title(spec, mode))
    link = figure_link or (figure_path.name if drawn else None)
    report = folder / "report.md"
    report.write_text(markdown(summary, spec, mode, link if drawn else None), encoding="utf-8")
    return report
