# Head-to-head: every pair of entries, alone in a market

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Matches | Win rate | Win rate (distinct) | Win rank | Opponents beaten (>50%) | Mean score | Mean margin | Idle | Floors | Exceptions | ms mean | ms max | Log social welfare | Welfare (Σ scores) |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Oracle (reference) (`clairvoyant`) | Reference | no | 3700 | 0.838 | 0.866 | 1 | 37/37 | 29.585 | +2.103 | 24.5 | 0.21 | 0 | 263 | 2539 | -18.2 | 57.07 |
| 2 | Random split (reference) (`random`) | Reference | yes | 3700 | 0.096 | 0.090 | 38 | 0/37 | 25.654 | -3.995 | 27.7 | 3.02 | 0 | 0.005 | 5.2 | -21.7 | 55.30 |
| 3 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 200 | 0.425 | nan | 34 | 1/37 | 29.291 | -0.478 | 28.1 | 0.01 | 0 | 0.002 | 0.123 | -8.9 | 59.06 |
| 4 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 200 | 0.405 | nan | 36 | 1/37 | 29.001 | -0.920 | 28.2 | 0.00 | 0 | 0.002 | 0.831 | -9.3 | 58.92 |
| 5 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 200 | 0.435 | nan | 32 | 1/37 | 29.187 | -0.586 | 28.1 | 0.00 | 0 | 0.013 | 0.458 | -9.1 | 58.96 |
| 6 | Template: weight bids (`template`) | Traditional (rules) | yes | 200 | 0.425 | nan | 35 | 1/37 | 29.291 | -0.478 | 28.1 | 0.01 | 0 | 0.301 | 5.3 | -8.9 | 59.06 |
| 7 | Battery taper (`taper`) | Traditional (rules) | yes | 200 | 0.605 | nan | 4 | 1/37 | 29.722 | +0.267 | 27.9 | 0.00 | 0 | 0.287 | 7.6 | -8.1 | 59.18 |
| 8 | Floor reservation (`floors`) | Optimization (one round) | yes | 200 | 0.425 | nan | 33 | 1/37 | 29.289 | -0.478 | 28.1 | 0.01 | 0 | 0.299 | 11.9 | -8.9 | 59.06 |
| 9 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 200 | 0.365 | nan | 37 | 1/37 | 29.147 | -0.662 | 28.2 | 0.10 | 0 | 0.281 | 6.7 | -9.0 | 58.96 |
| 10 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 200 | 0.605 | nan | 3 | 1/37 | 29.684 | +0.248 | 27.8 | 0.03 | 0 | 0.315 | 3.7 | -8.3 | 59.12 |
| 11 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 200 | 0.575 | nan | 10 | 1/37 | 29.678 | +0.200 | 27.9 | 0.01 | 0 | 1.7 | 15.3 | -8.2 | 59.16 |
| 12 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 200 | 0.645 | nan | 2 | 1/37 | 29.911 | +0.738 | 27.7 | 0.01 | 0 | 1.7 | 8.2 | -7.8 | 59.08 |
| 13 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 200 | 0.590 | nan | 6 | 1/37 | 29.715 | +0.271 | 27.9 | 0.01 | 0 | 1.8 | 16.9 | -8.2 | 59.16 |
| 14 | Best response to bot forecasts (`bot-aware`) | Optimization (one round) | no | 200 | 0.575 | nan | 7 | 1/37 | 29.678 | +0.200 | 27.9 | 0.01 | 0 | 1.5 | 34.4 | -8.2 | 59.16 |
| 15 | Lookahead planner (MPC) (`lookahead`) | Planning (exact bot model) | no | 200 | 0.575 | nan | 13 | 1/37 | 29.678 | +0.200 | 27.9 | 0.01 | 5413 | 0.688 | 18.2 | -8.2 | 59.16 |
| 16 | Lookahead + cutoff crossings (`lookahead-cutoff`) | Planning (exact bot model) | no | 200 | 0.575 | nan | 11 | 1/37 | 29.678 | +0.200 | 27.9 | 0.01 | 5413 | 0.803 | 8.5 | -8.2 | 59.16 |
| 17 | Lookahead + refinement (`lookahead-refine`) | Planning (exact bot model) | no | 200 | 0.575 | nan | 12 | 1/37 | 29.678 | +0.200 | 27.9 | 0.01 | 5413 | 0.782 | 33.5 | -8.2 | 59.16 |
| 18 | Cycle-Aware planner (selected) (`cycle-aware`) | Planning (exact bot model) | no | 200 | 0.575 | nan | 9 | 1/37 | 29.678 | +0.200 | 27.9 | 0.01 | 5413 | 0.776 | 6.8 | -8.2 | 59.16 |
| 19 | + online battery physics (`physics`) | Planning (exact bot model) | no | 200 | 0.575 | nan | 14 | 1/37 | 29.678 | +0.200 | 27.9 | 0.01 | 0 | 1.8 | 21.8 | -8.2 | 59.16 |
| 20 | + market residual (`residual`) | Planning (exact bot model) | no | 200 | 0.540 | nan | 20 | 1/37 | 26.284 | +2.007 | 18.9 | 0.04 | 0 | 10.4 | 61.8 | -41.9 | 50.56 |
| 21 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 200 | 0.520 | nan | 28 | 1/37 | 27.034 | +2.882 | 19.4 | 0.03 | 0 | 30.1 | 267 | -38.8 | 51.19 |
| 22 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 200 | 0.520 | nan | 29 | 1/37 | 27.100 | +2.905 | 19.5 | 0.04 | 0 | 29.6 | 139 | -38.4 | 51.29 |
| 23 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 200 | 0.525 | nan | 25 | 1/37 | 26.687 | +2.749 | 19.2 | 0.04 | 0 | 27.8 | 86.7 | -40.5 | 50.62 |
| 24 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 200 | 0.600 | nan | 5 | 1/37 | 28.862 | +3.556 | 21.2 | 0.01 | 0 | 27.3 | 112 | -28.9 | 54.17 |
| 25 | + strategy modes (`modes`) | Planning (exact bot model) | no | 200 | 0.535 | nan | 22 | 1/37 | 28.636 | +1.106 | 25.1 | 0.00 | 0 | 25.7 | 73.9 | -19.9 | 56.16 |
| 26 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 200 | 0.530 | nan | 23 | 1/37 | 26.378 | +2.055 | 18.8 | 0.02 | 0 | 10.4 | 122 | -41.9 | 50.70 |
| 27 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 200 | 0.545 | nan | 19 | 1/37 | 26.505 | +2.509 | 18.6 | 0.06 | 0 | 10.6 | 89.0 | -42.0 | 50.50 |
| 28 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 200 | 0.475 | nan | 31 | 1/37 | 25.718 | +1.355 | 18.7 | 1.69 | 0 | 11.5 | 66.1 | -44.0 | 50.08 |
| 29 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 200 | 0.505 | nan | 30 | 1/37 | 26.537 | +2.401 | 19.1 | 0.24 | 0 | 14.1 | 66.4 | -41.2 | 50.67 |
| 30 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 200 | 0.520 | nan | 27 | 1/37 | 26.744 | +2.555 | 18.9 | 0.19 | 0 | 14.2 | 105 | -40.6 | 50.93 |
| 31 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 200 | 0.575 | nan | 17 | 1/37 | 29.778 | +0.495 | 27.7 | 0.01 | 0 | 1.7 | 9.4 | -8.1 | 59.06 |
| 32 | Learned value (ridge), greedy (`ridge-value`) | Machine learning | no | 200 | 0.570 | nan | 18 | 1/37 | 29.675 | +0.244 | 27.8 | 0.01 | 0 | 0.802 | 37.5 | -8.5 | 59.11 |
| 33 | Planner + ridge terminal (4 rounds) (`ridge-terminal-4`) | Machine learning | no | 200 | 0.575 | nan | 15 | 1/37 | 29.678 | +0.200 | 27.9 | 0.01 | 5413 | 0.789 | 23.3 | -8.2 | 59.16 |
| 34 | Planner + ridge terminal (6 rounds) (`ridge-terminal-6`) | Machine learning | no | 200 | 0.575 | nan | 16 | 1/37 | 29.678 | +0.200 | 27.9 | 0.01 | 5413 | 0.731 | 9.7 | -8.2 | 59.16 |
| 35 | Planner + CatBoost terminal (`catboost-terminal`) | Machine learning | no | 200 | 0.575 | nan | 8 | 1/37 | 29.678 | +0.200 | 27.9 | 0.01 | 5413 | 0.795 | 17.7 | -8.2 | 59.16 |
| 36 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 200 | 0.535 | nan | 21 | 1/37 | 26.288 | +2.005 | 18.9 | 0.04 | 0 | 10.9 | 83.0 | -41.8 | 50.57 |
| 37 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 200 | 0.520 | nan | 26 | 1/37 | 27.153 | +2.898 | 19.1 | 0.04 | 0 | 10.8 | 68.6 | -39.2 | 51.41 |
| 38 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 200 | 0.530 | nan | 24 | 1/37 | 27.393 | +3.373 | 18.5 | 0.03 | 0 | 9.8 | 78.5 | -39.8 | 51.41 |

Each pair plays every seed alone in a 2-node market. Win rate: share of all matches won (ties ½); win rate (distinct): mean over opponents that do not play exactly as another participant (catalog fallbacks), so duplicates count once, and reference points are not counted; margin: own score minus the opponent's; welfare and log social welfare are means over the agent's matches. The full pairwise matrix is in `summary.json` (`_matrix`).

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
