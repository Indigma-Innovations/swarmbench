# Head-to-head: every pair of entries, alone in a market

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Matches | Win rate | Win rate (distinct) | Win rank | Opponents beaten (>50%) | Mean score | Mean margin | Idle | Floors | Exceptions | ms mean | ms max | Log social welfare | Welfare (Σ scores) |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 3500 | 0.130 | 0.142 | 35 | 2/35 | 25.330 | -4.648 | 28.4 | 0.00 | 0 | 0.003 | 17.6 | -22.3 | 55.31 |
| 2 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 3500 | 0.079 | 0.080 | 36 | 0/35 | 25.383 | -5.513 | 28.7 | 0.00 | 0 | 0.002 | 0.614 | -21.0 | 56.28 |
| 3 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 3500 | 0.150 | 0.169 | 34 | 5/35 | 25.390 | -5.033 | 28.4 | 0.00 | 0 | 0.015 | 8.8 | -22.1 | 55.81 |
| 4 | Template: weight bids (`template`) | Traditional (rules) | yes | 3500 | 0.175 | 0.153 | 31 | 2/35 | 26.260 | -2.782 | 28.0 | 0.00 | 0 | 0.295 | 49.4 | -19.3 | 55.30 |
| 5 | Battery taper (`taper`) | Traditional (rules) | yes | 3500 | 0.333 | 0.453 | 27 | 11/35 | 24.078 | -0.446 | 25.3 | 0.00 | 0 | 0.324 | 39.5 | -32.4 | 48.60 |
| 6 | Floor reservation (`floors`) | Optimization (one round) | yes | 3500 | 0.170 | 0.134 | 32 | 1/35 | 26.253 | -2.778 | 28.0 | 0.00 | 0 | 0.309 | 45.8 | -19.4 | 55.28 |
| 7 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 3500 | 0.161 | 0.135 | 33 | 4/35 | 26.457 | -3.310 | 28.2 | 0.04 | 0 | 0.330 | 31.9 | -18.0 | 56.22 |
| 8 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 3500 | 0.387 | 0.409 | 24 | 10/35 | 27.590 | -0.974 | 27.3 | 0.00 | 0 | 0.360 | 74.1 | -17.5 | 56.15 |
| 9 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 3500 | 0.539 | 0.546 | 21 | 14/35 | 24.050 | -0.457 | 25.3 | 0.00 | 0 | 1.6 | 63.9 | -32.6 | 48.56 |
| 10 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 3500 | 0.823 | 0.829 | 3 | 33/35 | 29.129 | +1.227 | 25.3 | 0.00 | 0 | 1.6 | 60.5 | -17.2 | 57.03 |
| 11 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 3500 | 0.378 | 0.503 | 25 | 12/35 | 24.072 | -0.451 | 25.3 | 0.00 | 0 | 1.6 | 39.4 | -32.5 | 48.60 |
| 12 | Best response to bot forecasts (`bot-aware`) | Optimization (one round) | no | 3500 | 0.539 | 0.544 | 20 | 14/35 | 24.051 | -0.456 | 25.3 | 0.00 | 0 | 1.6 | 63.4 | -32.6 | 48.56 |
| 13 | Lookahead planner (MPC) (`lookahead`) | Planning (exact bot model) | no | 3500 | 0.554 | 0.565 | 15 | 14/35 | 24.167 | +0.145 | 24.4 | 0.00 | 38392 | 2.0 | 109 | -34.4 | 48.19 |
| 14 | Lookahead + cutoff crossings (`lookahead-cutoff`) | Planning (exact bot model) | no | 3500 | 0.554 | 0.565 | 14 | 14/35 | 24.173 | +0.115 | 24.5 | 0.00 | 38392 | 2.1 | 82.2 | -34.2 | 48.23 |
| 15 | Lookahead + refinement (`lookahead-refine`) | Planning (exact bot model) | no | 3500 | 0.555 | 0.566 | 13 | 14/35 | 24.147 | +0.267 | 24.1 | 0.00 | 38392 | 3.9 | 174 | -35.0 | 48.03 |
| 16 | Cycle-Aware planner (selected) (`cycle-aware`) | Planning (exact bot model) | no | 3500 | 0.555 | 0.567 | 11 | 14/35 | 24.172 | +0.242 | 24.2 | 0.00 | 38392 | 4.0 | 207 | -34.8 | 48.10 |
| 17 | + online battery physics (`physics`) | Planning (exact bot model) | no | 3500 | 0.555 | 0.567 | 12 | 14/35 | 24.172 | +0.242 | 24.2 | 0.00 | 0 | 2.5 | 83.6 | -34.8 | 48.10 |
| 18 | + market residual (`residual`) | Planning (exact bot model) | no | 3500 | 0.260 | 0.317 | 30 | 6/35 | 23.801 | -0.804 | 20.7 | 0.01 | 0 | 10.0 | 102 | -40.6 | 48.41 |
| 19 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 3500 | 0.556 | 0.553 | 10 | 25/35 | 26.058 | +0.934 | 20.5 | 0.01 | 0 | 24.9 | 219 | -35.0 | 51.18 |
| 20 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 3500 | 0.549 | 0.538 | 19 | 25/35 | 26.066 | +0.876 | 20.5 | 0.00 | 0 | 24.8 | 209 | -35.0 | 51.26 |
| 21 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 3500 | 0.511 | 0.507 | 23 | 11/35 | 25.830 | +0.663 | 20.5 | 0.00 | 0 | 24.3 | 188 | -35.6 | 51.00 |
| 22 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 3500 | 0.759 | 0.765 | 8 | 32/35 | 28.022 | +2.096 | 21.5 | 0.00 | 0 | 24.2 | 214 | -28.3 | 53.95 |
| 23 | + strategy modes (`modes`) | Planning (exact bot model) | no | 3500 | 0.343 | 0.382 | 26 | 8/35 | 26.893 | -0.643 | 25.1 | 0.00 | 0 | 23.1 | 177 | -24.0 | 54.43 |
| 24 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 3500 | 0.332 | 0.394 | 28 | 9/35 | 24.252 | -0.223 | 20.2 | 0.01 | 0 | 10.0 | 180 | -40.4 | 48.73 |
| 25 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 3500 | 0.796 | 0.752 | 5 | 31/35 | 26.928 | +3.282 | 17.6 | 0.02 | 0 | 9.6 | 119 | -39.2 | 50.58 |
| 26 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 3500 | 0.721 | 0.680 | 9 | 27/35 | 26.356 | +2.647 | 17.9 | 0.30 | 0 | 11.1 | 253 | -40.1 | 50.07 |
| 27 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 3500 | 0.772 | 0.725 | 7 | 29/35 | 26.692 | +2.952 | 17.8 | 0.03 | 0 | 14.1 | 186 | -39.3 | 50.43 |
| 28 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 3500 | 0.783 | 0.741 | 6 | 29/35 | 26.798 | +3.186 | 17.6 | 0.02 | 0 | 13.9 | 166 | -39.4 | 50.41 |
| 29 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 3500 | 0.810 | 0.834 | 4 | 35/35 | 29.047 | +1.110 | 25.3 | 0.00 | 0 | 1.6 | 43.3 | -17.5 | 56.98 |
| 30 | Learned value (ridge), greedy (`ridge-value`) | Machine learning | no | 3500 | 0.532 | 0.534 | 22 | 14/35 | 24.032 | -0.225 | 24.8 | 0.00 | 0 | 1.3 | 49.8 | -33.7 | 48.29 |
| 31 | Planner + ridge terminal (4 rounds) (`ridge-terminal-4`) | Machine learning | no | 3500 | 0.553 | 0.564 | 16 | 14/35 | 24.158 | +0.090 | 24.5 | 0.00 | 38392 | 1.7 | 61.9 | -34.2 | 48.23 |
| 32 | Planner + ridge terminal (6 rounds) (`ridge-terminal-6`) | Machine learning | no | 3500 | 0.553 | 0.564 | 17 | 14/35 | 24.159 | +0.143 | 24.4 | 0.00 | 38392 | 2.0 | 77.0 | -34.4 | 48.18 |
| 33 | Planner + CatBoost terminal (`catboost-terminal`) | Machine learning | no | 3500 | 0.553 | 0.564 | 18 | 14/35 | 24.163 | +0.145 | 24.4 | 0.00 | 38392 | 2.8 | 124 | -34.4 | 48.18 |
| 34 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 3500 | 0.288 | 0.350 | 29 | 7/35 | 23.889 | -0.703 | 20.5 | 0.01 | 0 | 10.1 | 170 | -40.7 | 48.48 |
| 35 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 3500 | 0.823 | 0.751 | 2 | 29/35 | 28.256 | +4.378 | 17.0 | 0.00 | 0 | 10.3 | 178 | -36.6 | 52.13 |
| 36 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 3500 | 0.867 | 0.810 | 1 | 32/35 | 28.374 | +4.706 | 16.5 | 0.00 | 0 | 8.4 | 103 | -37.3 | 52.04 |

Each pair plays every seed alone in a 2-node market. Win rate: share of all matches won (ties ½); win rate (distinct): mean over opponents that do not play exactly as another participant (catalog fallbacks), so duplicates count once, and reference points are not counted; margin: own score minus the opponent's; welfare and log social welfare are means over the agent's matches. The full pairwise matrix is in `summary.json` (`_matrix`).

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
