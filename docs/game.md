# The game

The Swarm Arena of VelesHack 2026 Challenge 4 is a repeated auction among \(n\) edge nodes over
three shared resource pools, \(k \in \{C, E, S\}\): compute, energy and
security. SwarmBench uses the arena's `graded` scenario: 60 rounds, with the
constants below.

## One round

1. **The round opens.** Every pool gets a fresh capacity
   \(C_k = \bar C \cdot U(0.7, 1.3)\), with \(\bar C = 1\) (rounded to 4
   decimals), and every node gets the same wallet
   \(W = U(0.75, 1.25)\) (one common draw per round). The arena publishes
   last round's clearing prices \(\lambda_k = \sum_j b_j^k / C_k\) (floored
   at 0.01; 1.0 in the first round).
2. **Every admissible node bids** \(b_i = (b_i^C, b_i^E, b_i^S)\), with
   \(b_i^k \ge 0\) and \(\sum_k b_i^k \le W\). Unspent budget is lost: the
   wallet does not carry over.
3. **Allocation (Kelly proportional share).** Each node receives its share of
   the bids in each pool:

    \[
    x_i^k = C_k \, \frac{b_i^k}{\sum_j b_j^k}.
    \]

    The allocation is always feasible, and returns diminish, because a
    node's own bid sits in the denominator.

4. **Utility (CES, \(\rho = 1/2\)).** With preference weights \(w_i^k\)
   summing to 1,

    \[
    u_i = \Big(\sum_k w_i^k \, (x_i^k)^{\rho}\Big)^{1/\rho}
        = \Big(\sum_k w_i^k \sqrt{x_i^k}\Big)^{2}.
    \]

    The elasticity of substitution is \(\sigma = 1/(1-\rho) = 2\):
    resources substitute for one another, but a balanced bundle is worth more
    than a lopsided one.

5. **Service floors.** If the compute share \(x_i^C\) is below the node's
   floor \(q_{\min}\), the round's utility is halved; if the security share
   \(x_i^S\) is below \(s_{\min}\), it is halved again (a quarter of the
   utility when both floors are missed).
6. **Battery drain.** The energy a node wins comes out of its own battery
   \(B_i\):

    \[
    B_i \leftarrow \max\big(0,\; B_i - 0.30\,(1 + m_i)\,x_i^E - 0.004\big),
    \]

    where \(m_i\) is the node's mobility (mobile devices pay a surcharge) and
    0.004 is the idle drain of being awake.

7. **Score.** The node's score grows by the round's utility after floors.
   The final score is the sum over the 60 rounds (reported to 4 decimals).

## The battery cutoff

A node whose battery is at or below the **cutoff of 0.05** is *inadmissible*:
it cannot bid, scores nothing that round, and **recharges by 0.22** (capped
at 1). A node that wins energy greedily therefore flattens its battery and
loses whole rounds. The supplied bots do exactly that and rest for roughly a
third of the run. Planning these battery cycles, your own and your rivals',
is where most of the score is.

Admissibility also requires a compromise score below 0.60. In the live arena,
malformed, negative or over-budget bids raised it by 0.05 per warning. The
SwarmBench engine sanitises every bid first: non-finite or negative values
become 0, and an over-budget bid is scaled down to the wallet. Agents are
therefore never ejected.

## Devices and fairness

Each node has a device profile: preference weights \(w^C \sim U(0.25, 0.55)\),
\(w^E \sim U(0.15, 0.40)\), the rest to security (normalised to sum to 1),
a starting battery in \([0.55, 1]\), mobility in \([0, 0.45]\), and floors
\(q_{\min} \in [0.12, 0.22]\) and \(s_{\min} \in [0.08, 0.16]\). The arena
derives it deterministically from the seed and the team name.

A score only means something next to another score earned on the same
hardware, so the arena clones devices. In SwarmBench, **every participant
gets the same device**, minted from the seed and a fixed device label
(`swarmbench.engine.DEVICE_LABEL`, used by all the stored experiments). Within an episode, scores therefore
differ only through strategy and seat; across seeds, the device changes.

## What an agent observes

Everything an agent sees is public in the live arena (see
[`Observation`](api/agent.md)):

- the round payload: round index, wallet, this round's capacities, **last**
  round's clearing prices;
- its own profile: weights, floors, battery, mobility;
- the public swarm view: every other node's battery, mobility, weights,
  floors and activity, captured right after the round opens;
- its own settled results (allocation, utility, battery drawn, prices,
  capacities), delivered **one round late**, as in the live agent loop.

Agents do not see the other nodes' bids, the seed, or future draws. The
supplied bots never read results: they play their empty-history behaviour, as
the shipped bot runner does.

## Log social welfare

Every round, the arena reports the swarm's log social welfare
\(\mathrm{LSW}_t = \sum_i \log u_i\) over the participating nodes (utilities
floored at \(10^{-6}\)). SwarmBench sums it over the episode. Next to it,
*welfare* is the sum of every node's final score. Both measure whether a
strategy makes the swarm better off or only takes from its neighbours. In
this game the two often pull against winning.

## Constants of the graded scenario

| Constant | Value | Meaning |
|---|---|---|
| rounds | 60 | episode length |
| \(\rho\) | 0.5 | CES parameter |
| capacity | \(1 \cdot U(0.7, 1.3)\) | per pool, per round |
| wallet | \(1 \cdot U(0.75, 1.25)\) | common to all nodes, per round |
| battery drain | 0.30 | per unit of energy won, times \(1 + m\) |
| idle drain | 0.004 | per round of participation |
| cutoff | 0.05 | at or below: inadmissible |
| recharge | 0.22 | per idle round |
| floor penalty | \(\times 0.5\) | per missed floor |

The scenario files ship with the package (`swarmbench/arena/scenarios`).
`Market(scenario=...)` accepts `graded`, `practice` (40 rounds) or a path to
your own YAML file.
