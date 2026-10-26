# All together: every entry in one market (capacity scale 6.25)

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Mean rank (of 26) | First places | Idle | Floors | Exceptions | ms mean | ms max |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Random split (reference) (`random`) | Reference | yes | 7.561 | 0.204 | 26 | 25.94 | 0 | 23.1 | 25.80 | 0 | 0.016 | 3.7 |
| 2 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 11.940 | 0.134 | 22 | 21.44 | 0 | 23.6 | 2.33 | 0 | 0.009 | 1.1 |
| 3 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 10.541 | 0.304 | 24 | 23.45 | 0 | 26.3 | 7.10 | 0 | 0.005 | 0.501 |
| 4 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 9.945 | 0.228 | 25 | 24.58 | 0 | 26.9 | 11.25 | 0 | 0.023 | 4.8 |
| 5 | Battery taper (`taper`) | Traditional (rules) | yes | 14.552 | 0.167 | 6 | 5.77 | 1 | 4.4 | 0.72 | 0 | 1.2 | 27.2 |
| 6 | Floor reservation (`floors`) | Optimization (one round) | yes | 12.166 | 0.121 | 21 | 20.53 | 0 | 23.4 | 1.05 | 0 | 0.753 | 8.7 |
| 7 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 11.336 | 0.110 | 23 | 23.11 | 0 | 26.5 | 2.73 | 0 | 0.698 | 9.9 |
| 8 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 14.581 | 0.145 | 4 | 4.66 | 17 | 6.0 | 0.43 | 0 | 1.1 | 8.7 |
| 9 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 14.562 | 0.163 | 5 | 6.23 | 1 | 4.4 | 0.55 | 0 | 3.5 | 51.0 |
| 10 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 14.749 | 0.224 | 1 | 5.07 | 35 | 2.5 | 0.29 | 0 | 3.6 | 18.8 |
| 11 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 14.595 | 0.165 | 3 | 4.50 | 8 | 4.4 | 0.47 | 0 | 3.6 | 20.2 |
| 12 | + market residual (`residual`) | Planning (exact bot model) | no | 13.301 | 0.103 | 13 | 13.30 | 3 | 16.2 | 1.05 | 0 | 50.8 | 156 |
| 13 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 13.212 | 0.099 | 16 | 13.37 | 2 | 17.7 | 0.80 | 0 | 93.6 | 220 |
| 14 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 13.147 | 0.097 | 19 | 14.25 | 2 | 18.1 | 0.80 | 0 | 91.9 | 216 |
| 15 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 13.154 | 0.099 | 18 | 13.91 | 1 | 18.2 | 0.79 | 0 | 92.2 | 234 |
| 16 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 13.216 | 0.073 | 15 | 13.98 | 0 | 17.7 | 0.84 | 0 | 64.0 | 195 |
| 17 | + strategy modes (`modes`) | Planning (exact bot model) | no | 13.491 | 0.084 | 11 | 11.56 | 0 | 16.2 | 0.81 | 0 | 55.2 | 175 |
| 18 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 13.630 | 0.107 | 9 | 9.75 | 5 | 15.4 | 1.07 | 0 | 50.9 | 152 |
| 19 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 13.680 | 0.115 | 7 | 10.81 | 1 | 15.0 | 0.85 | 0 | 63.2 | 175 |
| 20 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 13.643 | 0.123 | 8 | 11.39 | 0 | 15.4 | 1.13 | 0 | 116 | 314 |
| 21 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 13.560 | 0.133 | 10 | 11.77 | 1 | 15.9 | 1.11 | 0 | 191 | 701 |
| 22 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 13.485 | 0.119 | 12 | 12.45 | 0 | 16.0 | 1.00 | 0 | 188 | 762 |
| 23 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 14.704 | 0.217 | 2 | 5.33 | 17 | 2.5 | 0.26 | 0 | 3.8 | 38.2 |
| 24 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 13.282 | 0.103 | 14 | 13.35 | 1 | 16.1 | 1.03 | 0 | 52.3 | 154 |
| 25 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 13.209 | 0.120 | 17 | 14.25 | 3 | 17.6 | 1.39 | 0 | 110 | 393 |
| 26 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 12.909 | 0.141 | 20 | 16.25 | 2 | 18.5 | 0.96 | 0 | 102 | 333 |

Market-level, per episode: log social welfare **-1465.8**, welfare (Σ of all 26 scores) **338.15**.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
