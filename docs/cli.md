# Command line

The `swarmbench` command (also `python -m swarmbench`) lists the catalog, runs
modes, reproduces the stored results and writes reports.

## Actions

| Command | Does |
|---|---|
| `swarmbench --list` | print the catalog in idea order |
| `swarmbench --mode MODE [options]` | run a mode and write its report |
| `swarmbench --reproduce [options]` | re-run stored experiments and compare every score |
| `swarmbench --report FOLDER` | (re)write `summary.json`, `report.md` and `figure.png` for a results folder |
| `swarmbench --publish FOLDER` | store a finished run in compact form under `--results` |
| `swarmbench --metagame FOLDER` | Nash averaging of a head-to-head folder, written to `metagame.json` (`analysis` extra) |
| `swarmbench --version` | print the version |

## Running a mode

| Option | Default | Meaning |
|---|---|---|
| `--mode` | | `solo`, `head-to-head` or `all-together` |
| `--agents KEY...` | `paper` | catalog keys and [groups](catalog.md#groups) |
| `--seeds N` | 100 | number of seeds |
| `--seed-start S` | 70001 | first seed; episodes use seeds S to S+N-1 |
| `--opponents KEY...` | the three bots | solo: replace the supplied bots (held-out opponents) |
| `--focus KEY...` | | head-to-head: only the pairs involving these entries |
| `--capacity-scale X` | 1.0 | multiply every pool's capacity; `auto` = n/4 for n nodes |
| `--rounds N` | 60 | shorten episodes (testing only) |
| `--workers N` | all CPUs | parallel worker processes |
| `--output DIR` | `runs/swarmbench/<mode>` | results folder; an existing run there is resumed |
| `--name NAME` | | experiment name, used by `--publish` |
| `--import MODULE` | | import a module that registers agents (repeatable) |

```bash
swarmbench --mode solo --agents cycle-aware identified-robust kelly --seeds 100
swarmbench --mode head-to-head --agents realistic --seeds 20 --workers 8
swarmbench --mode all-together --agents bots realistic --seeds 10
swarmbench --mode all-together --agents paper --capacity-scale auto
swarmbench --mode solo --agents paper --opponents energy-hoarder contrarian random
swarmbench --mode head-to-head --agents paper random clairvoyant --focus random clairvoyant
swarmbench --import my_agents --mode solo --agents my-agent cycle-aware
```

A run folder holds `spec.json`, `episodes.jsonl` (one JSON row per
participant and episode, appended as episodes finish), `summary.json`,
`report.md` and, with matplotlib, `figure.png`. Running the same command
again resumes an interrupted run: episodes already in `episodes.jsonl` are
skipped.

## Reproducing stored results

| Option | Default | Meaning |
|---|---|---|
| `--reproduce` | | re-run stored experiments |
| `--experiments NAME...` | `solo head-to-head all-together` | stored experiment folders, or `all` |
| `--mode MODE` | | shorthand for `--experiments MODE` |
| `--seeds N` | all stored seeds | only the first N seeds |
| `--results DIR` | `results/paper` | folder of stored results, relative to the current directory |
| `--output DIR` | `runs/reproduce` | where the fresh runs go (replaced on every call) |
| `--workers N` | all CPUs | parallel worker processes |

```bash
swarmbench --reproduce --mode solo --seeds 3
swarmbench --reproduce --experiments solo-heldout all-together-scaled --seeds 2
swarmbench --reproduce --experiments all --results /path/to/swarmbench/results/paper
```

For each experiment it prints `<name>: <same>/<total> participant scores
identical to <folder>` and exits with status 1 if any score differs. See
[reproducing the results](reproducing.md).

## Storing a run

`--publish FOLDER` checks that the run is complete, then writes the compact
form (`spec.json`, `episodes.csv.gz` with full-precision scores,
`summary.json`, `report.md`) to `<results>/<name>`. The name is `--name` if
the run was given one, otherwise the mode, with `-heldout` or `-scaled`
appended for held-out opponents or scaled capacities.

```bash
swarmbench --mode solo --agents paper --seeds 100 --output runs/solo
swarmbench --publish runs/solo --results results/paper
```

## Full help

<!-- swarmbench:cli-help -->
