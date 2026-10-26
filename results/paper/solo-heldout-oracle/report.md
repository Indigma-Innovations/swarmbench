# Solo: each entry against held-out opponents (energy-hoarder, contrarian, random)

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Δ vs cycle-aware (paired) | W/L vs cycle-aware | Beat all bots | Mean rank (of 4) | Idle | Floors | Exceptions | ms mean | ms max | Log social welfare | Bots' score | Welfare (Σ scores) |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Oracle (reference) (`clairvoyant`) | Reference | no | 19.621 | 0.278 | 1 | — | — | 100/100 | 1.00 | 9.1 | 0.09 | 0 | 374 | 1139 | -224.3 | 31.96 | 51.58 |

Log social welfare is the arena's Σ_i log u_i summed over rounds for the 4-node market; welfare is the sum of all four final scores. Δ is the mean per-seed relative gain with a normal 95% interval; W/L counts seeds with a strictly higher/lower score.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
