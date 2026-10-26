# All together: every entry in one market

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Mean rank (of 26) | First places | Idle | Floors | Exceptions | ms mean | ms max |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Oracle (reference) (`clairvoyant`) | Reference | no | 0.689 | 0.022 | 1 | 1.71 | 51 | 9.8 | 95.33 | 0 | 11561 | 35957 |
| 2 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 0.671 | 0.016 | 2 | 1.77 | 39 | 8.7 | 102.60 | 0 | 0.007 | 0.279 |
| 3 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 0.645 | 0.017 | 3 | 3.36 | 7 | 11.0 | 98.08 | 0 | 0.003 | 0.045 |
| 4 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 0.642 | 0.018 | 4 | 3.66 | 3 | 12.9 | 94.20 | 0 | 0.022 | 0.455 |
| 5 | Battery taper (`taper`) | Traditional (rules) | yes | 0.550 | 0.005 | 5 | 4.86 | 0 | 1.1 | 117.78 | 0 | 1.3 | 17.9 |
| 6 | Floor reservation (`floors`) | Optimization (one round) | yes | 0.381 | 0.012 | 19 | 16.60 | 0 | 0.0 | 119.98 | 0 | 1.1 | 10.5 |
| 7 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 0.381 | 0.012 | 20 | 17.25 | 0 | 0.0 | 119.98 | 0 | 1.0 | 9.4 |
| 8 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 0.380 | 0.012 | 23 | 19.37 | 0 | 0.0 | 119.98 | 0 | 1.1 | 10.5 |
| 9 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 0.361 | 0.011 | 24 | 22.28 | 0 | 0.0 | 119.67 | 0 | 1.1 | 18.6 |
| 10 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 0.357 | 0.011 | 26 | 25.09 | 0 | 0.0 | 119.67 | 0 | 1.1 | 11.4 |
| 11 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 0.380 | 0.012 | 22 | 18.78 | 0 | 0.0 | 119.98 | 0 | 1.2 | 33.1 |
| 12 | + market residual (`residual`) | Planning (exact bot model) | no | 0.386 | 0.010 | 17 | 17.68 | 0 | 0.8 | 118.37 | 0 | 64.7 | 293 |
| 13 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 0.469 | 0.009 | 9 | 9.56 | 0 | 6.2 | 107.51 | 0 | 108 | 501 |
| 14 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 0.472 | 0.008 | 7 | 9.24 | 0 | 5.9 | 108.11 | 0 | 108 | 421 |
| 15 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 0.471 | 0.008 | 8 | 8.94 | 0 | 5.7 | 108.42 | 0 | 108 | 494 |
| 16 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 0.397 | 0.011 | 15 | 14.40 | 0 | 0.1 | 119.55 | 0 | 94.0 | 455 |
| 17 | + strategy modes (`modes`) | Planning (exact bot model) | no | 0.380 | 0.012 | 21 | 19.01 | 0 | 0.1 | 119.67 | 0 | 82.6 | 383 |
| 18 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 0.388 | 0.010 | 16 | 16.73 | 0 | 0.7 | 118.54 | 0 | 66.1 | 259 |
| 19 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 0.401 | 0.009 | 13 | 14.21 | 0 | 0.0 | 119.56 | 0 | 70.8 | 278 |
| 20 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 0.422 | 0.008 | 10 | 12.63 | 0 | 1.2 | 116.94 | 0 | 152 | 657 |
| 21 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 0.405 | 0.009 | 11 | 14.01 | 0 | 0.4 | 118.51 | 0 | 376 | 1602 |
| 22 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 0.403 | 0.009 | 12 | 14.26 | 0 | 0.3 | 118.74 | 0 | 375 | 1644 |
| 23 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 0.358 | 0.011 | 25 | 24.05 | 0 | 0.0 | 119.67 | 0 | 1.3 | 19.2 |
| 24 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 0.385 | 0.011 | 18 | 17.86 | 0 | 0.6 | 118.65 | 0 | 62.2 | 245 |
| 25 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 0.400 | 0.010 | 14 | 14.69 | 0 | 0.1 | 118.65 | 0 | 115 | 459 |
| 26 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 0.473 | 0.009 | 6 | 9.00 | 0 | 1.1 | 116.72 | 0 | 93.9 | 391 |

Market-level, per episode: log social welfare **-7377.8**, welfare (Σ of all 26 scores) **11.65**.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
