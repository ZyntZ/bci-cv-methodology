# Changelog

All notable changes to this project will be documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-04-28

Author-attributed release prepared for Zenodo archival.

### Changed
- Repository now identifies the author: Anna Sokolova (Southern Federal
  University, Rostov-on-Don, Russia), ORCID
  [0009-0000-5733-9994](https://orcid.org/0009-0000-5733-9994), contact
  ansokolova@sfedu.ru. Updated `LICENSE`, `LICENSE-CC-BY-4.0`, `CITATION.cff`,
  `README.md`, and the manuscript title page accordingly.
- Manuscript and bibliography are English-only. The Russian-language
  manuscript and the Russian annotations of the reference list have been
  removed; `paper/references_annotated.docx` has been rewritten in English.
- Bumped to `v2.0.0` to mark the first version intended for citation via
  Zenodo (DOI to be minted on the tag).

### Removed
- `paper/paper_BCI_validation_methodology.docx` (Russian manuscript). The
  English manuscript `paper/paper_BCI_validation_methodology_EN_2026.docx`
  remains as the only archived version.

## [1.0.0] - 2026-02-14

Initial public release accompanying the manuscript.

### Added
- `code/run_analysis.py` — single-file deterministic pipeline reproducing
  all four cross-validation protocols (A–D) and the window-leakage experiment
  on BNCI2014-001 with `random_state=42`.
- `results/` — per-subject and summary CSVs, paired Wilcoxon + Holm test
  results, and the window-leakage table.
- `figures/` — Figures 1–3 of the manuscript at 300 dpi.
- `paper/` — manuscript and an annotated reference list.
- `requirements.txt`, `environment.yml`, `LICENSE` (MIT for code),
  `LICENSE-CC-BY-4.0` (paper/figures/derived data), `CITATION.cff`,
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, GitHub issue/PR templates and
  a lightweight CI workflow (syntax + import smoke test).
