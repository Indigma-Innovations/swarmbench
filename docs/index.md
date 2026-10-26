# SwarmBench

SwarmBench is a Python benchmark for strategic edge nodes in a repeated,
budgeted proportional-share auction, built on the open Swarm Arena of
Challenge 4 of the VelesHack 2026 hackathon.

Every round, each node splits a common wallet over three shared pools:
compute, energy and security. It receives its proportional share of each pool
and scores a CES utility over the bundle. Missing a service floor halves the
round's utility, and the energy a node wins drains its own battery. A node
whose battery falls to the cutoff sits out whole rounds until it recharges. So
the one-round optimum is easy to compute and nearly worthless. The game is
won over time, by managing the battery and reading the other nodes.

SwarmBench runs the unchanged arena engine in-process and deterministically,
and adds:

- **an agent API**: subclass [`Agent`](api/agent.md), implement
  `bid(obs) -> {"compute": .., "energy": .., "security": ..}`, register it;
- **a catalog of 36 entries**: the three supplied bots and 33 agents, in five
  families from fixed rules to planners and learned policies, each flagged
  **realistic** when it never relies on the supplied bots' names or code
  ([the catalog](catalog.md));
- **three modes**: solo (against the supplied bots), head-to-head (every pair)
  and all-together (one crowded market), with held-out opponents, capacity
  scaling and two reference points, a random split and an oracle that sees its rivals' current bids
  ([modes and metrics](modes.md));
- **metrics**: score, rank, win rate, Nash averaging, welfare, log social
  welfare and milliseconds per decision, with Markdown reports and figures;
- **stored results** of every experiment (100 seeds each), which
  `swarmbench --reproduce` re-runs and checks score by score
  ([reproducing](reproducing.md)).

```bash
pip install swarmbench
swarmbench --list
swarmbench --mode solo --agents cycle-aware identified-robust kelly --seeds 20
```

## Origin

The arena was built by the [CoGNETs](https://cognets.eu/) consortium as
**Challenge 4 of VelesHack 2026** ("Riding the Edge-to-Cloud Continuum",
6 to 8 October 2026): *Dynamic Node Registration and Auction-Based Resource
Allocation in an Edge Computing Environment*. It is a deliberately small
version of a multi-stage pipeline in which nodes are admitted to a swarm and
then bid for resources: congestion prices, Kelly proportional allocation, CES
utilities and admissibility floors. Teams wrote an agent that joined the swarm over
HTTP and competed against three supplied baseline bots.

SwarmBench grew out of one team's work on that challenge. It turns the
strategies developed during and after the event into a reproducible research
benchmark: the same engine and bots, without the network layer, so an episode
is a pure function of its seed and its participants.

CoGNETs has received funding from the European Union's Horizon Europe research
and innovation programme under grant agreement No 101135930.

## Where to go next

| | |
|---|---|
| [Installation](installation.md) | pip, uv, extras, from source |
| [Quickstart](quickstart.md) | run a mode and write a first agent in five minutes |
| [The game](game.md) | the rules, with every constant |
| [Modes and metrics](modes.md) | what each mode measures and how |
| [The catalog](catalog.md) | all 36 entries and the reference points |
| [Trained models](models.md) | the shipped models, how they were trained and how to train them again |
| [Writing your own agent](custom-agents.md) | the `Agent` and `Observation` API |
| [Command line](cli.md) | every option of `swarmbench` |
| [Reproducing the results](reproducing.md) | the stored experiments and how to check them |
