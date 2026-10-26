# All together: every entry in one market

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Mean rank (of 37) | First places | Idle | Floors | Exceptions | ms mean | ms max |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Random split (reference) (`random`) | Reference | yes | 0.440 | 0.013 | 5 | 5.77 | 0 | 9.2 | 101.58 | 0 | 0.011 | 1.1 |
| 2 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 0.514 | 0.014 | 1 | 2.81 | 0 | 7.7 | 104.62 | 0 | 0.006 | 0.333 |
| 3 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 0.510 | 0.015 | 3 | 2.45 | 33 | 10.0 | 100.00 | 0 | 0.003 | 0.490 |
| 4 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 0.509 | 0.018 | 4 | 2.99 | 26 | 12.4 | 95.24 | 0 | 0.019 | 2.2 |
| 5 | Template: weight bids (`template`) | Traditional (rules) | yes | 0.514 | 0.014 | 2 | 1.81 | 41 | 7.7 | 104.62 | 0 | 0.676 | 12.1 |
| 6 | Battery taper (`taper`) | Traditional (rules) | yes | 0.402 | 0.003 | 6 | 5.82 | 0 | 1.1 | 117.88 | 0 | 0.715 | 26.2 |
| 7 | Floor reservation (`floors`) | Optimization (one round) | yes | 0.250 | 0.008 | 21 | 21.13 | 0 | 0.0 | 120.00 | 0 | 0.714 | 33.7 |
| 8 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 0.250 | 0.008 | 22 | 22.68 | 0 | 0.0 | 120.00 | 0 | 0.708 | 12.6 |
| 9 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 0.249 | 0.008 | 24 | 27.72 | 0 | 0.0 | 120.00 | 0 | 0.722 | 18.3 |
| 10 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 0.241 | 0.008 | 28 | 26.78 | 0 | 0.0 | 120.00 | 0 | 0.767 | 12.6 |
| 11 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 0.239 | 0.008 | 37 | 36.94 | 0 | 0.0 | 120.00 | 0 | 0.772 | 25.5 |
| 12 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 0.250 | 0.008 | 23 | 25.37 | 0 | 0.0 | 120.00 | 0 | 0.777 | 25.3 |
| 13 | Best response to bot forecasts (`bot-aware`) | Optimization (one round) | no | 0.241 | 0.008 | 25 | 23.73 | 0 | 0.0 | 120.00 | 0 | 0.814 | 21.0 |
| 14 | Lookahead planner (MPC) (`lookahead`) | Planning (exact bot model) | no | 0.241 | 0.008 | 29 | 28.32 | 0 | 0.0 | 120.00 | 0 | 0.785 | 8.4 |
| 15 | Lookahead + cutoff crossings (`lookahead-cutoff`) | Planning (exact bot model) | no | 0.241 | 0.008 | 30 | 29.32 | 0 | 0.0 | 120.00 | 0 | 0.784 | 8.5 |
| 16 | Lookahead + refinement (`lookahead-refine`) | Planning (exact bot model) | no | 0.241 | 0.008 | 31 | 30.32 | 0 | 0.0 | 120.00 | 0 | 0.786 | 15.0 |
| 17 | Cycle-Aware planner (selected) (`cycle-aware`) | Planning (exact bot model) | no | 0.241 | 0.008 | 27 | 25.73 | 0 | 0.0 | 120.00 | 0 | 0.771 | 13.3 |
| 18 | + online battery physics (`physics`) | Planning (exact bot model) | no | 0.241 | 0.008 | 32 | 31.46 | 0 | 0.0 | 120.00 | 0 | 0.924 | 10.4 |
| 19 | + market residual (`residual`) | Planning (exact bot model) | no | 0.293 | 0.008 | 15 | 15.27 | 0 | 1.4 | 117.06 | 0 | 47.5 | 114 |
| 20 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 0.337 | 0.004 | 8 | 9.83 | 0 | 2.9 | 114.24 | 0 | 83.3 | 222 |
| 21 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 0.336 | 0.004 | 9 | 10.45 | 0 | 2.9 | 114.20 | 0 | 82.7 | 229 |
| 22 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 0.327 | 0.004 | 10 | 10.62 | 0 | 2.2 | 115.56 | 0 | 83.1 | 325 |
| 23 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 0.291 | 0.008 | 17 | 14.38 | 0 | 0.4 | 119.18 | 0 | 72.4 | 447 |
| 24 | + strategy modes (`modes`) | Planning (exact bot model) | no | 0.268 | 0.009 | 20 | 19.75 | 0 | 0.0 | 119.88 | 0 | 62.3 | 190 |
| 25 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 0.294 | 0.008 | 14 | 14.25 | 0 | 1.4 | 117.17 | 0 | 48.5 | 194 |
| 26 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 0.284 | 0.007 | 19 | 16.72 | 0 | 0.0 | 119.74 | 0 | 57.5 | 207 |
| 27 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 0.317 | 0.005 | 11 | 12.88 | 0 | 1.2 | 117.35 | 0 | 132 | 456 |
| 28 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 0.300 | 0.006 | 12 | 14.22 | 0 | 0.7 | 118.44 | 0 | 331 | 808 |
| 29 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 0.294 | 0.006 | 13 | 14.84 | 0 | 0.3 | 119.06 | 0 | 333 | 916 |
| 30 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 0.240 | 0.008 | 36 | 35.94 | 0 | 0.0 | 120.00 | 0 | 0.920 | 12.6 |
| 31 | Learned value (ridge), greedy (`ridge-value`) | Machine learning | no | 0.241 | 0.008 | 35 | 34.55 | 0 | 0.0 | 120.00 | 0 | 0.875 | 19.0 |
| 32 | Planner + ridge terminal (4 rounds) (`ridge-terminal-4`) | Machine learning | no | 0.241 | 0.008 | 33 | 32.55 | 0 | 0.0 | 120.00 | 0 | 0.833 | 35.0 |
| 33 | Planner + ridge terminal (6 rounds) (`ridge-terminal-6`) | Machine learning | no | 0.241 | 0.008 | 34 | 33.55 | 0 | 0.0 | 120.00 | 0 | 0.801 | 8.0 |
| 34 | Planner + CatBoost terminal (`catboost-terminal`) | Machine learning | no | 0.241 | 0.008 | 26 | 24.73 | 0 | 0.0 | 120.00 | 0 | 0.797 | 8.0 |
| 35 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 0.292 | 0.008 | 16 | 15.03 | 0 | 1.5 | 116.99 | 0 | 46.3 | 156 |
| 36 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 0.291 | 0.007 | 18 | 14.92 | 0 | 0.2 | 118.99 | 0 | 98.4 | 259 |
| 37 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 0.372 | 0.006 | 7 | 7.37 | 0 | 1.7 | 115.99 | 0 | 81.0 | 297 |

Market-level, per episode: log social welfare **-11521.3**, welfare (Σ of all 37 scores) **11.32**.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
