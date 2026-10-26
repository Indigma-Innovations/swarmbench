# All together: every entry in one market (capacity scale 6.25)

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Mean rank (of 26) | First places | Idle | Floors | Exceptions | ms mean | ms max |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Oracle (reference) (`clairvoyant`) | Reference | no | 14.968 | 0.099 | 1 | 2.84 | 49 | 7.5 | 0.00 | 0 | 4828 | 12405 |
| 2 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 11.721 | 0.130 | 23 | 22.64 | 0 | 24.3 | 2.64 | 0 | 0.006 | 0.109 |
| 3 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 10.503 | 0.303 | 25 | 24.06 | 0 | 26.6 | 7.23 | 0 | 0.008 | 14.0 |
| 4 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 9.893 | 0.211 | 26 | 25.55 | 0 | 27.4 | 11.36 | 0 | 0.016 | 2.1 |
| 5 | Battery taper (`taper`) | Traditional (rules) | yes | 14.334 | 0.165 | 6 | 6.90 | 0 | 4.5 | 0.78 | 0 | 1.0 | 25.8 |
| 6 | Floor reservation (`floors`) | Optimization (one round) | yes | 11.965 | 0.121 | 22 | 21.62 | 0 | 24.1 | 1.08 | 0 | 0.559 | 8.2 |
| 7 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 11.252 | 0.100 | 24 | 23.96 | 0 | 27.2 | 2.94 | 0 | 0.508 | 5.4 |
| 8 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 14.316 | 0.129 | 7 | 6.36 | 2 | 6.7 | 0.40 | 0 | 0.820 | 9.7 |
| 9 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 14.353 | 0.161 | 5 | 7.32 | 0 | 4.5 | 0.56 | 0 | 2.6 | 19.6 |
| 10 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 14.573 | 0.227 | 2 | 5.86 | 25 | 2.5 | 0.25 | 0 | 2.7 | 46.6 |
| 11 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 14.383 | 0.161 | 4 | 5.69 | 1 | 4.5 | 0.46 | 0 | 2.7 | 30.9 |
| 12 | + market residual (`residual`) | Planning (exact bot model) | no | 13.130 | 0.094 | 15 | 14.19 | 0 | 16.4 | 1.17 | 0 | 38.0 | 126 |
| 13 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 13.055 | 0.100 | 18 | 14.95 | 1 | 18.2 | 0.85 | 0 | 68.7 | 216 |
| 14 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 13.051 | 0.096 | 19 | 14.43 | 0 | 18.4 | 0.91 | 0 | 67.6 | 205 |
| 15 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 13.069 | 0.099 | 16 | 14.80 | 0 | 18.3 | 0.86 | 0 | 68.0 | 198 |
| 16 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 13.194 | 0.102 | 14 | 13.85 | 0 | 17.7 | 0.83 | 0 | 47.2 | 162 |
| 17 | + strategy modes (`modes`) | Planning (exact bot model) | no | 13.362 | 0.083 | 11 | 12.65 | 0 | 16.5 | 0.82 | 0 | 40.3 | 201 |
| 18 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 13.518 | 0.102 | 10 | 10.06 | 0 | 15.6 | 1.19 | 0 | 37.6 | 153 |
| 19 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 13.633 | 0.112 | 8 | 10.82 | 0 | 15.5 | 0.83 | 0 | 47.1 | 147 |
| 20 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 13.544 | 0.131 | 9 | 11.22 | 0 | 16.6 | 1.18 | 0 | 81.9 | 257 |
| 21 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 13.300 | 0.121 | 13 | 13.38 | 0 | 17.6 | 1.13 | 0 | 127 | 518 |
| 22 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 13.309 | 0.102 | 12 | 13.63 | 0 | 17.4 | 1.10 | 0 | 126 | 500 |
| 23 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 14.528 | 0.226 | 3 | 6.35 | 22 | 2.5 | 0.27 | 0 | 2.8 | 22.2 |
| 24 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 13.048 | 0.094 | 20 | 15.28 | 0 | 16.4 | 1.25 | 0 | 38.8 | 121 |
| 25 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 13.058 | 0.120 | 17 | 15.57 | 0 | 18.3 | 1.43 | 0 | 81.5 | 334 |
| 26 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 12.732 | 0.136 | 21 | 17.02 | 0 | 19.2 | 1.04 | 0 | 77.1 | 285 |

Market-level, per episode: log social welfare **-1456.5**, welfare (Σ of all 26 scores) **341.79**.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
