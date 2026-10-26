# Writing your own agent

## The interface

An agent subclasses [`swarmbench.Agent`](api/agent.md#swarmbench.agent.Agent)
and implements one method:

```python
import swarmbench as sb


class MyAgent(sb.Agent):
    def reset(self, seed: int) -> None:          # optional: called once before an episode
        self.rounds_seen = 0

    def bid(self, obs: sb.Observation) -> dict:
        self.rounds_seen += 1
        return {k: obs.budget * obs.weights[k] for k in sb.RESOURCES}
```

`bid` returns `{"compute": b_C, "energy": b_E, "security": b_S}`:
non-negative amounts summing to at most `obs.budget`. The engine applies the
live agent's last line of defence. Missing, non-numeric, negative or
non-finite values become 0, and an over-budget bid is scaled down to the
wallet. If `bid` raises, the round is not lost: the engine bids the
preference weights and counts an exception in the results.

One instance plays one episode (the catalog calls the factory for every
episode), so keep per-episode state on `self`.

## The observation

| Field | Meaning |
|---|---|
| `round`, `total_rounds` | the current round (1-based) and the episode length |
| `budget` | this round's wallet \(W\), common to all nodes |
| `prices` | **last** round's clearing prices (total bid / capacity) per pool |
| `capacities` | this round's pool sizes \(C_k\) |
| `profile` | own profile: `features` (`battery`, `mobility`, ...), `weights`, `q_min`, `s_min` |
| `rivals` | the public view of every other node: `node_id`, `team`, `features`, `weights`, `q_min`, `s_min`, `active`, `is_baseline` |
| `history` | own settled results, one round late: `round`, `allocation`, `bid`, `spend`, `prices`, `capacities`, `utility`, `floor_violations`, `battery_drawn`, `battery`, ... |

Shortcuts: `obs.battery`, `obs.mobility`, `obs.weights`, `obs.floors`
(`(q_min, s_min)`).

The rules of [the game](game.md) in one line: you get
\(x_k = C_k b_k / \sum_j b_j^k\), score \((\sum_k w_k \sqrt{x_k})^2\), halved per
missed floor, and the energy you win drains your battery by
\(0.30 (1+m) x_E + 0.004\). At or below 0.05 you sit out a round and
recharge 0.22.

## Registering

[`register_agent`](api/catalog.md#swarmbench.catalog.register_agent) adds the
agent to the catalog, so modes, reports and the command line can use it:

```python
sb.register_agent(
    "my-agent", MyAgent,                  # key and factory (called once per episode)
    name="My agent",
    family="Optimization (one round)",    # one of swarmbench.FAMILIES
    realistic=True,                       # never uses the bots' names or code
    description="Weight bids.",
)
rows = sb.run_mode("solo", ["my-agent", "cycle-aware"], range(70001, 70021), workers=4)
```

The factory can be any callable that returns a fresh agent, for example a
lambda that sets parameters: `lambda: MyAgent(threshold=0.6)`.

Use the **realistic** flag honestly. An agent that reads `team` names in
`obs.rivals` to recognise `bot-naive-max` and friends, or that embeds the
bots' formulas, is not realistic: it will meet unnamed opponents in
head-to-head and all-together runs.

## Wrapping a plain function

Functions with the signature of the built-in strategies,
`f(budget, prices, capacities, profile, history) -> bid`, plug in through
[`FunctionAgent`](api/agent.md#swarmbench.agent.FunctionAgent). The public
rivals are in `profile["_market"]["nodes"]`:

```python
def compute_heavy(budget, prices, capacities, profile, history):
    return {"compute": 0.6 * budget, "energy": 0.2 * budget, "security": 0.2 * budget}

sb.register_agent("compute-heavy", lambda: sb.FunctionAgent(compute_heavy),
                  family="Traditional (rules)", description="60/20/20 split.")
```

## One episode by hand

[`Market`](api/engine.md#swarmbench.engine.Market) and
[`seat`](api/engine.md#swarmbench.engine.seat) give full control over who
sits in a market:

```python
market = sb.Market()                                  # graded scenario, 60 rounds
seats = [sb.seat(sb.get_spec(b)) for b in ("naive-max", "even-split", "proportional")]
seats.append(sb.seat(sb.get_spec("my-agent"), team="agent-my-agent", baseline=False))
episode = market.play(70001, seats)
for row in episode.rows:
    print(row["team"], row["score"], row["rank"], row["idle"])
print(episode.lsw_total, episode.welfare)
```

`Market.play` accepts an `observer(state, seats)` callback, called after
every settled round, for traces.

## From the command line

The command line reads the catalog of a fresh process. Put the agent in an
importable module that registers it, and pass the module with `--import`:

```python
# my_agents.py
import swarmbench as sb
from my_package import MyAgent

sb.register_agent("my-agent", MyAgent, family="Optimization (one round)", realistic=True)
```

```bash
swarmbench --import my_agents --mode solo --agents my-agent cycle-aware --seeds 20
swarmbench --import my_agents --mode head-to-head --agents my-agent realistic --seeds 10
```

## Running in parallel

`run_mode(..., workers=n)` and `--workers` run episodes in worker processes.
On Linux and macOS they are forked, so they inherit every agent registered
in your session, notebooks included. Where only spawning is available
(Windows), the workers start from a fresh interpreter. Agents registered in
modules passed to `--import` (or `swarmbench.catalog.import_agents`) are
re-imported there; agents defined interactively need `workers=1`.

## Guidelines for a fair agent

- Use only the `Observation`. Reaching into the engine, the arena or the seed
  is not a strategy.
- Keep per-episode state on `self`, not in module globals.
- Seed any randomness from `reset(seed)`, so episodes stay reproducible.
- Stay well within the live arena's round window (4 seconds in the graded
  scenario). The built-in agents average from well under a millisecond to a
  few hundred milliseconds per decision.
