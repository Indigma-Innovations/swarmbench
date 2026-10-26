# Solo: each entry against the three supplied bots

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Δ vs cycle-aware (paired) | W/L vs cycle-aware | Beat all bots | Mean rank (of 4) | Idle | Floors | Exceptions | ms mean | ms max | Log social welfare | Bots' score | Welfare (Σ scores) |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Random split (reference) (`random`) | Reference | yes | 10.212 | 0.248 | 1 | — | — | 0/100 | 3.96 | 19.1 | 20.00 | 0 | 0.004 | 0.608 | -202.4 | 44.54 | 54.75 |

Log social welfare is the arena's Σ_i log u_i summed over rounds for the 4-node market; welfare is the sum of all four final scores. Δ is the mean per-seed relative gain with a normal 95% interval; W/L counts seeds with a strictly higher/lower score.

Times are wall-clock milliseconds per decision measured inside the run (2 parallel workers), so they include contention; they are comparable across agents, not portable.
