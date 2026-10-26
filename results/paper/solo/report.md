# Solo: each entry against the three supplied bots

Seeds 70001–70100 (100), `graded` scenario, 60 rounds, unchanged arena engine in-process. Every participant has the same device (minted from the seed and a fixed device label). Agents are listed in idea order: traditional rules, optimization, model-based planning, machine learning. **Realistic** = never uses the bots' names or code, so it can face unnamed opponents.

| # | Agent | Family | Realistic | Mean score | ±95% | Score rank | Δ vs cycle-aware (paired) | W/L vs cycle-aware | Beat all bots | Mean rank (of 4) | Idle | Floors | Exceptions | ms mean | ms max | Log social welfare | Bots' score | Welfare (Σ scores) |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Naive max (bot) (`naive-max`) | Traditional (rules) | yes | 13.366 | 0.122 | 34 | -29.33% ±1.22 | 0/100 | 0/100 | 2.60 | 18.6 | 1.82 | 0 | 0.002 | 1.4 | -186.0 | 44.76 | 58.13 |
| 2 | Even split (bot) (`even-split`) | Traditional (rules) | yes | 12.741 | 0.203 | 36 | -32.50% ±1.70 | 0/100 | 0/100 | 2.97 | 19.8 | 3.67 | 0 | 0.001 | 0.050 | -183.6 | 45.38 | 58.12 |
| 3 | Proportional (bot) (`proportional`) | Traditional (rules) | yes | 13.775 | 0.116 | 32 | -27.19% ±1.17 | 0/100 | 0/100 | 2.66 | 17.4 | 0.40 | 0 | 0.007 | 1.1 | -187.3 | 44.36 | 58.13 |
| 4 | Template: weight bids (`template`) | Traditional (rules) | yes | 13.366 | 0.122 | 35 | -29.33% ±1.22 | 0/100 | 0/100 | 2.60 | 18.6 | 1.82 | 0 | 0.346 | 7.6 | -186.0 | 44.76 | 58.13 |
| 5 | Battery taper (`taper`) | Traditional (rules) | yes | 17.083 | 0.273 | 27 | -10.03% ±1.12 | 1/99 | 95/100 | 1.05 | 4.3 | 0.48 | 0 | 0.442 | 16.1 | -202.3 | 38.37 | 55.45 |
| 6 | Floor reservation (`floors`) | Optimization (one round) | yes | 13.683 | 0.167 | 33 | -27.61% ±1.49 | 1/99 | 4/100 | 2.71 | 18.7 | 1.14 | 0 | 0.351 | 6.7 | -184.5 | 44.52 | 58.21 |
| 7 | Price-taker split + floors (`price-taker`) | Optimization (one round) | yes | 14.651 | 0.201 | 31 | -22.64% ±1.31 | 1/99 | 22/100 | 2.43 | 18.3 | 2.02 | 0 | 0.349 | 27.5 | -182.2 | 43.45 | 58.10 |
| 8 | Price-taker + taper (`market-taper`) | Optimization (one round) | yes | 17.154 | 0.284 | 24 | -9.67% ±1.14 | 2/98 | 96/100 | 1.04 | 4.0 | 0.59 | 0 | 0.555 | 32.5 | -202.4 | 38.22 | 55.37 |
| 9 | Guarded Kelly best response (`kelly`) | Optimization (one round) | yes | 17.107 | 0.278 | 26 | -9.90% ±1.16 | 2/98 | 95/100 | 1.05 | 4.3 | 0.49 | 0 | 1.6 | 9.5 | -201.9 | 38.42 | 55.53 |
| 10 | Kelly with drain price (`kelly-drain`) | Optimization (one round) | yes | 16.996 | 0.348 | 29 | -10.63% ±1.25 | 1/99 | 93/100 | 1.07 | 3.3 | 0.42 | 0 | 1.7 | 39.3 | -203.9 | 37.92 | 54.92 |
| 11 | Taper/Kelly blend (`kelly-blend`) | Optimization (one round) | yes | 17.110 | 0.276 | 25 | -9.88% ±1.15 | 2/98 | 95/100 | 1.05 | 4.3 | 0.44 | 0 | 1.7 | 37.6 | -202.1 | 38.39 | 55.50 |
| 12 | Best response to bot forecasts (`bot-aware`) | Optimization (one round) | no | 17.235 | 0.280 | 23 | -9.25% ±1.10 | 0/100 | 96/100 | 1.04 | 4.4 | 0.00 | 0 | 1.5 | 12.7 | -201.6 | 38.41 | 55.64 |
| 13 | Lookahead planner (MPC) (`lookahead`) | Planning (exact bot model) | no | 18.800 | 0.287 | 16 | -1.01% ±1.13 | 38/62 | 100/100 | 1.00 | 9.5 | 0.43 | 0 | 23.2 | 67.1 | -198.6 | 37.95 | 56.75 |
| 14 | Lookahead + cutoff crossings (`lookahead-cutoff`) | Planning (exact bot model) | no | 18.893 | 0.286 | 14 | -0.54% ±1.02 | 44/56 | 100/100 | 1.00 | 9.9 | 0.30 | 0 | 29.7 | 148 | -199.4 | 37.90 | 56.79 |
| 15 | Lookahead + refinement (`lookahead-refine`) | Planning (exact bot model) | no | 19.047 | 0.254 | 6 | +0.34% ±1.04 | 47/53 | 100/100 | 1.00 | 9.0 | 0.30 | 0 | 74.2 | 469 | -199.7 | 37.66 | 56.71 |
| 16 | Cycle-Aware planner (selected) (`cycle-aware`) | Planning (exact bot model) | no | 19.008 | 0.255 | 9 | reference | — | 100/100 | 1.00 | 9.5 | 0.28 | 0 | 84.1 | 248 | -199.3 | 37.82 | 56.83 |
| 17 | + online battery physics (`physics`) | Planning (exact bot model) | no | 19.008 | 0.255 | 10 | +0.00% ±0.00 | 0/0 | 100/100 | 1.00 | 9.5 | 0.28 | 0 | 25.5 | 166 | -199.3 | 37.82 | 56.83 |
| 18 | + market residual (`residual`) | Planning (exact bot model) | no | 19.008 | 0.255 | 11 | +0.00% ±0.00 | 0/0 | 100/100 | 1.00 | 9.5 | 0.28 | 0 | 25.0 | 133 | -199.3 | 37.82 | 56.83 |
| 19 | + noisy scenarios (`noisy-scenarios`) | Planning (exact bot model) | no | 19.056 | 0.264 | 5 | +0.46% ±1.38 | 43/57 | 100/100 | 1.00 | 9.9 | 0.29 | 0 | 46.9 | 188 | -200.1 | 37.77 | 56.83 |
| 20 | + probabilistic cutoffs (`prob-cutoff`) | Planning (exact bot model) | no | 19.063 | 0.266 | 4 | +0.49% ±1.37 | 43/57 | 100/100 | 1.00 | 9.9 | 0.29 | 0 | 50.3 | 237 | -200.2 | 37.76 | 56.82 |
| 21 | + CVaR risk (`cvar`) | Planning (exact bot model) | no | 19.101 | 0.266 | 3 | +0.66% ±1.26 | 49/51 | 100/100 | 1.00 | 9.4 | 0.23 | 0 | 45.3 | 169 | -200.1 | 37.72 | 56.82 |
| 22 | + dynamic horizon (`dynamic-horizon`) | Planning (exact bot model) | no | 19.122 | 0.264 | 2 | +0.76% ±1.20 | 53/47 | 100/100 | 1.00 | 9.5 | 0.19 | 0 | 44.8 | 161 | -200.3 | 37.67 | 56.80 |
| 23 | + strategy modes (`modes`) | Planning (exact bot model) | no | 19.130 | 0.280 | 1 | +0.82% ±1.35 | 48/52 | 100/100 | 1.00 | 9.2 | 0.26 | 0 | 42.2 | 174 | -200.1 | 37.60 | 56.73 |
| 24 | Adaptive cycle-aware (`adaptive-cycle-aware`) | Planning (exact bot model) | no | 19.008 | 0.255 | 7 | +0.00% ±0.00 | 1/3 | 100/100 | 1.00 | 9.5 | 0.28 | 0 | 26.0 | 97.5 | -199.3 | 37.82 | 56.83 |
| 25 | Identified market: linear (`identified-linear`) | Planning (identified market) | yes | 17.734 | 0.247 | 22 | -6.57% ±1.03 | 8/92 | 100/100 | 1.00 | 8.6 | 1.18 | 0 | 24.2 | 144 | -194.9 | 39.04 | 56.77 |
| 26 | Identified market: logit demand (`identified-logit`) | Planning (identified market) | yes | 18.194 | 0.291 | 21 | -4.20% ±1.13 | 22/78 | 100/100 | 1.00 | 8.6 | 1.30 | 0 | 42.8 | 127 | -198.4 | 38.46 | 56.66 |
| 27 | Identified market: rational demand (`identified-structural`) | Planning (identified market) | yes | 18.541 | 0.288 | 18 | -2.36% ±1.16 | 28/72 | 100/100 | 1.00 | 8.8 | 0.85 | 0 | 58.9 | 180 | -198.1 | 38.21 | 56.75 |
| 28 | Identified market: robust crossings (`identified-robust`) | Planning (identified market) | yes | 18.911 | 0.281 | 13 | -0.41% ±1.12 | 45/55 | 100/100 | 1.00 | 9.6 | 0.81 | 0 | 56.5 | 215 | -199.0 | 37.91 | 56.82 |
| 29 | UCB over energy prices (`ucb-energy`) | Machine learning | yes | 17.012 | 0.352 | 28 | -10.54% ±1.30 | 1/99 | 91/100 | 1.11 | 3.2 | 0.49 | 0 | 1.9 | 15.2 | -204.6 | 37.85 | 54.86 |
| 30 | Learned value (ridge), greedy (`ridge-value`) | Machine learning | no | 16.740 | 0.340 | 30 | -11.94% ±1.33 | 2/98 | 76/100 | 1.38 | 10.8 | 0.09 | 0 | 2.5 | 26.6 | -191.6 | 40.44 | 57.18 |
| 31 | Planner + ridge terminal (4 rounds) (`ridge-terminal-4`) | Machine learning | no | 18.217 | 0.273 | 20 | -4.01% ±1.24 | 25/75 | 98/100 | 1.02 | 10.2 | 0.48 | 0 | 15.6 | 52.9 | -195.1 | 38.74 | 56.96 |
| 32 | Planner + ridge terminal (6 rounds) (`ridge-terminal-6`) | Machine learning | no | 18.423 | 0.261 | 19 | -2.88% ±1.33 | 31/69 | 100/100 | 1.00 | 10.0 | 0.31 | 0 | 24.5 | 79.9 | -195.0 | 38.48 | 56.90 |
| 33 | Planner + CatBoost terminal (`catboost-terminal`) | Machine learning | no | 18.774 | 0.268 | 17 | -0.98% ±1.50 | 37/63 | 100/100 | 1.00 | 8.8 | 0.58 | 0 | 36.2 | 134 | -200.0 | 37.75 | 56.53 |
| 34 | LinUCB mode selector (`linucb-modes`) | Machine learning | no | 18.984 | 0.229 | 12 | +0.08% ±1.15 | 44/56 | 100/100 | 1.00 | 8.9 | 0.17 | 0 | 22.1 | 114 | -197.5 | 37.84 | 56.83 |
| 35 | Bayesian rival archetypes (`archetype-learning`) | Machine learning | no | 19.008 | 0.255 | 8 | +0.00% ±0.00 | 1/3 | 100/100 | 1.00 | 9.5 | 0.28 | 0 | 23.6 | 176 | -199.3 | 37.82 | 56.83 |
| 36 | Learned candidate shortlist (`learned-shortlist`) | Machine learning | no | 18.800 | 0.263 | 15 | -1.01% ±0.90 | 38/62 | 100/100 | 1.00 | 7.9 | 0.00 | 0 | 19.9 | 89.4 | -198.2 | 37.95 | 56.75 |

Log social welfare is the arena's Σ_i log u_i summed over rounds for the 4-node market; welfare is the sum of all four final scores. Δ is the mean per-seed relative gain with a normal 95% interval; W/L counts seeds with a strictly higher/lower score.

Times are wall-clock milliseconds per decision measured inside the run (4 parallel workers), so they include contention; they are comparable across agents, not portable.
