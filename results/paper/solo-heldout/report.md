# Solo: each entry against held-out opponents (energy-hoarder, contrarian, random)

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Δ vs cycle-aware (paired) | W/L vs cycle-aware | Beat all bots | Mean rank (of 4) | Idle | Floors | Exceptions | ms mean | ms max | Log social welfare | Bots' score | Welfare (Σ scores) |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 15.976 | 0.193 | 34 | -12.13% ±1.28 | 5/95 | 79/100 | 1.22 | 17.5 | 1.19 | 0 | 0.002 | 1.3 | -206.1 | 38.03 | 54.01 |
| 2 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 14.937 | 0.149 | 36 | -17.35% ±2.09 | 7/93 | 22/100 | 1.78 | 19.2 | 1.66 | 0 | 0.001 | 0.447 | -205.9 | 39.21 | 54.15 |
| 3 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 16.714 | 0.271 | 31 | -8.32% ±1.00 | 11/89 | 93/100 | 1.07 | 14.4 | 0.37 | 0 | 0.012 | 4.1 | -210.3 | 36.68 | 53.40 |
| 4 | Template: weight bids (`template`) | Traditional (rules) | yes | 15.976 | 0.193 | 35 | -12.13% ±1.28 | 5/95 | 79/100 | 1.22 | 17.5 | 1.19 | 0 | 0.615 | 32.4 | -206.1 | 38.03 | 54.01 |
| 5 | Battery taper (`taper`) | Traditional (rules) | yes | 18.306 | 0.366 | 18 | +0.09% ±0.30 | 32/68 | 100/100 | 1.00 | 3.9 | 0.34 | 0 | 0.803 | 18.9 | -229.0 | 31.97 | 50.28 |
| 6 | Floor reservation (`floors`) | Optimization (one round) | yes | 15.994 | 0.187 | 33 | -12.01% ±1.30 | 5/95 | 79/100 | 1.22 | 17.4 | 1.06 | 0 | 0.550 | 23.1 | -206.2 | 37.98 | 53.97 |
| 7 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 16.618 | 0.326 | 32 | -9.01% ±0.93 | 2/98 | 86/100 | 1.17 | 14.3 | 2.69 | 0 | 0.783 | 16.8 | -210.5 | 36.50 | 53.12 |
| 8 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 18.057 | 0.379 | 30 | -1.29% ±0.58 | 28/72 | 100/100 | 1.00 | 2.9 | 1.14 | 0 | 0.805 | 17.0 | -232.3 | 31.44 | 49.49 |
| 9 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 18.312 | 0.368 | 16 | +0.11% ±0.17 | 19/7 | 100/100 | 1.00 | 3.9 | 0.35 | 0 | 2.9 | 99.7 | -228.4 | 32.11 | 50.42 |
| 10 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 18.296 | 0.425 | 20 | -0.11% ±0.65 | 56/44 | 100/100 | 1.00 | 3.0 | 0.28 | 0 | 3.0 | 24.7 | -231.0 | 31.65 | 49.94 |
| 11 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 18.332 | 0.365 | 15 | +0.23% ±0.28 | 63/37 | 100/100 | 1.00 | 3.9 | 0.33 | 0 | 2.7 | 31.2 | -228.7 | 32.05 | 50.38 |
| 12 | Best response to bot forecasts (`bot-aware`) | Optimization (one round) | no | 18.289 | 0.367 | 28 | -0.02% ±0.15 | 8/17 | 100/100 | 1.00 | 3.9 | 0.35 | 0 | 2.7 | 34.3 | -228.7 | 32.10 | 50.39 |
| 13 | Lookahead planner (MPC) (`lookahead`) | Planning (exact bot model) | no | 18.292 | 0.366 | 23 | +0.00% ±0.00 | 0/0 | 100/100 | 1.00 | 3.9 | 0.33 | 34 | 2.8 | 35.8 | -228.5 | 32.16 | 50.45 |
| 14 | Lookahead + cutoff crossings (`lookahead-cutoff`) | Planning (exact bot model) | no | 18.292 | 0.366 | 24 | +0.00% ±0.00 | 0/0 | 100/100 | 1.00 | 3.9 | 0.33 | 34 | 2.9 | 83.9 | -228.5 | 32.16 | 50.45 |
| 15 | Lookahead + refinement (`lookahead-refine`) | Planning (exact bot model) | no | 18.292 | 0.366 | 25 | +0.00% ±0.00 | 0/0 | 100/100 | 1.00 | 3.9 | 0.33 | 34 | 2.9 | 26.9 | -228.5 | 32.16 | 50.45 |
| 16 | Cycle-Aware planner (selected) (`cycle-aware`) | Planning (exact bot model) | no | 18.292 | 0.366 | 22 | reference | — | 100/100 | 1.00 | 3.9 | 0.33 | 34 | 3.4 | 23.0 | -228.5 | 32.16 | 50.45 |
| 17 | + online battery physics (`physics`) | Planning (exact bot model) | no | 18.312 | 0.368 | 17 | +0.11% ±0.17 | 19/7 | 100/100 | 1.00 | 3.9 | 0.35 | 0 | 3.0 | 49.4 | -228.4 | 32.11 | 50.42 |
| 18 | + market residual (`residual`) | Planning (exact bot model) | no | 18.645 | 0.338 | 6 | +2.09% ±0.69 | 76/24 | 100/100 | 1.00 | 6.2 | 0.55 | 0 | 41.6 | 138 | -223.1 | 32.83 | 51.47 |
| 19 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 18.492 | 0.290 | 14 | +1.40% ±0.85 | 56/44 | 100/100 | 1.00 | 7.4 | 0.28 | 0 | 69.7 | 211 | -220.2 | 33.40 | 51.89 |
| 20 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 18.525 | 0.282 | 13 | +1.59% ±0.84 | 60/40 | 100/100 | 1.00 | 7.5 | 0.38 | 0 | 69.1 | 204 | -220.1 | 33.35 | 51.87 |
| 21 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 18.592 | 0.296 | 9 | +1.93% ±0.86 | 62/38 | 100/100 | 1.00 | 7.2 | 0.47 | 0 | 58.8 | 231 | -220.7 | 33.19 | 51.78 |
| 22 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 18.586 | 0.328 | 10 | +1.78% ±0.67 | 70/30 | 100/100 | 1.00 | 6.8 | 0.36 | 0 | 36.4 | 117 | -221.4 | 33.22 | 51.81 |
| 23 | + strategy modes (`modes`) | Planning (exact bot model) | no | 18.762 | 0.319 | 2 | +2.79% ±0.71 | 81/19 | 100/100 | 1.00 | 6.3 | 0.30 | 0 | 30.9 | 92.4 | -221.7 | 32.92 | 51.68 |
| 24 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 18.687 | 0.354 | 4 | +2.28% ±0.67 | 78/22 | 100/100 | 1.00 | 6.3 | 0.64 | 0 | 24.7 | 116 | -222.6 | 32.84 | 51.52 |
| 25 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 18.539 | 0.332 | 11 | +1.52% ±0.68 | 65/35 | 99/100 | 1.01 | 7.0 | 0.87 | 0 | 25.7 | 101 | -222.4 | 33.04 | 51.58 |
| 26 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 18.535 | 0.324 | 12 | +1.55% ±0.86 | 59/41 | 100/100 | 1.00 | 7.3 | 1.00 | 0 | 51.0 | 152 | -222.5 | 33.05 | 51.58 |
| 27 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 18.611 | 0.334 | 8 | +1.94% ±0.84 | 69/31 | 100/100 | 1.00 | 7.1 | 0.64 | 0 | 66.2 | 175 | -223.5 | 32.94 | 51.55 |
| 28 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 18.707 | 0.324 | 3 | +2.48% ±0.73 | 75/25 | 100/100 | 1.00 | 6.9 | 0.59 | 0 | 67.1 | 205 | -223.3 | 32.83 | 51.54 |
| 29 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 18.261 | 0.423 | 29 | -0.29% ±0.72 | 52/48 | 99/100 | 1.01 | 3.0 | 0.29 | 0 | 1.8 | 29.7 | -231.8 | 31.60 | 49.86 |
| 30 | Learned value (ridge), greedy (`ridge-value`) | Machine learning | no | 18.301 | 0.364 | 19 | +0.06% ±0.19 | 10/15 | 100/100 | 1.00 | 3.9 | 0.34 | 0 | 1.6 | 24.9 | -228.8 | 32.08 | 50.38 |
| 31 | Planner + ridge terminal (4 rounds) (`ridge-terminal-4`) | Machine learning | no | 18.292 | 0.366 | 26 | +0.00% ±0.00 | 0/0 | 100/100 | 1.00 | 3.9 | 0.33 | 34 | 1.8 | 15.5 | -228.5 | 32.16 | 50.45 |
| 32 | Planner + ridge terminal (6 rounds) (`ridge-terminal-6`) | Machine learning | no | 18.292 | 0.366 | 27 | +0.00% ±0.00 | 0/0 | 100/100 | 1.00 | 3.9 | 0.33 | 34 | 1.8 | 68.4 | -228.5 | 32.16 | 50.45 |
| 33 | Planner + CatBoost terminal (`catboost-terminal`) | Machine learning | no | 18.292 | 0.366 | 21 | +0.00% ±0.00 | 0/0 | 100/100 | 1.00 | 3.9 | 0.33 | 34 | 1.4 | 6.8 | -228.5 | 32.16 | 50.45 |
| 34 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 18.644 | 0.332 | 7 | +2.10% ±0.71 | 75/25 | 100/100 | 1.00 | 6.1 | 0.64 | 0 | 24.5 | 95.8 | -223.6 | 32.79 | 51.43 |
| 35 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 18.649 | 0.310 | 5 | +2.22% ±0.89 | 71/29 | 100/100 | 1.00 | 6.9 | 0.79 | 0 | 32.6 | 122 | -223.7 | 32.83 | 51.48 |
| 36 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 18.804 | 0.329 | 1 | +3.00% ±0.72 | 78/22 | 100/100 | 1.00 | 6.2 | 0.53 | 0 | 23.9 | 142 | -223.2 | 32.64 | 51.45 |

Log social welfare is the arena's Σ_i log u_i summed over rounds for the 4-node market; welfare is the sum of all four final scores. Δ is the mean per-seed relative gain with a normal 95% interval; W/L counts seeds with a strictly higher/lower score.

Times are wall-clock milliseconds per decision measured inside the run (2 parallel workers), so they include contention; they are comparable across agents, not portable.
