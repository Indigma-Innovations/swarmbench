# Installation

SwarmBench needs Python 3.12 or newer. Its only runtime dependency is PyYAML.

=== "pip"

    ```bash
    pip install swarmbench
    ```

=== "uv"

    ```bash
    uv add swarmbench          # in a uv project
    uv pip install swarmbench  # in any virtual environment
    ```

Check the install:

```bash
swarmbench --version
swarmbench --list
```

## Optional extras

| Extra | Installs | For |
|---|---|---|
| `report` | matplotlib | `figure.png` next to every report |
| `analysis` | SciPy (and NumPy) | Nash averaging (`swarmbench --metagame`) |
| `notebooks` | Jupyter, matplotlib | the notebooks in `notebooks/` |
| `docs` | MkDocs Material, mkdocstrings | building this documentation |
| `dev` | pytest, ruff, build | running the tests and the linter |

```bash
pip install "swarmbench[report,analysis]"
uv add "swarmbench[report]"
```

## From source

The repository also holds the stored results (`results/paper`), the
notebooks and the tests.

```bash
git clone https://github.com/Indigma-Innovations/swarmbench
cd swarmbench
uv sync --all-extras                    # creates .venv with every extra
uv run swarmbench --list
```

Without uv:

```bash
python -m venv .venv
source .venv/bin/activate               # Windows: .venv\Scripts\activate
pip install -e ".[dev,report,analysis]"
```

## Python versions and exact reproduction

SwarmBench supports Python 3.12 and newer, and the stored results reproduce
exactly on every supported version. The minimum is 3.12 because the
built-in `sum()` of floats uses compensated summation since that release;
the arena and the strategies sum floats everywhere, and the results were
produced on Python 3.13.

## Platforms

Episodes run in worker processes (`--workers`, default: all CPUs). On Linux
and macOS the workers are forked, so they inherit agents registered at run
time. On Windows, where only spawning is available, put custom agents in an
importable module and pass it with `--import`, or run with `--workers 1`
(see [writing your own agent](custom-agents.md#running-in-parallel)).
