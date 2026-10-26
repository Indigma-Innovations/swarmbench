# All together: every entry in one market

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Mean rank (of 37) | First places | Idle | Floors | Exceptions | ms mean | ms max |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Oracle (reference) (`clairvoyant`) | Reference | no | 0.530 | 0.019 | 1 | 1.92 | 57 | 10.6 | 96.95 | 0 | 9661 | 19899 |
| 2 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 0.511 | 0.014 | 2 | 3.56 | 0 | 7.5 | 104.96 | 0 | 0.006 | 1.5 |
| 3 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 0.507 | 0.015 | 4 | 3.33 | 14 | 9.8 | 100.32 | 0 | 0.003 | 0.108 |
| 4 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 0.507 | 0.018 | 5 | 3.70 | 4 | 12.3 | 95.48 | 0 | 0.020 | 4.1 |
| 5 | Template: weight bids (`template`) | Traditional (rules) | yes | 0.511 | 0.014 | 3 | 2.56 | 25 | 7.5 | 104.96 | 0 | 0.743 | 11.7 |
| 6 | Battery taper (`taper`) | Traditional (rules) | yes | 0.401 | 0.003 | 6 | 6.13 | 0 | 1.0 | 118.02 | 0 | 0.682 | 6.1 |
| 7 | Floor reservation (`floors`) | Optimization (one round) | yes | 0.250 | 0.007 | 21 | 20.92 | 0 | 0.0 | 119.99 | 0 | 0.677 | 7.7 |
| 8 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 0.250 | 0.007 | 22 | 22.45 | 0 | 0.0 | 119.99 | 0 | 0.668 | 7.4 |
| 9 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 0.249 | 0.007 | 24 | 27.57 | 0 | 0.0 | 119.99 | 0 | 0.685 | 13.2 |
| 10 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 0.241 | 0.008 | 28 | 26.78 | 0 | 0.0 | 120.00 | 0 | 0.739 | 12.8 |
| 11 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 0.239 | 0.008 | 37 | 36.92 | 0 | 0.0 | 120.00 | 0 | 0.736 | 8.2 |
| 12 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 0.249 | 0.008 | 23 | 25.04 | 0 | 0.0 | 119.99 | 0 | 0.753 | 8.5 |
| 13 | Best response to bot forecasts (`bot-aware`) | Optimization (one round) | no | 0.241 | 0.008 | 25 | 23.73 | 0 | 0.0 | 120.00 | 0 | 0.789 | 8.9 |
| 14 | Lookahead planner (MPC) (`lookahead`) | Planning (exact bot model) | no | 0.241 | 0.008 | 29 | 28.34 | 0 | 0.0 | 120.00 | 0 | 0.774 | 9.2 |
| 15 | Lookahead + cutoff crossings (`lookahead-cutoff`) | Planning (exact bot model) | no | 0.241 | 0.008 | 30 | 29.34 | 0 | 0.0 | 120.00 | 0 | 0.771 | 8.9 |
| 16 | Lookahead + refinement (`lookahead-refine`) | Planning (exact bot model) | no | 0.241 | 0.008 | 31 | 30.34 | 0 | 0.0 | 120.00 | 0 | 0.768 | 15.2 |
| 17 | Cycle-Aware planner (selected) (`cycle-aware`) | Planning (exact bot model) | no | 0.241 | 0.008 | 27 | 25.73 | 0 | 0.0 | 120.00 | 0 | 0.763 | 8.9 |
| 18 | + online battery physics (`physics`) | Planning (exact bot model) | no | 0.241 | 0.008 | 32 | 31.45 | 0 | 0.0 | 120.00 | 0 | 0.919 | 7.2 |
| 19 | + market residual (`residual`) | Planning (exact bot model) | no | 0.291 | 0.008 | 16 | 14.74 | 0 | 1.2 | 117.57 | 0 | 47.9 | 239 |
| 20 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 0.325 | 0.005 | 9 | 10.34 | 0 | 2.7 | 114.66 | 0 | 84.2 | 880 |
| 21 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 0.325 | 0.005 | 8 | 10.41 | 0 | 2.6 | 114.71 | 0 | 83.7 | 221 |
| 22 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 0.318 | 0.007 | 10 | 10.82 | 0 | 2.0 | 115.96 | 0 | 84.5 | 218 |
| 23 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 0.287 | 0.009 | 18 | 14.89 | 0 | 0.4 | 119.12 | 0 | 72.7 | 343 |
| 24 | + strategy modes (`modes`) | Planning (exact bot model) | no | 0.267 | 0.009 | 20 | 19.93 | 0 | 0.0 | 119.87 | 0 | 62.3 | 205 |
| 25 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 0.291 | 0.009 | 15 | 14.44 | 0 | 1.4 | 117.06 | 0 | 48.5 | 124 |
| 26 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 0.283 | 0.007 | 19 | 16.27 | 0 | 0.0 | 119.78 | 0 | 58.2 | 921 |
| 27 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 0.311 | 0.006 | 11 | 12.94 | 0 | 1.2 | 117.33 | 0 | 134 | 342 |
| 28 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 0.295 | 0.006 | 12 | 14.60 | 0 | 0.6 | 118.63 | 0 | 333 | 1313 |
| 29 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 0.293 | 0.006 | 13 | 14.84 | 0 | 0.5 | 118.75 | 0 | 332 | 796 |
| 30 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 0.240 | 0.008 | 36 | 35.92 | 0 | 0.0 | 120.00 | 0 | 0.952 | 9.5 |
| 31 | Learned value (ridge), greedy (`ridge-value`) | Machine learning | no | 0.241 | 0.008 | 35 | 34.52 | 0 | 0.0 | 120.00 | 0 | 0.876 | 8.7 |
| 32 | Planner + ridge terminal (4 rounds) (`ridge-terminal-4`) | Machine learning | no | 0.241 | 0.008 | 33 | 32.52 | 0 | 0.0 | 120.00 | 0 | 0.847 | 19.5 |
| 33 | Planner + ridge terminal (6 rounds) (`ridge-terminal-6`) | Machine learning | no | 0.241 | 0.008 | 34 | 33.52 | 0 | 0.0 | 120.00 | 0 | 0.818 | 17.3 |
| 34 | Planner + CatBoost terminal (`catboost-terminal`) | Machine learning | no | 0.241 | 0.008 | 26 | 24.73 | 0 | 0.0 | 120.00 | 0 | 0.822 | 13.1 |
| 35 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 0.288 | 0.008 | 17 | 15.99 | 0 | 1.2 | 117.50 | 0 | 47.0 | 247 |
| 36 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 0.291 | 0.007 | 14 | 14.53 | 0 | 0.2 | 118.92 | 0 | 101 | 356 |
| 37 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 0.373 | 0.006 | 7 | 7.24 | 0 | 1.7 | 116.05 | 0 | 82.3 | 388 |

Market-level, per episode: log social welfare **-11523.5**, welfare (Σ of all 37 scores) **11.34**.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
