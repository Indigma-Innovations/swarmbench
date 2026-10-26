# All together: every entry in one market (capacity scale auto)

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Mean rank (of 36) | First places | Idle | Floors | Exceptions | ms mean | ms max |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 12.445 | 0.179 | 32 | 28.73 | 0 | 26.9 | 2.02 | 0 | 0.006 | 0.162 |
| 2 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 11.758 | 0.345 | 35 | 28.84 | 1 | 28.0 | 7.55 | 0 | 0.004 | 0.033 |
| 3 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 9.970 | 0.346 | 36 | 34.99 | 0 | 28.4 | 18.97 | 0 | 0.014 | 0.577 |
| 4 | Template: weight bids (`template`) | Traditional (rules) | yes | 12.445 | 0.179 | 33 | 27.73 | 1 | 26.9 | 2.02 | 0 | 0.418 | 8.1 |
| 5 | Battery taper (`taper`) | Traditional (rules) | yes | 13.727 | 0.179 | 7 | 12.04 | 0 | 5.7 | 0.56 | 0 | 0.646 | 14.5 |
| 6 | Floor reservation (`floors`) | Optimization (one round) | yes | 12.698 | 0.173 | 31 | 26.01 | 0 | 26.7 | 0.82 | 0 | 0.389 | 5.5 |
| 7 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 12.423 | 0.174 | 34 | 27.84 | 1 | 28.2 | 5.36 | 0 | 0.388 | 5.8 |
| 8 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 14.237 | 0.124 | 3 | 7.86 | 4 | 11.1 | 0.34 | 0 | 0.591 | 14.9 |
| 9 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 13.708 | 0.175 | 11 | 15.22 | 0 | 5.7 | 0.44 | 0 | 1.9 | 23.7 |
| 10 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 14.827 | 0.285 | 1 | 6.54 | 36 | 3.1 | 0.31 | 0 | 1.9 | 16.1 |
| 11 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 13.770 | 0.179 | 6 | 10.71 | 0 | 5.7 | 0.35 | 0 | 1.9 | 17.6 |
| 12 | Best response to bot forecasts (`bot-aware`) | Optimization (one round) | no | 13.708 | 0.175 | 8 | 12.22 | 0 | 5.7 | 0.44 | 0 | 1.9 | 19.2 |
| 13 | Lookahead planner (MPC) (`lookahead`) | Planning (exact bot model) | no | 13.708 | 0.175 | 12 | 16.22 | 0 | 5.7 | 0.44 | 0 | 1.9 | 23.8 |
| 14 | Lookahead + cutoff crossings (`lookahead-cutoff`) | Planning (exact bot model) | no | 13.708 | 0.175 | 13 | 17.22 | 0 | 5.7 | 0.44 | 0 | 1.9 | 25.2 |
| 15 | Lookahead + refinement (`lookahead-refine`) | Planning (exact bot model) | no | 13.708 | 0.175 | 14 | 18.22 | 0 | 5.7 | 0.44 | 0 | 1.9 | 19.3 |
| 16 | Cycle-Aware planner (selected) (`cycle-aware`) | Planning (exact bot model) | no | 13.708 | 0.175 | 10 | 14.22 | 0 | 5.7 | 0.44 | 0 | 1.9 | 39.7 |
| 17 | + online battery physics (`physics`) | Planning (exact bot model) | no | 13.708 | 0.175 | 15 | 19.22 | 0 | 5.7 | 0.44 | 0 | 2.0 | 16.9 |
| 18 | + market residual (`residual`) | Planning (exact bot model) | no | 12.921 | 0.094 | 29 | 25.38 | 0 | 20.0 | 1.32 | 0 | 29.7 | 103 |
| 19 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 13.491 | 0.098 | 24 | 18.25 | 0 | 20.6 | 0.80 | 0 | 46.6 | 140 |
| 20 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 13.603 | 0.089 | 22 | 16.89 | 1 | 20.4 | 0.77 | 0 | 46.0 | 161 |
| 21 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 13.408 | 0.115 | 27 | 19.03 | 1 | 20.8 | 0.83 | 0 | 46.3 | 152 |
| 22 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 13.236 | 0.115 | 28 | 20.86 | 0 | 21.3 | 0.78 | 0 | 43.4 | 159 |
| 23 | + strategy modes (`modes`) | Planning (exact bot model) | no | 13.446 | 0.109 | 26 | 19.04 | 0 | 19.5 | 0.77 | 0 | 29.4 | 108 |
| 24 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 13.632 | 0.121 | 21 | 16.25 | 7 | 18.1 | 1.31 | 0 | 28.8 | 109 |
| 25 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 13.830 | 0.136 | 5 | 13.98 | 2 | 19.5 | 0.90 | 0 | 37.4 | 157 |
| 26 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 13.640 | 0.124 | 20 | 17.16 | 2 | 20.4 | 0.90 | 0 | 66.1 | 237 |
| 27 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 13.643 | 0.142 | 19 | 16.51 | 6 | 21.0 | 1.00 | 0 | 100 | 356 |
| 28 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 13.559 | 0.135 | 23 | 17.34 | 0 | 20.6 | 1.04 | 0 | 105 | 396 |
| 29 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 14.775 | 0.283 | 2 | 7.02 | 23 | 3.0 | 0.31 | 0 | 2.1 | 23.4 |
| 30 | Learned value (ridge), greedy (`ridge-value`) | Machine learning | no | 13.708 | 0.175 | 18 | 22.22 | 0 | 5.7 | 0.44 | 0 | 2.0 | 12.3 |
| 31 | Planner + ridge terminal (4 rounds) (`ridge-terminal-4`) | Machine learning | no | 13.708 | 0.175 | 16 | 20.22 | 0 | 5.7 | 0.44 | 0 | 1.9 | 24.2 |
| 32 | Planner + ridge terminal (6 rounds) (`ridge-terminal-6`) | Machine learning | no | 13.708 | 0.175 | 17 | 21.22 | 0 | 5.7 | 0.44 | 0 | 1.9 | 14.5 |
| 33 | Planner + CatBoost terminal (`catboost-terminal`) | Machine learning | no | 13.708 | 0.175 | 9 | 13.22 | 0 | 5.7 | 0.44 | 0 | 1.9 | 11.3 |
| 34 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 12.888 | 0.098 | 30 | 26.03 | 0 | 20.0 | 1.33 | 0 | 30.6 | 152 |
| 35 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 13.874 | 0.148 | 4 | 13.98 | 8 | 21.2 | 1.13 | 0 | 80.4 | 305 |
| 36 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 13.489 | 0.166 | 25 | 17.57 | 7 | 22.5 | 0.77 | 0 | 75.6 | 286 |

Market-level, per episode: log social welfare **-2045.5**, welfare (Σ of all 36 scores) **482.52**.

Times are wall-clock milliseconds per decision measured inside the run (2 parallel workers), so they include contention; they are comparable across agents, not portable.
