# All together: every entry in one market (capacity scale 9.0)

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Mean rank (of 37) | First places | Idle | Floors | Exceptions | ms mean | ms max |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Random split (reference) (`random`) | Reference | yes | 7.950 | 0.199 | 37 | 36.76 | 0 | 24.4 | 26.26 | 0 | 0.013 | 4.1 |
| 2 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 11.995 | 0.155 | 32 | 29.37 | 0 | 26.2 | 2.48 | 0 | 0.005 | 0.064 |
| 3 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 10.982 | 0.352 | 35 | 31.13 | 1 | 27.8 | 8.18 | 0 | 0.003 | 0.084 |
| 4 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 9.566 | 0.317 | 36 | 35.35 | 0 | 28.2 | 18.77 | 0 | 0.014 | 0.640 |
| 5 | Template: weight bids (`template`) | Traditional (rules) | yes | 11.995 | 0.155 | 33 | 28.37 | 0 | 26.2 | 2.48 | 0 | 0.429 | 4.0 |
| 6 | Battery taper (`taper`) | Traditional (rules) | yes | 13.450 | 0.178 | 8 | 11.94 | 0 | 5.4 | 0.74 | 0 | 0.658 | 23.1 |
| 7 | Floor reservation (`floors`) | Optimization (one round) | yes | 12.272 | 0.146 | 31 | 26.16 | 1 | 25.9 | 1.06 | 0 | 0.405 | 4.8 |
| 8 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 11.867 | 0.160 | 34 | 29.58 | 0 | 28.0 | 4.98 | 0 | 0.392 | 8.5 |
| 9 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 14.026 | 0.139 | 3 | 7.46 | 7 | 9.6 | 0.38 | 0 | 0.602 | 7.5 |
| 10 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 13.444 | 0.175 | 12 | 14.48 | 0 | 5.4 | 0.55 | 0 | 2.0 | 14.0 |
| 11 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 14.416 | 0.286 | 1 | 6.87 | 36 | 3.0 | 0.35 | 0 | 2.0 | 19.1 |
| 12 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 13.481 | 0.175 | 7 | 10.14 | 0 | 5.4 | 0.49 | 0 | 2.0 | 8.9 |
| 13 | Best response to bot forecasts (`bot-aware`) | Optimization (one round) | no | 13.444 | 0.175 | 9 | 11.48 | 0 | 5.4 | 0.55 | 0 | 2.0 | 42.4 |
| 14 | Lookahead planner (MPC) (`lookahead`) | Planning (exact bot model) | no | 13.444 | 0.175 | 13 | 15.48 | 0 | 5.4 | 0.55 | 0 | 2.0 | 24.9 |
| 15 | Lookahead + cutoff crossings (`lookahead-cutoff`) | Planning (exact bot model) | no | 13.444 | 0.175 | 14 | 16.48 | 0 | 5.4 | 0.55 | 0 | 1.9 | 12.1 |
| 16 | Lookahead + refinement (`lookahead-refine`) | Planning (exact bot model) | no | 13.444 | 0.175 | 15 | 17.48 | 0 | 5.4 | 0.55 | 0 | 1.9 | 12.3 |
| 17 | Cycle-Aware planner (selected) (`cycle-aware`) | Planning (exact bot model) | no | 13.444 | 0.175 | 11 | 13.48 | 0 | 5.4 | 0.55 | 0 | 2.0 | 16.9 |
| 18 | + online battery physics (`physics`) | Planning (exact bot model) | no | 13.444 | 0.175 | 16 | 18.48 | 0 | 5.4 | 0.55 | 0 | 2.1 | 85.6 |
| 19 | + market residual (`residual`) | Planning (exact bot model) | no | 12.628 | 0.106 | 29 | 23.46 | 0 | 19.4 | 1.43 | 0 | 30.9 | 99.5 |
| 20 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 12.764 | 0.124 | 25 | 21.18 | 0 | 20.9 | 1.02 | 0 | 59.3 | 457 |
| 21 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 12.653 | 0.122 | 28 | 22.79 | 0 | 21.2 | 1.03 | 0 | 57.8 | 198 |
| 22 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 12.669 | 0.116 | 27 | 22.19 | 0 | 21.0 | 1.04 | 0 | 58.2 | 250 |
| 23 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 12.705 | 0.120 | 26 | 22.12 | 0 | 21.5 | 1.14 | 0 | 39.4 | 121 |
| 24 | + strategy modes (`modes`) | Planning (exact bot model) | no | 12.850 | 0.110 | 24 | 22.22 | 0 | 19.6 | 0.98 | 0 | 37.0 | 174 |
| 25 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 13.218 | 0.118 | 22 | 16.31 | 2 | 17.9 | 1.50 | 0 | 30.1 | 110 |
| 26 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 13.652 | 0.132 | 4 | 12.58 | 6 | 18.4 | 1.02 | 0 | 39.8 | 140 |
| 27 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 13.517 | 0.146 | 6 | 13.81 | 5 | 19.2 | 1.11 | 0 | 73.8 | 421 |
| 28 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 13.361 | 0.138 | 20 | 15.16 | 2 | 19.9 | 1.20 | 0 | 114 | 388 |
| 29 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 13.360 | 0.136 | 21 | 15.45 | 4 | 19.4 | 1.12 | 0 | 120 | 462 |
| 30 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 14.363 | 0.278 | 2 | 6.90 | 18 | 3.0 | 0.36 | 0 | 2.1 | 18.5 |
| 31 | Learned value (ridge), greedy (`ridge-value`) | Machine learning | no | 13.444 | 0.175 | 19 | 21.48 | 0 | 5.4 | 0.55 | 0 | 2.1 | 29.7 |
| 32 | Planner + ridge terminal (4 rounds) (`ridge-terminal-4`) | Machine learning | no | 13.444 | 0.175 | 17 | 19.48 | 0 | 5.4 | 0.55 | 0 | 2.0 | 22.4 |
| 33 | Planner + ridge terminal (6 rounds) (`ridge-terminal-6`) | Machine learning | no | 13.444 | 0.175 | 18 | 20.48 | 0 | 5.4 | 0.55 | 0 | 2.0 | 43.1 |
| 34 | Planner + CatBoost terminal (`catboost-terminal`) | Machine learning | no | 13.444 | 0.175 | 10 | 12.48 | 0 | 5.4 | 0.55 | 0 | 2.0 | 18.2 |
| 35 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 12.614 | 0.116 | 30 | 23.75 | 0 | 19.4 | 1.52 | 0 | 31.9 | 95.8 |
| 36 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 13.531 | 0.164 | 5 | 13.59 | 10 | 20.4 | 1.28 | 0 | 87.5 | 306 |
| 37 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 13.093 | 0.205 | 23 | 17.08 | 8 | 21.6 | 0.99 | 0 | 81.2 | 247 |

Market-level, per episode: log social welfare **-2180.3**, welfare (Σ of all 37 scores) **476.87**.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
