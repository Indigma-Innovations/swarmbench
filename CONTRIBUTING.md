# Contributing

Thanks for your interest in SwarmBench. Bug reports, new agents, new
reference points and documentation fixes are all welcome.

## Development setup

```bash
git clone https://github.com/Indigma-Innovations/swarmbench
cd swarmbench
uv sync --all-extras          # or: python -m venv .venv && pip install -e ".[dev,report,analysis,docs]"
uv run pytest                 # the full suite, including the stored-results checks
uv run ruff check .
uv run mkdocs serve           # the documentation at http://127.0.0.1:8000
```

## Ground rules

- **Behaviour is frozen.** The stored results in `results/paper` must keep
  reproducing bit for bit. Any change to the arena engine
  (`src/swarmbench/arena`), the bots (`src/swarmbench/bots.py`), the built-in
  strategies (`src/swarmbench/strategies`) or the engine loop
  (`src/swarmbench/engine.py`) must leave every score identical. Check with
  `uv run pytest` and `uv run swarmbench --reproduce --mode solo --seeds 3`.
- The strategy modules are kept as they were measured; ruff only checks them
  for real errors. Do not restyle them.
- New agents go through the public API (`swarmbench.Agent`,
  `swarmbench.register_agent`). A new built-in entry needs a family, a
  position in the idea order, an honest **realistic** flag, and a
  description; add it to `_BUILTIN` in `src/swarmbench/catalog.py`.
- Keep the core install light: the only runtime dependency is PyYAML.
  Anything else goes into an optional extra.
- Add a test for every bug fix and every new feature; add a line to
  `CHANGELOG.md`.

## Pull requests

1. Fork the repository and create a branch.
2. Make your change with tests and documentation.
3. Run `uv run ruff check .`, `uv run pytest` and `uv run mkdocs build --strict`.
4. Open a pull request describing what changed and why.

By contributing you agree that your contributions are licensed under the
Apache License 2.0.
