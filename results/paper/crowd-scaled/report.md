# All together: every entry in one market (capacity scale 6.25)

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Mean rank (of 25) | First places | Idle | Floors | Exceptions | ms mean | ms max |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 12.331 | 0.137 | 22 | 21.55 | 0 | 24.8 | 1.69 | 0 | 0.007 | 0.061 |
| 2 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 11.193 | 0.301 | 24 | 23.10 | 0 | 26.9 | 5.93 | 0 | 0.005 | 2.1 |
| 3 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 10.465 | 0.228 | 25 | 24.47 | 0 | 27.7 | 10.27 | 0 | 0.019 | 2.3 |
| 4 | Battery taper (`taper`) | Traditional (rules) | yes | 15.045 | 0.166 | 4 | 5.91 | 1 | 4.7 | 0.43 | 0 | 1.0 | 26.4 |
| 5 | Floor reservation (`floors`) | Optimization (one round) | yes | 12.496 | 0.133 | 21 | 20.80 | 0 | 24.6 | 0.71 | 0 | 0.647 | 9.6 |
| 6 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 11.850 | 0.124 | 23 | 22.86 | 0 | 27.4 | 2.39 | 0 | 0.612 | 21.0 |
| 7 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 14.981 | 0.131 | 6 | 5.35 | 10 | 7.0 | 0.35 | 0 | 0.957 | 13.0 |
| 8 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 15.038 | 0.164 | 5 | 6.74 | 0 | 4.7 | 0.41 | 0 | 3.1 | 54.4 |
| 9 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 15.285 | 0.230 | 1 | 5.27 | 32 | 2.6 | 0.15 | 0 | 3.1 | 19.3 |
| 10 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 15.057 | 0.166 | 3 | 5.05 | 5 | 4.7 | 0.33 | 0 | 3.1 | 20.0 |
| 11 | + market residual (`residual`) | Planning (exact bot model) | no | 13.915 | 0.099 | 14 | 12.61 | 3 | 16.4 | 0.80 | 0 | 43.0 | 172 |
| 12 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 14.143 | 0.100 | 11 | 11.00 | 2 | 17.1 | 0.56 | 0 | 78.9 | 243 |
| 13 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 14.146 | 0.096 | 10 | 10.47 | 6 | 17.3 | 0.50 | 0 | 75.4 | 236 |
| 14 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 14.050 | 0.090 | 13 | 11.59 | 4 | 17.7 | 0.56 | 0 | 75.4 | 244 |
| 15 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 13.704 | 0.108 | 17 | 15.05 | 0 | 18.3 | 0.59 | 0 | 61.1 | 205 |
| 16 | + strategy modes (`modes`) | Planning (exact bot model) | no | 13.539 | 0.110 | 19 | 16.38 | 0 | 18.1 | 0.57 | 0 | 59.1 | 267 |
| 17 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 14.277 | 0.116 | 7 | 9.13 | 6 | 15.7 | 0.76 | 0 | 42.9 | 297 |
| 18 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 14.262 | 0.087 | 8 | 10.43 | 2 | 16.1 | 0.57 | 0 | 52.4 | 227 |
| 19 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 14.189 | 0.107 | 9 | 10.49 | 1 | 16.8 | 0.71 | 0 | 92.0 | 279 |
| 20 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 14.063 | 0.110 | 12 | 11.93 | 0 | 17.3 | 0.78 | 0 | 147 | 743 |
| 21 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 13.907 | 0.124 | 15 | 13.38 | 1 | 17.4 | 0.77 | 0 | 146 | 609 |
| 22 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 15.249 | 0.231 | 2 | 5.77 | 26 | 2.5 | 0.17 | 0 | 3.3 | 31.3 |
| 23 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 13.881 | 0.097 | 16 | 13.09 | 0 | 16.4 | 0.85 | 0 | 44.3 | 318 |
| 24 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 13.609 | 0.121 | 18 | 15.16 | 0 | 19.2 | 1.24 | 0 | 90.8 | 367 |
| 25 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 13.127 | 0.168 | 20 | 17.42 | 1 | 20.7 | 0.82 | 0 | 85.7 | 427 |

Market-level, per episode: log social welfare **-1319.0**, welfare (Σ of all 25 scores) **343.80**.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
