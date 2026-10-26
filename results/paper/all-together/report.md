# All together: every entry in one market

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Mean rank (of 36) | First places | Idle | Floors | Exceptions | ms mean | ms max |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 0.532 | 0.015 | 1 | 2.87 | 0 | 8.1 | 103.80 | 0 | 0.006 | 0.399 |
| 2 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 0.529 | 0.017 | 3 | 2.54 | 32 | 10.5 | 99.06 | 0 | 0.003 | 0.134 |
| 3 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 0.528 | 0.020 | 4 | 2.81 | 29 | 13.0 | 93.96 | 0 | 0.019 | 2.6 |
| 4 | Template: weight bids (`template`) | Traditional (rules) | yes | 0.532 | 0.015 | 2 | 1.87 | 39 | 8.1 | 103.80 | 0 | 0.661 | 11.0 |
| 5 | Battery taper (`taper`) | Traditional (rules) | yes | 0.413 | 0.004 | 5 | 5.57 | 0 | 1.1 | 117.78 | 0 | 0.704 | 18.7 |
| 6 | Floor reservation (`floors`) | Optimization (one round) | yes | 0.258 | 0.008 | 20 | 19.95 | 0 | 0.0 | 119.99 | 0 | 0.702 | 8.6 |
| 7 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 0.258 | 0.008 | 21 | 21.36 | 0 | 0.0 | 119.99 | 0 | 0.697 | 17.4 |
| 8 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 0.257 | 0.008 | 23 | 25.78 | 0 | 0.0 | 119.99 | 0 | 0.706 | 17.3 |
| 9 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 0.247 | 0.008 | 27 | 25.96 | 0 | 0.0 | 120.00 | 0 | 0.756 | 11.5 |
| 10 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 0.245 | 0.008 | 36 | 35.93 | 0 | 0.0 | 120.00 | 0 | 0.751 | 20.9 |
| 11 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 0.257 | 0.008 | 22 | 23.85 | 0 | 0.0 | 119.99 | 0 | 0.763 | 12.7 |
| 12 | Best response to bot forecasts (`bot-aware`) | Optimization (one round) | no | 0.247 | 0.008 | 24 | 22.95 | 0 | 0.0 | 120.00 | 0 | 0.790 | 12.7 |
| 13 | Lookahead planner (MPC) (`lookahead`) | Planning (exact bot model) | no | 0.247 | 0.008 | 28 | 27.41 | 0 | 0.0 | 120.00 | 0 | 0.781 | 24.6 |
| 14 | Lookahead + cutoff crossings (`lookahead-cutoff`) | Planning (exact bot model) | no | 0.247 | 0.008 | 29 | 28.41 | 0 | 0.0 | 120.00 | 0 | 0.770 | 10.0 |
| 15 | Lookahead + refinement (`lookahead-refine`) | Planning (exact bot model) | no | 0.247 | 0.008 | 30 | 29.41 | 0 | 0.0 | 120.00 | 0 | 0.758 | 9.2 |
| 16 | Cycle-Aware planner (selected) (`cycle-aware`) | Planning (exact bot model) | no | 0.247 | 0.008 | 26 | 24.95 | 0 | 0.0 | 120.00 | 0 | 0.757 | 12.5 |
| 17 | + online battery physics (`physics`) | Planning (exact bot model) | no | 0.247 | 0.008 | 31 | 30.52 | 0 | 0.0 | 120.00 | 0 | 0.904 | 31.4 |
| 18 | + market residual (`residual`) | Planning (exact bot model) | no | 0.302 | 0.008 | 16 | 15.06 | 0 | 1.3 | 117.40 | 0 | 45.1 | 172 |
| 19 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 0.373 | 0.006 | 7 | 8.30 | 0 | 4.2 | 111.66 | 0 | 69.5 | 223 |
| 20 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 0.372 | 0.007 | 8 | 8.34 | 0 | 4.1 | 111.66 | 0 | 69.7 | 257 |
| 21 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 0.363 | 0.006 | 9 | 8.91 | 0 | 3.5 | 112.85 | 0 | 69.9 | 230 |
| 22 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 0.355 | 0.008 | 10 | 9.20 | 0 | 3.5 | 112.92 | 0 | 62.9 | 193 |
| 23 | + strategy modes (`modes`) | Planning (exact bot model) | no | 0.281 | 0.009 | 19 | 18.79 | 0 | 0.1 | 119.71 | 0 | 49.5 | 183 |
| 24 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 0.303 | 0.008 | 15 | 14.61 | 0 | 1.4 | 117.20 | 0 | 45.9 | 178 |
| 25 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 0.301 | 0.007 | 17 | 15.57 | 0 | 0.2 | 119.30 | 0 | 53.6 | 198 |
| 26 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 0.324 | 0.007 | 11 | 12.46 | 0 | 1.2 | 117.23 | 0 | 122 | 355 |
| 27 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 0.306 | 0.006 | 12 | 14.29 | 0 | 0.6 | 118.45 | 0 | 309 | 847 |
| 28 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 0.305 | 0.007 | 13 | 14.21 | 0 | 0.5 | 118.81 | 0 | 308 | 934 |
| 29 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 0.245 | 0.008 | 35 | 34.93 | 0 | 0.0 | 120.00 | 0 | 0.910 | 22.4 |
| 30 | Learned value (ridge), greedy (`ridge-value`) | Machine learning | no | 0.247 | 0.008 | 34 | 33.57 | 0 | 0.0 | 120.00 | 0 | 0.849 | 14.1 |
| 31 | Planner + ridge terminal (4 rounds) (`ridge-terminal-4`) | Machine learning | no | 0.247 | 0.008 | 32 | 31.57 | 0 | 0.0 | 120.00 | 0 | 0.810 | 27.1 |
| 32 | Planner + ridge terminal (6 rounds) (`ridge-terminal-6`) | Machine learning | no | 0.247 | 0.008 | 33 | 32.57 | 0 | 0.0 | 120.00 | 0 | 0.785 | 9.4 |
| 33 | Planner + CatBoost terminal (`catboost-terminal`) | Machine learning | no | 0.247 | 0.008 | 25 | 23.95 | 0 | 0.0 | 120.00 | 0 | 0.784 | 35.7 |
| 34 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 0.304 | 0.008 | 14 | 14.70 | 0 | 1.2 | 117.59 | 0 | 43.9 | 208 |
| 35 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 0.297 | 0.007 | 18 | 15.46 | 0 | 0.2 | 118.91 | 0 | 91.6 | 348 |
| 36 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 0.384 | 0.007 | 6 | 7.37 | 0 | 1.5 | 116.42 | 0 | 75.2 | 337 |

Market-level, per episode: log social welfare **-11149.7**, welfare (Σ of all 36 scores) **11.34**.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
