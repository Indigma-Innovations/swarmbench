"""Nash averaging of a head-to-head tournament (Balduzzi et al., 2018).

The head-to-head win-rate matrix ``W`` (ties count 1/2, so ``W + W^T = 1`` off
the diagonal) defines a symmetric zero-sum meta-game with payoff
``A = W - 1/2``. Its maximum-entropy Nash equilibrium ``p*`` is unique; an
entry's Nash-averaged rating is ``(A p*)_i``: zero for entries in the support,
negative otherwise. Redundant copies of an entry cannot change it, unlike the
mean win rate.

Needs NumPy and SciPy (``pip install "swarmbench[analysis]"``)::

    swarmbench --metagame results/paper/head-to-head
"""

import json
from pathlib import Path

from .catalog import get_spec


def maxent_nash(A):
    """Maximum-entropy ``p`` with ``A^T p >= 0`` (the value of a symmetric zero-sum game is 0)."""
    import numpy as np
    from scipy.optimize import linprog, minimize

    A = np.asarray(A, dtype=float)
    n = len(A)
    # any equilibrium first (LP), as a feasible start
    res = linprog(np.zeros(n), A_ub=-A.T, b_ub=np.zeros(n), A_eq=np.ones((1, n)), b_eq=[1],
                  bounds=[(0, 1)] * n, method="highs")
    p0 = res.x
    tol = 1e-9

    def negent(p):
        q = np.clip(p, 1e-12, 1)
        return float(np.sum(q * np.log(q)))

    def grad(p):
        return np.log(np.clip(p, 1e-12, 1)) + 1

    out = minimize(negent, p0 + 1e-6, jac=grad, method="SLSQP", bounds=[(0, 1)] * n,
                   constraints=[{"type": "eq", "fun": lambda p: p.sum() - 1},
                                {"type": "ineq", "fun": lambda p: A.T @ p + tol}],
                   options={"maxiter": 2000, "ftol": 1e-12})
    p = np.clip(out.x if out.success else p0, 0, None)
    return p / p.sum()


def nash_averaging(keys: list[str], matrix: dict) -> dict:
    """Equilibrium support, Nash-averaged ratings and exploitability for ``keys``.

    ``matrix[a][b]`` is the share of a-versus-b matches that ``a`` won (the
    ``_matrix`` of a head-to-head summary)."""
    import numpy as np

    W = np.array([[0.5 if a == b else matrix[a][b] for b in keys] for a in keys])
    A = W - 0.5
    p = maxent_nash(A)
    rating = A @ p
    return {"keys": keys,
            "support": {k: round(float(x), 4) for k, x in zip(keys, p) if x > 1e-4},
            "rating": {k: round(float(r), 4) for k, r in zip(keys, rating)},
            "exploitability": round(float(max(A.T @ p) if len(keys) else 0.0), 6)}


def reference_ratings(support: dict, matrix: dict, references=("random", "clairvoyant")) -> dict:
    """Rate reference points against a roster equilibrium (roster ratings unchanged)."""
    return {ref: round(sum(p * (matrix[ref][k] - 0.5) for k, p in support.items()), 4)
            for ref in references if ref in matrix}


def metagame(folder: Path, references: Path | None = None) -> dict:
    """Nash averaging of a head-to-head results folder; writes ``metagame.json`` there.

    Rates every entry (``all``) and the realistic entries alone
    (``realistic``). With ``references`` (a head-to-head folder whose pairs
    involve reference points, e.g. ``head-to-head-references``), the
    reference points are rated against the roster's equilibrium."""
    folder = Path(folder)
    summary_path = folder / "summary.json"
    if not summary_path.exists():
        from .report import write_report
        write_report(folder)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    matrix = summary["_matrix"]
    spec = json.loads((folder / "spec.json").read_text(encoding="utf-8"))
    everyone = [k for k in spec["agents"] if k in matrix]
    realistic = [k for k in everyone if get_spec(k).realistic]
    out = {"all": nash_averaging(everyone, matrix), "realistic": nash_averaging(realistic, matrix)}
    if references is None and (folder.parent / f"{folder.name}-references" / "summary.json").exists():
        references = folder.parent / f"{folder.name}-references"
    if references is not None:
        ref_matrix = json.loads((Path(references) / "summary.json").read_text(encoding="utf-8"))["_matrix"]
        out["references"] = reference_ratings(out["all"]["support"], ref_matrix)
    (folder / "metagame.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out
