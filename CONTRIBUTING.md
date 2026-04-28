# Contributing

Thanks for considering a contribution!

## Ground rules

1. **Don't break reproducibility.** The CSVs in `results/` and the PNGs in
   `figures/` are reference outputs of `code/run_analysis.py` with
   `random_state=42`. If your change alters them, please justify it in the PR
   and update the CSVs/PNGs in the same commit.
2. **Keep the pipeline a single deterministic script.** Helper modules are
   fine, but `python code/run_analysis.py` should remain the one-command entry
   point.
3. **No fabricated numbers.** Every value reported in `results/`, in figures,
   and in the manuscript must come from a deterministic re-run of the code in
   this repo on a public dataset (currently BNCI2014-001 via MOABB).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python code/run_analysis.py
```

## Pull requests

- Open an issue first for substantive changes (new datasets, new pipelines,
  new statistical tests) so we can agree on scope.
- Keep PRs focused. One conceptual change per PR.
- Include a short note in the PR body listing every file in `results/` or
  `figures/` that changed and why.

## Code style

- Python 3.10+.
- Plain `numpy` / `scikit-learn` / `pyriemann`. Avoid heavy framework
  dependencies (PyTorch, TensorFlow) in the core pipeline.
- Use `random_state=42` everywhere.

## Reporting issues

Please include:

- Python version and OS.
- Output of `pip freeze | grep -Ei "mne|moabb|pyriemann|scikit-learn"`.
- The full traceback or the diff of the affected CSV.
