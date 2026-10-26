# All together: every entry in one market (capacity scale 9.0)

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Mean rank (of 37) | First places | Idle | Floors | Exceptions | ms mean | ms max |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Oracle (reference) (`clairvoyant`) | Reference | no | 16.070 | 0.143 | 1 | 1.48 | 72 | 10.0 | 0.00 | 0 | 4263 | 11817 |
| 2 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 12.009 | 0.161 | 33 | 29.76 | 0 | 26.6 | 2.65 | 0 | 0.006 | 0.092 |
| 3 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 11.009 | 0.353 | 36 | 31.34 | 0 | 27.9 | 8.64 | 0 | 0.005 | 3.1 |
| 4 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 9.326 | 0.322 | 37 | 36.33 | 0 | 28.4 | 19.77 | 0 | 0.015 | 0.217 |
| 5 | Template: weight bids (`template`) | Traditional (rules) | yes | 12.009 | 0.161 | 34 | 28.76 | 0 | 26.6 | 2.65 | 0 | 0.550 | 8.7 |
| 6 | Battery taper (`taper`) | Traditional (rules) | yes | 13.338 | 0.170 | 19 | 12.81 | 0 | 5.6 | 0.86 | 0 | 0.702 | 16.7 |
| 7 | Floor reservation (`floors`) | Optimization (one round) | yes | 12.276 | 0.156 | 32 | 26.46 | 0 | 26.3 | 1.09 | 0 | 0.394 | 4.5 |
| 8 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 11.923 | 0.154 | 35 | 30.09 | 0 | 28.0 | 5.11 | 0 | 0.388 | 7.4 |
| 9 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 13.839 | 0.129 | 4 | 8.35 | 0 | 10.2 | 0.38 | 0 | 0.588 | 7.6 |
| 10 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 13.342 | 0.170 | 11 | 15.46 | 0 | 5.5 | 0.52 | 0 | 2.0 | 33.8 |
| 11 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 14.306 | 0.275 | 2 | 7.60 | 20 | 3.0 | 0.33 | 0 | 2.0 | 12.6 |
| 12 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 13.406 | 0.169 | 6 | 10.97 | 0 | 5.5 | 0.47 | 0 | 2.0 | 33.1 |
| 13 | Best response to bot forecasts (`bot-aware`) | Optimization (one round) | no | 13.342 | 0.170 | 8 | 12.46 | 0 | 5.5 | 0.52 | 0 | 2.0 | 24.4 |
| 14 | Lookahead planner (MPC) (`lookahead`) | Planning (exact bot model) | no | 13.342 | 0.170 | 12 | 16.46 | 0 | 5.5 | 0.52 | 0 | 2.0 | 13.0 |
| 15 | Lookahead + cutoff crossings (`lookahead-cutoff`) | Planning (exact bot model) | no | 13.342 | 0.170 | 13 | 17.46 | 0 | 5.5 | 0.52 | 0 | 2.0 | 31.1 |
| 16 | Lookahead + refinement (`lookahead-refine`) | Planning (exact bot model) | no | 13.342 | 0.170 | 14 | 18.46 | 0 | 5.5 | 0.52 | 0 | 2.0 | 10.5 |
| 17 | Cycle-Aware planner (selected) (`cycle-aware`) | Planning (exact bot model) | no | 13.342 | 0.170 | 10 | 14.46 | 0 | 5.5 | 0.52 | 0 | 2.0 | 8.4 |
| 18 | + online battery physics (`physics`) | Planning (exact bot model) | no | 13.342 | 0.170 | 15 | 19.46 | 0 | 5.5 | 0.52 | 0 | 2.2 | 15.6 |
| 19 | + market residual (`residual`) | Planning (exact bot model) | no | 12.486 | 0.112 | 31 | 25.76 | 0 | 19.7 | 1.43 | 0 | 32.4 | 134 |
| 20 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 12.669 | 0.104 | 26 | 22.31 | 0 | 21.2 | 1.07 | 0 | 61.7 | 172 |
| 21 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 12.591 | 0.118 | 27 | 22.87 | 0 | 21.6 | 1.07 | 0 | 60.0 | 257 |
| 22 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 12.566 | 0.112 | 28 | 24.11 | 0 | 21.4 | 1.16 | 0 | 60.1 | 155 |
| 23 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 12.564 | 0.113 | 29 | 24.32 | 0 | 21.7 | 1.26 | 0 | 40.2 | 163 |
| 24 | + strategy modes (`modes`) | Planning (exact bot model) | no | 12.732 | 0.098 | 25 | 22.52 | 0 | 19.9 | 1.12 | 0 | 37.7 | 109 |
| 25 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 13.159 | 0.127 | 23 | 16.19 | 0 | 18.1 | 1.48 | 0 | 31.6 | 129 |
| 26 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 13.422 | 0.144 | 5 | 13.96 | 0 | 18.8 | 1.26 | 0 | 41.6 | 137 |
| 27 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 13.280 | 0.140 | 20 | 15.86 | 0 | 19.8 | 1.21 | 0 | 75.2 | 327 |
| 28 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 13.236 | 0.125 | 21 | 16.14 | 0 | 20.6 | 1.08 | 0 | 113 | 384 |
| 29 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 13.216 | 0.147 | 22 | 16.21 | 0 | 20.1 | 1.12 | 0 | 119 | 462 |
| 30 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 14.276 | 0.263 | 3 | 7.08 | 8 | 3.0 | 0.34 | 0 | 2.2 | 20.9 |
| 31 | Learned value (ridge), greedy (`ridge-value`) | Machine learning | no | 13.342 | 0.170 | 18 | 22.46 | 0 | 5.5 | 0.52 | 0 | 2.1 | 43.1 |
| 32 | Planner + ridge terminal (4 rounds) (`ridge-terminal-4`) | Machine learning | no | 13.342 | 0.170 | 16 | 20.46 | 0 | 5.5 | 0.52 | 0 | 2.1 | 15.8 |
| 33 | Planner + ridge terminal (6 rounds) (`ridge-terminal-6`) | Machine learning | no | 13.342 | 0.170 | 17 | 21.46 | 0 | 5.5 | 0.52 | 0 | 2.1 | 23.9 |
| 34 | Planner + CatBoost terminal (`catboost-terminal`) | Machine learning | no | 13.342 | 0.170 | 9 | 13.46 | 0 | 5.5 | 0.52 | 0 | 2.0 | 14.2 |
| 35 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 12.495 | 0.113 | 30 | 25.25 | 0 | 19.6 | 1.48 | 0 | 33.1 | 98.6 |
| 36 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 13.374 | 0.135 | 7 | 14.35 | 0 | 20.9 | 1.51 | 0 | 87.7 | 319 |
| 37 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 12.856 | 0.181 | 24 | 20.06 | 0 | 22.3 | 1.08 | 0 | 82.8 | 301 |

Market-level, per episode: log social welfare **-2171.7**, welfare (Σ of all 37 scores) **481.19**.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
