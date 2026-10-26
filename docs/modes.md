# Modes and metrics

An **episode** is one 60-round run of the arena with a given seed and a
given set of participants. A **mode** decides who meets whom; every mode
plays each of its markets on every seed (default: 100 seeds from 70001).

## The three modes

| Mode | Market | Nodes | What it answers |
|---|---|---:|---|
| `solo` | each entry alone against the three supplied bots | 4 | the original challenge |
| `head-to-head` | every unordered pair of entries, bots included | 2 | who beats whom, one on one |
| `all-together` | every listed entry in one market | n | how the strategies fare as a population |

**Solo.** The entry under test takes the seat a team took in the challenge,
and the three bots keep their real team names (`bot-naive-max`, ...). A bot
under test is renamed (`agent-<key>`), so it is one more participant rather
than a duplicate registration. Only the entry's row is reported; its
`bots_score` is the three bots' total.

**Head-to-head.** For \(N\) entries, the \(N(N-1)/2\) pairs each play every
seed in a two-node market. Nobody is named as a bot, so agents that recognise
the supplied bots by name meet only unnamed rivals.

**All-together.** Every listed entry joins one market, for example all 36
roster entries. With equal capacities, a crowded market is a different game:
no node can meet its floors.

Ten catalog entries play exactly as `kelly` when no rival is named as a bot,
and `template` plays as `naive-max`. The group `distinct` leaves them out, so
each behaviour enters the market once:

```bash
swarmbench --mode all-together --agents distinct --capacity-scale 6.25
```

## Variants

**Held-out opponents** (`--opponents`, solo only) replace the three bots
with opponents no catalog agent was developed against: `energy-hoarder`
(half of every wallet on energy), `contrarian` (weights leaning into the
pools that cleared cheapest) and `random`. They play under neutral names.

```bash
swarmbench --mode solo --agents paper --opponents energy-hoarder contrarian random
```

**Capacity scaling** (`--capacity-scale`) multiplies every pool's capacity.
`auto` sizes the pools for the market: \(n/4\) for \(n\) nodes, so a crowd of
36 gets 9 times the capacity, and each node faces the same scarcity as in
a four-node market.

```bash
swarmbench --mode all-together --agents paper --capacity-scale auto
```

**Focus pairs** (`--focus`, head-to-head only) keep only the pairs that
involve the given entries, for example to add reference points to an
existing tournament without replaying it:

```bash
swarmbench --mode head-to-head --agents paper random clairvoyant --focus random clairvoyant
```

## Reference points

Two entries bracket every result. They are runnable in every mode but are
not part of the roster:

- **Random split** (`random`) spends the whole wallet on a uniformly random
  split each round (seeded). It is the floor any agent should clear.
- **Oracle** (`oracle`, also accepted as `clairvoyant`) is not an admissible agent. The
  engine lets it bid last, after it has seen the other nodes' bids of the
  current round. Each round it evaluates a small candidate set: floor-aware
  exact best responses under several energy limits, bids that push its own or
  a rival's battery across the cutoff, and its base agent's bid
  (`kelly-drain`). It plays each candidate forward 10 rounds in a copy of the
  whole market, with true future draws and every other agent's real code and
  state, and commits the best. In markets of more than 8 nodes it looks one
  round ahead. It is an upper reference, not an upper bound.

## Metrics

Every participant of every episode produces one row:

| Field | Meaning |
|---|---|
| `score` | the arena's final score: the sum of the round utilities after floors |
| `rank`, `nodes` | place on the episode's leaderboard, market size |
| `beat_all` | strictly higher score than every other node |
| `participated`, `idle`, `missed` | rounds bid, rounds resting on a flat battery, rounds skipped while admissible |
| `floors` | service-floor violations |
| `exceptions` | rounds in which `bid()` raised (the engine then bids the preference weights) |
| `decisions`, `ms_mean`, `ms_max` | decisions taken and wall-clock milliseconds per decision |
| `others_score` | the other nodes' total score (`bots_score` in solo) |
| `welfare` | the sum of every node's final score in the market |
| `lsw_total` | the arena's log social welfare \(\sum_i \log u_i\), summed over the rounds |

`swarmbench.report.summarize` aggregates the rows per entry:

- **Mean score** with a normal 95% interval, **score rank**, **mean rank**
  and **first places**.
- **Paired gain** (solo): the mean per-seed relative gain over
  `cycle-aware`, the selected challenge submission, with its 95% interval,
  and wins and losses against it seed by seed.
- **Win rate** (head-to-head): the share of matches won, ties counting ½;
  **opponents beaten** (win rate above 50% against that opponent);
  **margin** (own score minus the opponent's); and the full pairwise matrix.
- **Nash averaging** (head-to-head, `swarmbench --metagame`, `analysis`
  extra). The win-rate matrix \(W\) defines a symmetric zero-sum meta-game
  \(A = W - \tfrac12\). Its maximum-entropy Nash equilibrium \(p^*\) is
  unique, and an entry's rating is \((A p^*)_i\): zero in the support,
  negative outside it. Unlike the mean win rate, it cannot be inflated by
  adding copies of an entry (Balduzzi et al., 2018). Reference points are
  rated against the roster's equilibrium.
- **Welfare** and **log social welfare**, averaged over the entry's episodes.
- **Milliseconds per decision**, mean and maximum. They are wall-clock
  times measured inside the run, contention included, so they compare
  agents within a run rather than across machines. A live graded round
  lasted 4 seconds.

## Determinism

An episode is a pure function of its seed, its participants and their seat
order: capacities, wallets and devices are drawn from seeded generators, and
every built-in agent seeds its own randomness. Results do not depend on the
number of workers or on the order in which episodes finish, and they
reproduce exactly (see [installation](installation.md#python-versions-and-exact-reproduction)).
