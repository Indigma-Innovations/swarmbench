# Changelog

All notable changes to SwarmBench are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
uses [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-10-26

First public release.

### Added

- `swarmbench` package (src layout) with the public API `Agent`,
  `Observation`, `FunctionAgent`, `register_agent`, `get_spec`, `resolve`,
  `Market`, `seat`, `play` and `run_mode`.
- The CoGNETs Swarm Arena game engine as `swarmbench.arena`, run in-process
  and deterministically, with the `graded` and `practice` scenarios.
- The three supplied baseline bots as `swarmbench.bots`.
- A catalog of 36 agents in five families (traditional rules, one-round
  optimization, planning with the exact bot model, planning with an
  identified market, machine learning), with a realistic flag, plus reference
  points (random split, oracle) and held-out opponents. Built-in strategies
  are addressed by their catalog key and run through `StrategyAgent`.
- Three modes: solo, head-to-head and all-together; held-out opponents,
  capacity scaling and focus pairs.
- Metrics and reports: score, rank, win rate, win rate over distinct opponents
  (duplicates of another participant count once), welfare, log social welfare,
  milliseconds per decision, paired gains; Nash averaging
  (`swarmbench --metagame`, `analysis` extra).
- The `swarmbench` command line, with `--reproduce` to re-run the stored
  results bit for bit (`--results DIR`, `--experiments`), `--publish` and
  `--import` for custom agents.
- Documentation of the trained models ([trained models](https://swarmbench.readthedocs.io/en/latest/models/)):
  the exported files that ship with the package, how each model was trained
  and validated, and scripts in `docs/training/` to train them again.
- Stored results of every experiment in `results/paper`, reproducible bit for
  bit on every supported Python version (3.12 and newer).
- Documentation (MkDocs Material), two notebooks, CI and PyPI publishing
  workflows.
