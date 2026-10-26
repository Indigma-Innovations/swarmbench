# All together: every entry in one market

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Mean rank (of 26) | First places | Idle | Floors | Exceptions | ms mean | ms max |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Random split (reference) (`random`) | Reference | yes | 0.560 | 0.016 | 4 | 6.39 | 0 | 10.1 | 99.50 | 0 | 0.015 | 4.1 |
| 2 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 0.672 | 0.015 | 1 | 1.32 | 71 | 8.8 | 102.48 | 0 | 0.008 | 4.1 |
| 3 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 0.645 | 0.016 | 3 | 2.48 | 16 | 11.1 | 97.76 | 0 | 0.004 | 0.209 |
| 4 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 0.646 | 0.019 | 2 | 2.62 | 13 | 13.0 | 94.08 | 0 | 0.028 | 16.1 |
| 5 | Battery taper (`taper`) | Traditional (rules) | yes | 0.551 | 0.005 | 5 | 4.65 | 0 | 1.1 | 117.78 | 0 | 1.2 | 14.1 |
| 6 | Floor reservation (`floors`) | Optimization (one round) | yes | 0.382 | 0.012 | 19 | 16.63 | 0 | 0.0 | 119.95 | 0 | 1.1 | 9.5 |
| 7 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 0.382 | 0.012 | 20 | 17.26 | 0 | 0.0 | 119.95 | 0 | 1.1 | 17.5 |
| 8 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 0.381 | 0.012 | 22 | 19.50 | 0 | 0.0 | 119.96 | 0 | 1.1 | 12.4 |
| 9 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 0.361 | 0.011 | 24 | 22.35 | 0 | 0.0 | 119.75 | 0 | 1.2 | 17.9 |
| 10 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 0.358 | 0.011 | 26 | 25.21 | 0 | 0.0 | 119.76 | 0 | 1.2 | 12.5 |
| 11 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 0.381 | 0.012 | 21 | 18.95 | 0 | 0.0 | 119.96 | 0 | 1.2 | 30.5 |
| 12 | + market residual (`residual`) | Planning (exact bot model) | no | 0.392 | 0.010 | 18 | 17.24 | 0 | 0.7 | 118.55 | 0 | 67.1 | 240 |
| 13 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 0.489 | 0.008 | 6 | 8.76 | 0 | 6.4 | 107.11 | 0 | 111 | 352 |
| 14 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 0.487 | 0.007 | 8 | 8.25 | 0 | 5.8 | 108.37 | 0 | 111 | 454 |
| 15 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 0.487 | 0.008 | 7 | 8.64 | 0 | 6.3 | 107.20 | 0 | 111 | 369 |
| 16 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 0.398 | 0.011 | 15 | 14.89 | 0 | 0.1 | 119.59 | 0 | 96.9 | 303 |
| 17 | + strategy modes (`modes`) | Planning (exact bot model) | no | 0.380 | 0.011 | 23 | 19.67 | 0 | 0.0 | 119.66 | 0 | 86.1 | 279 |
| 18 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 0.394 | 0.010 | 17 | 16.37 | 0 | 0.6 | 118.72 | 0 | 68.8 | 231 |
| 19 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 0.403 | 0.010 | 13 | 14.25 | 0 | 0.0 | 119.42 | 0 | 73.9 | 249 |
| 20 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 0.420 | 0.008 | 10 | 12.81 | 0 | 0.9 | 117.51 | 0 | 159 | 549 |
| 21 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 0.408 | 0.008 | 11 | 13.92 | 0 | 0.3 | 118.83 | 0 | 394 | 1413 |
| 22 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 0.407 | 0.008 | 12 | 13.91 | 0 | 0.3 | 118.80 | 0 | 394 | 1396 |
| 23 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 0.359 | 0.011 | 25 | 24.18 | 0 | 0.0 | 119.76 | 0 | 1.4 | 25.2 |
| 24 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 0.394 | 0.010 | 16 | 16.69 | 0 | 0.6 | 118.79 | 0 | 65.3 | 215 |
| 25 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 0.401 | 0.010 | 14 | 15.09 | 0 | 0.2 | 118.12 | 0 | 119 | 448 |
| 26 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 0.475 | 0.008 | 9 | 8.97 | 0 | 0.9 | 116.60 | 0 | 96.7 | 449 |

Market-level, per episode: log social welfare **-7372.5**, welfare (Σ of all 26 scores) **11.61**.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
