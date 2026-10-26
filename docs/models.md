# Trained models

Four entries of the machine-learning family use parameters fitted offline.
The fitted models ship inside the package as exported files, in
`swarmbench/strategies/`. Nothing is trained when SwarmBench runs, and no
machine-learning library is imported: inference is plain standard-library
Python, so PyYAML stays the only runtime dependency. NumPy and CatBoost are
needed only to [train the models again](#training-the-models).

## What ships

| File | Model | Used by | Trained on |
|---|---|---|---|
| `value_model.json` | ridge regression of the remaining score on 43 public-state features | `ridge-value`, `ridge-terminal-4`, `ridge-terminal-6` | 5,900 states from 100 episodes of `lookahead` (seeds 4001–4100) |
| `catboost_value_model.py` | CatBoost: 265 symmetric trees of depth 6, same features and target, exported to Python | `catboost-terminal` | the same 5,900 states |
| `catboost_value_meta.json` | the CatBoost training record: grid, validation errors, export parity | (documentation only) | |
| `bandit_prior.json` | LinUCB statistics (`A`, `b`) per mode, 9-dimensional context | `linucb-modes` | 400 episodes of `linucb-modes` (seeds 50001–50400), 18,531 pulls |
| `shortlist_model.json` | logistic regression on 15 one-step features of a candidate bid | `learned-shortlist` | 5,514 decisions of `archetype-learning` (seeds 52001–52120) |

- **The models are frozen.** No file is written during a run. `linucb-modes`
  keeps learning within an episode, starting from its own copy of the prior;
  `ucb-energy` and `archetype-learning` learn online only and use no file.
- **The training seeds are disjoint** from the development seeds and from the
  evaluation seeds of the stored results (70001–70100).
- **The files are the ones measured.** They are byte for byte the files the
  stored results were produced with. Changing one changes those entries'
  scores, and `swarmbench --reproduce` reports the difference.
- **Without its file**, an entry still runs: `ridge-value` and the
  `ridge-terminal` planners fall back to `kelly`, `catboost-terminal` to
  `lookahead`, `learned-shortlist` keeps every candidate (it then bids as
  `archetype-learning`), and `linucb-modes` starts with no prior.

## The models

### Value models (ridge and CatBoost)

Both predict the score a node will still collect in the episode from the
public state after a round: with $R = 60 - t$ rounds left after round $t$,
the label is the realized remaining score $y_t = \sum_{j=t+1}^{60} u_j$.
The 43 inputs (`planner.value_features`) are the rounds left, the node's own
battery and derived terms, its utility weights, mobility and service floors,
the named bots' batteries and admission indicators, the last clearing prices
and their interactions. The episode seed is never an input.

The corpus is 100 complete episodes of `lookahead` against the three bots,
59 labeled states each. The last 20 episodes (4081–4100) are held out whole
to choose the hyperparameters, which are then frozen, and the model is refit
on all 100 episodes.

| Model | Selection | Held-out RMSE (1,180 states) |
|---|---|---:|
| Ridge | $\alpha \in \{0.01, 0.1, 1, 10, 100\}$ on standardized features, intercept unpenalized; $\alpha = 0.1$ | 0.7525 |
| CatBoost | depth 3, 4 or 6 × `l2_leaf_reg` 3 or 10, at most 1,200 trees, learning rate 0.03, early stopping after 70; depth 6, `l2_leaf_reg` 10, 265 trees | **0.6286** |

`ridge-value` bids greedily on the immediate utility plus the ridge value of
the next state. `ridge-terminal-4`, `ridge-terminal-6` and
`catboost-terminal` plan as `lookahead` and add the learned value, clipped to
$[0, 1.5R]$, at the end of their rollouts instead of its battery heuristic.

### The CatBoost export

CatBoost 1.2.10 fitted the model, and `save_model(path, format="python")`
exported it: `catboost_value_model.py` holds the trees as plain lists and an
`apply_catboost_model` function, with no CatBoost import. Native CatBoost
compares features in float32, and the export prints the tree borders to nine
digits. `planner.load_catboost_model` therefore rounds the borders back to
float32, and `planner.catboost_value` rounds the inputs, so that values lying
exactly on a border fall on the same side as in CatBoost. The export then
matches the native model to $5 \times 10^{-10}$ on all 5,900 training states
and on 919 probes placed on the borders (`catboost_value_meta.json`).

### The LinUCB prior

`linucb-modes` does not choose bids: each round, a LinUCB bandit chooses the
planner's personality (conservative, balanced, aggressive or robust) from a
9-dimensional context (bias, own battery, weakest awake rival, progress,
market and battery forecast errors, share of unknown rivals, competition,
floor pressure). Its reward is the utility of the decision round and the next
two. One episode is too short to learn this, so the per-arm statistics are
warm-started from 400 training episodes, played with a doubled exploration
bonus by four learners, each over its own quarter of the seeds. The
statistics are sums, so the four learners merge exactly into one prior.

### The shortlist model

`learned-shortlist` is `archetype-learning` with a learned pruning step. For
every decision of `archetype-learning` on the training seeds, each candidate
bid that the rollouts evaluated is labeled 1 if they ranked it among the
three best. A logistic regression on 15 cheap one-step features of the
candidate (energy share, immediate reward relative to the best, batteries and
admissions after the round, the candidate's kind, progress) learns to predict
that label; it was fitted by Newton's method with a ridge penalty of 1. At run
time, only the 9 best-scored candidates, plus the best immediate one, reach
the rollouts. On 1,103 held-out decisions, a shortlist of 9 keeps 87% of the
planner's top three (80% with 7, 70% with 5).

## Training the models

The recipes below repeat each training procedure on SwarmBench's engine.
They need NumPy, and CatBoost for the CatBoost model:

```bash
pip install swarmbench numpy catboost
```

Each writes a file in the format of the shipped one. The scripts are in
[`docs/training/`](https://github.com/Indigma-Innovations/swarmbench/tree/main/docs/training)
in the repository. With the seeds shown (the original ones), each model takes
a few minutes.

The shipped files were fitted in the development harness the strategies were
first written in. Run on SwarmBench's engine with the original seeds, the
recipes reproduce them:

| Model | Retrained with these recipes |
|---|---|
| CatBoost | the same grid errors and 265 trees; `catboost_value_model.py` byte for byte |
| Ridge | the same features, $\alpha$ and validation errors; coefficients within $5 \times 10^{-13}$ |
| LinUCB prior | the same pulls per mode and training score; statistics within $2 \times 10^{-14}$ (relative) |
| Shortlist | the same decisions, rows and held-out recalls; coefficients within $10^{-12}$ (relative) |

The last-digit differences come from floating-point differences between the
environments (the originals were fitted on Windows, with another NumPy build,
and the shortlist with a pure-Python solver). The shipped files remain the
ones the stored results depend on.

### 1. The value corpus

```python title="generate_value_data.py"
--8<-- "docs/training/generate_value_data.py"
```

```bash
python generate_value_data.py 4001 100 value.jsonl     # 5,900 labeled states
```

### 2. The ridge value model

```python title="train_value.py"
--8<-- "docs/training/train_value.py"
```

```bash
python train_value.py value.jsonl value_model.json
```

### 3. The CatBoost value model

```python title="train_catboost.py"
--8<-- "docs/training/train_catboost.py"
```

```bash
python train_catboost.py value.jsonl catboost_value_model.py
```

### 4. The LinUCB prior

```python title="train_bandit.py"
--8<-- "docs/training/train_bandit.py"
```

```bash
python train_bandit.py 50001 400 bandit_prior.json
```

### 5. The shortlist model

```python title="train_shortlist.py"
--8<-- "docs/training/train_shortlist.py"
```

```bash
python train_shortlist.py 52001 120 shortlist_model.json
```

### Using a retrained model

The strategies read their files from the installed package directory,
`swarmbench/strategies/`, once per process. To run with a retrained model,
install SwarmBench from a clone in editable mode (`pip install -e .`, see
[installation](installation.md#from-source)), replace the file in
`src/swarmbench/strategies/`, and run the entries as usual. The scores of the
entries that use it will no longer match the stored results, so save such
runs under another name than `results/paper`.
