# The catalog

The roster has **36 entries**: the three supplied bots and 33 agents. They are
ordered from the simplest idea to the most complex, in five families:

| Family | Idea |
|---|---|
| **Traditional (rules)** | fixed splits and hand-written rules: the bots, the template, a battery taper |
| **Optimization (one round)** | infer rival demand from own results or prices, then solve the one-round problem (price-taker splits, guarded Kelly best responses, drain-aware pricing) |
| **Planning (exact bot model)** | stochastic multi-round rollouts that forecast the supplied bots from their published code, including battery-cutoff crossings, refinement and online physics |
| **Planning (identified market)** | the same planning, but with rival behaviour *identified* from public telemetry (battery drain reveals energy bids, prices reveal demand), with no names and no bot code |
| **Machine learning** | bandits, learned value functions (ridge, CatBoost), a LinUCB mode selector, Bayesian rival archetypes, a learned candidate shortlist |

## The realistic flag

An entry is **realistic** when it never relies on the supplied bots' team
names or source code, so it can face unnamed opponents as they are. The bots
themselves, the rule-based agents, the one-round optimizers (except
`bot-aware`), the UCB bandit and the four identified-market planners are
realistic. `bot-aware`, the planners with the exact bot model and the
learners built on them recognise the bots by name. Against
rivals they do not recognise, they fall back to simpler play. Several of them
then play *exactly* as another entry, which the table notes. This matters in
head-to-head, all-together and held-out runs.

## Roster

<!-- swarmbench:catalog -->

`swarmbench --list` prints the same roster. One further entry,
`cycle-aware-diagnostics`, bids exactly as `cycle-aware` and also logs its
predicted-versus-realized battery and market paths; it is not run by default.

## Reference points and held-out opponents

<!-- swarmbench:references -->

See [modes and metrics](modes.md#reference-points) for how the clairvoyant
oracle works.

## Groups

Wherever a list of agents is expected (`--agents`, `--opponents`, `--focus`,
`swarmbench.resolve`, `swarmbench.run_mode`), these group names expand:

| Group | Entries |
|---|---|
| `paper` (or `all`) | the 36 roster entries |
| `agents` | the 33 agents (roster without the bots) |
| `bots` | `naive-max`, `even-split`, `proportional` |
| `realistic` | the realistic roster entries |
| `distinct` | one entry per distinct behaviour among unnamed rivals (drops the entries that fall back to another) |

Groups and keys can be mixed, e.g. `--agents bots realistic random`;
duplicates are dropped.

## Where the strategies live

The bots are in `swarmbench.bots`, the agents in `swarmbench.strategies`, and
the catalog entries in `swarmbench.catalog`. The strategy modules are kept
exactly as they were measured, so that the stored results reproduce bit for
bit. Each is a plain function `f(budget, prices, capacities, profile, history)`
that reads only public information, wrapped as an [`Agent`](api/agent.md) by
the catalog.

The machine-learning entries that use trained models (the ridge and CatBoost
value functions, the LinUCB prior and the candidate shortlist) load them from
files shipped with the package; [trained models](models.md) describes them and
how to train them again.
