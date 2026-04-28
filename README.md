# Cross-Validation Pitfalls in Motor-Imagery BCI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code: Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Reproducible](https://img.shields.io/badge/reproducible-yes-brightgreen)](#reproduce)
[![Dataset: BNCI2014-001](https://img.shields.io/badge/dataset-BNCI2014--001-informational)](https://moabb.neurotechx.com/docs/generated/moabb.datasets.BNCI2014_001.html)
[![DOI](https://img.shields.io/badge/DOI-pending--zenodo-blue)](#citation)

Reproducibility bundle for the manuscript

> **How Cross-Validation Choice Inflates Decoding Accuracy in Motor-Imagery EEG
> Brain–Computer Interfaces: A Quantitative Audit on BNCI2014-001 with a
> Reproducibility Checklist.**
>
> Anna Sokolova (Southern Federal University, Rostov-on-Don, Russia).
> ORCID: <https://orcid.org/0009-0000-5733-9994> · Contact: ansokolova@sfedu.ru.

The repository quantifies how four common validation protocols (random 5-fold,
within-session, cross-session, leave-one-subject-out) and one common
preprocessing mistake (random k-fold over overlapping sliding windows) inflate
or deflate the reported accuracy on the public BNCI2014-001 motor-imagery
dataset (9 subjects, 4 classes).

All numbers, tables, and figures in the paper are produced by a single
deterministic script — see [Reproduce](#reproduce).

---

## TL;DR — Key findings

| Protocol | Accuracy (mean ± SD over 9 subjects) |
|---|---|
| A. Random 5-fold, mixed sessions | **0.588 ± 0.133** |
| B. Within-session 5-fold         | **0.604 ± 0.140** |
| C. Cross-session (train→test)    | **0.577 ± 0.122** |
| D. Leave-One-Subject-Out (LOSO)  | **0.316 ± 0.093** |

- A vs B vs C: not statistically distinguishable (paired Wilcoxon, Holm-corrected `p > 0.99`).
- A or C vs D (LOSO): drop of ~0.26, `p_holm = 0.0195`.
- Random k-fold over overlapping sliding windows (no trial grouping) inflates
  accuracy by **+3.7 ± 2.7 pp** vs `GroupKFold` keyed on the source trial id
  (paired Wilcoxon `p = 0.0039`; the inflation direction is consistent across
  all 9 subjects).

See [`results/`](results/) for the raw CSVs and [`figures/`](figures/) for the plots.

---

## Repository layout

```
.
├── code/
│   └── run_analysis.py        # single-file deterministic pipeline
├── results/
│   ├── results_per_subject.csv
│   ├── results_summary.csv
│   ├── stat_tests.csv
│   └── window_leakage_results.csv
├── figures/
│   ├── fig1_protocols.png
│   ├── fig2_window_leakage.png
│   └── fig3_heatmap.png
├── paper/
│   ├── paper_BCI_validation_methodology_EN_2026.docx   # manuscript (English)
│   └── references_annotated.docx                       # 16 annotated references (English)
├── requirements.txt
├── environment.yml
├── CITATION.cff
├── LICENSE                    # code: MIT
├── LICENSE-CC-BY-4.0          # paper / figures / derived data: CC BY 4.0
└── README.md
```

---

## Reproduce

The pipeline downloads BNCI2014-001 via [MOABB](https://github.com/NeuroTechX/moabb)
on first run (~390 MB into `~/mne_data/`), trains an OAS-shrunk Riemannian MDM
classifier for each subject under each protocol, and writes all CSVs and PNGs
back into `results/` and `figures/`.

### Option 1 — pip / venv

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python code/run_analysis.py
```

Runtime is roughly **15–30 minutes** on a modern laptop CPU; no GPU required.

### Option 2 — conda

```bash
conda env create -f environment.yml
conda activate bci-validation
python code/run_analysis.py
```

### Determinism

The random seed is fixed (`random_state=42`) for every `StratifiedKFold`.
Riemannian MDM with OAS covariances has no stochastic components. Re-running
on the same machine reproduces the CSVs in `results/` bit-for-bit; minor
floating-point drift across BLAS implementations is possible but does not
affect any reported conclusion.

---

## Methods at a glance

- **Dataset**: BNCI2014-001 (9 subjects, 2 sessions of 288 trials each, 22 EEG
  channels at 250 Hz, 4 motor-imagery classes).
- **Preprocessing**: MOABB `MotorImagery(n_classes=4, fmin=8, fmax=32)` —
  bandpass 8–32 Hz, default trial epoching.
- **Features / Classifier**: OAS-shrunk sample covariance + Riemannian Minimum
  Distance to Mean (`pyriemann.classification.MDM`).
- **Protocols A–D**: see paper §3 / `code/run_analysis.py`.
- **Window-leakage experiment**: 2 s windows with 0.67 s stride per trial,
  compared between `StratifiedKFold` (leaky) and `GroupKFold` keyed on the
  source trial id (correct).
- **Statistics**: paired Wilcoxon signed-rank, two-sided, with Holm correction
  for the family of 5 protocol comparisons; window-leakage uses a separate
  paired Wilcoxon over the 9 subjects.

---

## Citation

If you use this code or these figures, please cite the paper and this
repository (see [`CITATION.cff`](CITATION.cff) — GitHub renders a "Cite this
repository" button from it).

A Zenodo DOI will be issued for the tagged release (`v2.0.0`); once it is
minted, replace the placeholder in [`CITATION.cff`](CITATION.cff) and update
the badge above.

BibTeX (manuscript):

```bibtex
@unpublished{sokolova_bci_validation_2026,
  author = {Sokolova, Anna},
  title  = {How Cross-Validation Choice Inflates Decoding Accuracy in
            Motor-Imagery EEG Brain--Computer Interfaces:
            A Quantitative Audit on BNCI2014-001 with a Reproducibility Checklist},
  year   = {2026},
  note   = {Manuscript and reproducibility code:
            \url{ttps://github.com/ZyntZ/bci-cv-methodology.git}}
}
```

Please also cite the underlying dataset and tooling:

- Tangermann et al., *Review of the BCI Competition IV*, Front. Neurosci., 2012 (BNCI2014-001).
- Jayaram & Barachant, *MOABB: trustworthy algorithm benchmarking for BCIs*, JNE, 2018.
- Barachant et al., *pyRiemann*, <https://github.com/pyRiemann/pyRiemann>.

---

## License

- **Code** (`code/`, scripts, configs): [MIT](LICENSE).
- **Paper, figures, derived CSVs** (`paper/`, `figures/`, `results/`):
  [CC BY 4.0](LICENSE-CC-BY-4.0).

---

## Contributing

Issues and pull requests are welcome. Useful directions:

- additional MOABB datasets (BNCI2014-004, Cho2017, …)
- additional pipelines (CSP+LDA, EEGNet)
- bootstrap / permutation CIs on the protocol gaps

Please open an issue first for substantive changes so we can discuss scope.
