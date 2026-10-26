# All together: every entry in one market

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Mean rank (of 25) | First places | Idle | Floors | Exceptions | ms mean | ms max |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 0.709 | 0.018 | 1 | 1.26 | 80 | 9.7 | 100.66 | 0 | 0.012 | 8.1 |
| 2 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 0.682 | 0.019 | 2 | 2.41 | 16 | 12.1 | 95.86 | 0 | 0.010 | 8.8 |
| 3 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 0.675 | 0.021 | 3 | 2.74 | 4 | 13.9 | 92.14 | 0 | 0.038 | 8.6 |
| 4 | Battery taper (`taper`) | Traditional (rules) | yes | 0.573 | 0.005 | 4 | 4.07 | 0 | 1.4 | 117.28 | 0 | 1.8 | 19.4 |
| 5 | Floor reservation (`floors`) | Optimization (one round) | yes | 0.400 | 0.012 | 19 | 15.85 | 0 | 0.0 | 119.87 | 0 | 1.8 | 19.3 |
| 6 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 0.400 | 0.012 | 20 | 16.43 | 0 | 0.0 | 119.87 | 0 | 1.8 | 112 |
| 7 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 0.399 | 0.012 | 22 | 18.59 | 0 | 0.0 | 119.87 | 0 | 1.8 | 24.8 |
| 8 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 0.376 | 0.012 | 23 | 21.40 | 0 | 0.0 | 119.38 | 0 | 1.9 | 22.3 |
| 9 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 0.372 | 0.012 | 25 | 24.11 | 0 | 0.0 | 119.38 | 0 | 1.9 | 33.4 |
| 10 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 0.399 | 0.012 | 21 | 18.01 | 0 | 0.0 | 119.87 | 0 | 2.0 | 35.2 |
| 11 | + market residual (`residual`) | Planning (exact bot model) | no | 0.427 | 0.009 | 12 | 14.33 | 0 | 2.8 | 114.36 | 0 | 104 | 474 |
| 12 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 0.501 | 0.008 | 7 | 8.54 | 0 | 4.2 | 111.45 | 0 | 176 | 868 |
| 13 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 0.504 | 0.009 | 6 | 8.33 | 0 | 4.0 | 111.82 | 0 | 174 | 980 |
| 14 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 0.504 | 0.009 | 5 | 8.15 | 0 | 4.4 | 110.92 | 0 | 174 | 1159 |
| 15 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 0.409 | 0.011 | 17 | 16.42 | 0 | 0.2 | 119.30 | 0 | 153 | 655 |
| 16 | + strategy modes (`modes`) | Planning (exact bot model) | no | 0.402 | 0.012 | 18 | 17.82 | 0 | 0.1 | 119.42 | 0 | 133 | 617 |
| 17 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 0.427 | 0.009 | 13 | 14.07 | 0 | 2.8 | 114.25 | 0 | 106 | 511 |
| 18 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 0.421 | 0.010 | 15 | 13.88 | 0 | 0.0 | 119.27 | 0 | 116 | 605 |
| 19 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 0.452 | 0.009 | 9 | 12.44 | 0 | 2.8 | 113.51 | 0 | 240 | 1109 |
| 20 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 0.436 | 0.009 | 10 | 12.53 | 0 | 1.5 | 116.25 | 0 | 632 | 3271 |
| 21 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 0.435 | 0.009 | 11 | 12.69 | 0 | 1.2 | 116.75 | 0 | 630 | 3282 |
| 22 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 0.373 | 0.012 | 24 | 23.06 | 0 | 0.0 | 119.38 | 0 | 2.2 | 29.7 |
| 23 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 0.426 | 0.009 | 14 | 14.45 | 0 | 2.5 | 114.63 | 0 | 101 | 645 |
| 24 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 0.415 | 0.010 | 16 | 15.43 | 0 | 0.3 | 117.74 | 0 | 185 | 969 |
| 25 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 0.497 | 0.009 | 8 | 7.99 | 0 | 1.2 | 116.04 | 0 | 149 | 766 |

Market-level, per episode: log social welfare **-7037.8**, welfare (Σ of all 25 scores) **11.61**.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
