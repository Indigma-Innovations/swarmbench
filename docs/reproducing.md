# Reproducing the results

The repository stores every experiment behind the SwarmBench results in
`results/paper/<experiment>/`:

| File | Content |
|---|---|
| `spec.json` | the exact run: mode, agents, seeds, scenario, rounds, options, Python version |
| `episodes.csv.gz` | one row per participant and episode; scores at full precision |
| `summary.json` | the per-entry metrics (`swarmbench.report.summarize`) |
| `report.md` | the Markdown report |
| `metagame.json` | head-to-head only: Nash averaging |

All experiments use the `graded` scenario, 60 rounds and seeds 70001 to
70100. They were produced on Python 3.13.

| Experiment | Mode | Market | Episodes |
|---|---|---|---:|
| `solo` | solo | each of the 36 entries against the three bots | 3,600 |
| `head-to-head` | head-to-head | every pair of the 36 entries | 63,000 |
| `all-together` | all-together | all 36 entries in one market | 100 |
| `solo-heldout` | solo | each entry against `energy-hoarder`, `contrarian`, `random` | 3,600 |
| `all-together-scaled` | all-together | all 36, capacities × 9 (`auto`) | 100 |
| `solo-random`, `solo-clairvoyant` | solo | the reference points against the bots | 100 each |
| `head-to-head-references` | head-to-head | `random` and `clairvoyant` against every entry | 7,300 |
| `all-together-random`, `all-together-clairvoyant` | all-together | the 36 plus one reference point | 100 each |
| `all-together-scaled-random`, `all-together-scaled-clairvoyant` | all-together | the same, capacities × 9 | 100 each |
| `solo-heldout-random`, `solo-heldout-oracle` | solo | the reference points against the held-out opponents | 100 each |
| `crowd` | all-together | the 25 distinct entries (`distinct`) in one market | 100 |
| `crowd-scaled` | all-together | the 25 distinct entries, capacities × 6.25 | 100 |
| `crowd-random`, `crowd-oracle` | all-together | the 25 distinct entries plus one reference point | 100 each |
| `crowd-scaled-random`, `crowd-scaled-oracle` | all-together | the same, capacities × 6.25 | 100 each |

## Checking them

From a clone of the repository:

```bash
swarmbench --reproduce --mode solo --seeds 3                 # 108 episodes, about 2 minutes on 2 cores
swarmbench --reproduce --mode head-to-head --seeds 1         # 630 episodes, about 7 minutes on 4 cores
swarmbench --reproduce --experiments all --seeds 1           # one seed of every experiment, about 40 minutes
swarmbench --reproduce                                       # solo, head-to-head and all-together in full
```

`--reproduce` reads each experiment's `spec.json`, re-runs it (or its first
`--seeds` seeds) into `runs/reproduce/<experiment>`, and compares every
participant's score with `episodes.csv.gz` for exact equality, at the four decimals the
arena reports. It prints, for
example,

```text
solo: 108/108 participant scores identical to results/paper/solo
```

and exits with status 1 if any score differs. The stored results live in the
repository, not in the installed package. Run the command from the
repository root, or point `--results` at the folder.

The full head-to-head experiment is the expensive one: 63,000 episodes, some
hours on four cores. The planners take tens of milliseconds per decision, and
the oracle a few hundred.

!!! note "Why Python 3.12"
    Python 3.12 changed the built-in `sum()` of floats to compensated
    (Neumaier) summation. The arena and the strategies sum floats everywhere,
    so exact reproduction depends on it, and 3.12 is the minimum
    supported version.

## Results at a glance

| Experiment | Finding |
|---|---|
| solo | The exact-model planners score 18.8 to 19.1, against 12.7 to 13.8 for the bots' policies. No extension significantly beats the selected `cycle-aware` planner (19.01), with or without a Holm correction; the realistic `identified-robust` is equivalent to it within ±1.5% (-0.41% ± 1.12) without knowing who the bots are. |
| head-to-head | Over the distinct entries (`win_rate_distinct`), `ucb-energy` has the highest win rate (0.834), ahead of `kelly-drain` (0.829) and `learned-shortlist` (0.810); `ucb-energy` beats every other entry in more than half the seeds, but only 51 of 100 against `dynamic-horizon`. The exact-model planners drop to 0.567. Raw win rates count the ten entries that fall back to `kelly` ten times. |
| all-together | With 36 nodes, nobody can meet the floors. The fixed-weight bots and the template take most of the energy and finish first (0.53 against 0.38 for the best agent). |
| all-together-scaled | With capacities × 9, the drain-aware Kelly agents win and the bots finish last. |
| crowd | Among the 25 distinct entries, the three bots take the first three places (0.709, 0.682, 0.675): most strategic entries bid little on energy, and the bots win half the energy pool. |
| crowd-scaled | With capacities × 6.25, `kelly-drain` (15.29) and `ucb-energy` (15.25) lead, all four Kelly variants finish in the top five, and the bots finish last. |
| solo-heldout | Against opponents nobody was developed against, `identified-robust` beats `cycle-aware` by +2.48% ± 0.73. |
| references | In solo, the random split scores 10.21 and the oracle 19.19 (+1.2% ± 1.5 over `cycle-aware`, not significant). In head-to-head, the oracle wins 0.866 of its matches against the distinct entries and beats every entry; random wins 0.090 and beats none. Nash averaging of the head-to-head matrix puts all weight on `ucb-energy`. |

Winning and welfare pull apart throughout: battery-cycling planners win
matches but lower the market's total welfare.

## Re-generating reports

Summaries and reports are derived from the episodes, so they can be rebuilt
at any time (with figures, if matplotlib is installed):

```bash
swarmbench --report results/paper/solo
swarmbench --metagame results/paper/head-to-head      # needs the analysis extra
```
