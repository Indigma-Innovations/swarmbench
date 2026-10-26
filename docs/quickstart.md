# Quickstart

## Look at the catalog

```bash
swarmbench --list
```

prints the 36 roster entries in *idea order* (simplest idea first), with
their family and the **realistic** flag, followed by aliases and reference
points. See [the catalog](catalog.md).

## Run a mode from the command line

```bash
# each entry against the three supplied bots, 20 seeds
swarmbench --mode solo --agents template kelly identified-robust cycle-aware --seeds 20

# every pair alone in a two-node market
swarmbench --mode head-to-head --agents kelly-drain identified-robust cycle-aware naive-max --seeds 10

# everyone in one market
swarmbench --mode all-together --agents bots realistic --seeds 5
```

Each run writes a folder (default `runs/swarmbench/<mode>`) with:

| File | Content |
|---|---|
| `spec.json` | what was run |
| `episodes.jsonl` | one row per participant and episode, appended as episodes finish |
| `summary.json` | the metrics per entry (and the pairwise matrix in head-to-head) |
| `report.md` | a Markdown table of everything |
| `figure.png` | a figure, when matplotlib is installed (`report` extra) |

Interrupted runs resume where they stopped: run the same command again.

## Run a mode from Python

```python
import swarmbench as sb
from swarmbench.report import summarize

rows = sb.run_mode("solo", ["template", "kelly", "cycle-aware"], range(70001, 70006), workers=4)
summary = summarize(rows, "solo")
for key in ("template", "kelly", "cycle-aware"):
    s = summary[key]
    print(f"{key:12} {s['mean_score']:6.2f} ±{s['ci95']:.2f}  {s['ms_mean']:.1f} ms/decision")
```

## Write a first agent

An agent is a class with one method. It receives an
[`Observation`](api/agent.md) and returns a bid per pool:

```python
import swarmbench as sb


class BatterySaver(sb.Agent):
    """Bid the preference weights, but stop buying energy before the battery runs flat."""

    def __init__(self, threshold: float = 0.4):
        self.threshold = threshold

    def bid(self, obs: sb.Observation) -> dict:
        w = dict(obs.weights)
        if obs.battery < self.threshold:
            w["energy"] *= obs.battery / self.threshold
        total = sum(w.values())
        return {k: obs.budget * w[k] / total for k in sb.RESOURCES}


sb.register_agent("battery-saver", BatterySaver, family="Traditional (rules)", realistic=True,
                  description="Weight bids with an energy cut below 40% battery.")
rows = sb.run_mode("solo", ["template", "battery-saver"], range(70001, 70011), workers=4)
```

Against the supplied bots, `battery-saver` beats `template` by a wide
margin: the battery is the game. To go further, see
[writing your own agent](custom-agents.md) and the notebooks in the
repository (`notebooks/01_run_modes.ipynb`, `notebooks/02_custom_agent.ipynb`).

## Check that your install reproduces the stored results

From a clone of the repository (the stored results live in `results/paper`):

```bash
swarmbench --reproduce --mode solo --seeds 3
```

Every score must be reported identical. See
[reproducing the results](reproducing.md).
