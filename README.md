# SwarmBench

[![PyPI](https://img.shields.io/pypi/v/swarmbench?label=PyPI)](https://pypi.org/project/swarmbench/)
[![Python](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/github/actions/workflow/status/Indigma-Innovations/swarmbench/tests.yml?branch=main&label=tests)](https://github.com/Indigma-Innovations/swarmbench/actions/workflows/tests.yml)
[![Docs](https://img.shields.io/readthedocs/swarmbench?label=docs)](https://swarmbench.readthedocs.io)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](https://github.com/Indigma-Innovations/swarmbench/blob/main/LICENSE)

SwarmBench is a Python benchmark for strategic edge nodes in a repeated,
budgeted proportional-share (Kelly) auction, built on the open Swarm Arena of
Challenge 4 of the VelesHack 2026 hackathon. Each round, nodes split a common wallet over three pools (compute,
energy, security); they score a CES utility with service floors, and the
energy they win drains their own battery, so a node that bids greedily goes
flat and sits out whole rounds. SwarmBench runs the unchanged arena engine
in-process and deterministically. It ships a catalog of 36 agents, from
fixed rules to model-based planners and learned policies, each marked
**realistic** or not, plus three benchmark modes, reference points (a random
split and an oracle that sees its rivals' current bids), welfare metrics, and the stored results of
every experiment, which `swarmbench --reproduce` re-runs and checks score by
score (to the four decimals the arena reports).

## Install

```bash
pip install swarmbench            # or: uv add swarmbench
pip install "swarmbench[report]"  # + figures (matplotlib); extras: analysis, notebooks, docs, dev
```

Python 3.12+. The only runtime dependency is PyYAML.

## Quickstart

```python
import swarmbench as sb

class BatterySaver(sb.Agent):
    def bid(self, obs: sb.Observation) -> dict:
        w = dict(obs.weights)
        if obs.battery < 0.4:                       # stop buying energy before the battery runs flat
            w["energy"] *= obs.battery / 0.4
        return {k: obs.budget * w[k] / sum(w.values()) for k in sb.RESOURCES}

sb.register_agent("battery-saver", BatterySaver, family="Traditional (rules)", realistic=True)
rows = sb.run_mode("solo", ["battery-saver", "kelly", "cycle-aware"], range(70001, 70011), workers=4)
print({key: round(sum(r["score"] for r in rows if r["agent"] == key) / 10, 2) for key in ("battery-saver", "kelly", "cycle-aware")})
```

## Command line

```bash
swarmbench --list                                          # the catalog, in idea order
swarmbench --mode solo --agents cycle-aware identified-robust kelly --seeds 100
swarmbench --mode head-to-head --agents realistic --seeds 20
swarmbench --mode all-together --agents bots realistic --seeds 10
swarmbench --mode head-to-head --agents paper random clairvoyant --focus random clairvoyant
swarmbench --reproduce --mode solo --seeds 3               # from a clone: scores must be identical
swarmbench --report runs/swarmbench/solo                   # summary.json, report.md, figure.png
```

## Documentation

<https://swarmbench.readthedocs.io>: the game, the modes and metrics, the
catalog, the trained models and how to train them, writing your own agent,
the CLI, reproducing the results and the API reference. Two notebooks in [`notebooks/`](https://github.com/Indigma-Innovations/swarmbench/tree/main/notebooks) run a mode and build a
custom agent.

## Results

On 100 seeds, against the three supplied bots, the exact-model planners score
18.8 to 19.1 against 12.7 to 13.8 for the bots, and the realistic
`identified-robust` is equivalent to the selected `cycle-aware` planner (within
±1.5%) without knowing who the bots are. Against a single unknown rival, the
drain-pricing Kelly bidders lead: `ucb-energy` has the highest win rate over the
distinct entries (0.834, ahead of `kelly-drain` at 0.829), and the two are best
responses to each other in the two-node score game. In a crowd of the 25
distinct entries the fixed-weight bots win at nominal capacity and finish last
once capacity is sized to the crowd. Rankings do not transfer across protocols,
and winning and welfare pull apart. The stored experiments are in
[`results/paper`](https://github.com/Indigma-Innovations/swarmbench/tree/main/results/paper); `swarmbench --reproduce` re-runs them.

## Citation

If you use SwarmBench, please cite it (see also [`CITATION.cff`](https://github.com/Indigma-Innovations/swarmbench/blob/main/CITATION.cff)):

```bibtex
@misc{perifanis2026swarmbench,
  title        = {{SwarmBench}: A Benchmark for Strategic Edge Nodes in Battery-Coupled Proportional-Share Markets},
  author       = {Perifanis, Vasilis and Pavlidis, Nikolaos},
  year         = {2026},
  howpublished = {\url{https://github.com/Indigma-Innovations/swarmbench}},
  note         = {Manuscript submitted for publication}
}
```

## Acknowledgments

The arena game engine and the three baseline bots were prepared by the
[CoGNETs](https://cognets.eu/) consortium as Challenge 4 of VelesHack 2026
("Riding the Edge-to-Cloud Continuum", 6 to 8 October 2026) and are used
unchanged under the Apache-2.0 licence (see [NOTICE](https://github.com/Indigma-Innovations/swarmbench/blob/main/NOTICE)). SwarmBench is
written by Vasilis Perifanis and Nikolaos Pavlidis (Indigma Innovations and
Democritus University of Thrace).

## License

Apache-2.0. See [LICENSE](https://github.com/Indigma-Innovations/swarmbench/blob/main/LICENSE) and [NOTICE](https://github.com/Indigma-Innovations/swarmbench/blob/main/NOTICE).
