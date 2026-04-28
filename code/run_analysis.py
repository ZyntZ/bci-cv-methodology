"""
Reproducibility script for the article
"How Cross-Validation Choice Inflates Decoding Accuracy in Motor-Imagery EEG
Brain-Computer Interfaces: A Quantitative Audit on BNCI2014-001 with a
Reproducibility Checklist."

Author: Anna Sokolova (Southern Federal University, Rostov-on-Don, Russia).
ORCID: https://orcid.org/0009-0000-5733-9994
Contact: ansokolova@sfedu.ru

Run from the repository root:
    python code/run_analysis.py

Outputs (relative to the repo root, auto-detected):
    results/results_per_subject.csv
    results/results_summary.csv
    results/stat_tests.csv
    results/window_leakage_results.csv
    figures/fig1_protocols.png
    figures/fig2_window_leakage.png
    figures/fig3_heatmap.png

Requires: moabb, mne, pyriemann, scikit-learn, scipy, statsmodels, pandas, numpy, matplotlib
"""
import os, sys, warnings, logging
from pathlib import Path
warnings.filterwarnings("ignore")
logging.getLogger("mne").setLevel(logging.ERROR)

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests
from sklearn.model_selection import StratifiedKFold, GroupKFold
from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score
from sklearn.preprocessing import LabelEncoder
from pyriemann.estimation import Covariances
from pyriemann.classification import MDM
from moabb.datasets import BNCI2014_001
from moabb.paradigms import MotorImagery
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- Output directories ----------
HERE = Path(__file__).resolve().parent
REPO = HERE.parent if HERE.name == "code" else HERE
RESULTS = REPO / "results"
FIGS = REPO / "figures"
RESULTS.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

# ---------- Data ----------
ds = BNCI2014_001()
paradigm = MotorImagery(n_classes=4, fmin=8, fmax=32)
X, y, meta = paradigm.get_data(dataset=ds, subjects=ds.subject_list)
le = LabelEncoder().fit(y); ye = le.transform(y)


def fit_eval(Xtr, ytr, Xte, yte):
    cov = Covariances(estimator="oas")
    Ctr, Cte = cov.fit_transform(Xtr), cov.transform(Xte)
    mdm = MDM(metric=dict(mean="riemann", distance="riemann"))
    mdm.fit(Ctr, ytr); pred = mdm.predict(Cte)
    return dict(acc=accuracy_score(yte, pred),
                f1=f1_score(yte, pred, average="macro"),
                kappa=cohen_kappa_score(yte, pred))


# ---------- Protocol A: random 5-fold over both sessions ----------
records = []
for s in ds.subject_list:
    msk = meta["subject"] == s
    Xs, ys = X[msk], ye[msk]
    skf = StratifiedKFold(5, shuffle=True, random_state=42)
    accs, f1s, kps = [], [], []
    for tr, te in skf.split(Xs, ys):
        r = fit_eval(Xs[tr], ys[tr], Xs[te], ys[te])
        accs.append(r["acc"]); f1s.append(r["f1"]); kps.append(r["kappa"])
    records.append(dict(subject=s, protocol="A_random5fold_mixed_sessions",
                        acc=np.mean(accs), acc_sd=np.std(accs),
                        f1=np.mean(f1s), kappa=np.mean(kps)))

# ---------- Protocol B: within-session 5-fold ----------
for s in ds.subject_list:
    msk = (meta["subject"] == s) & (meta["session"] == "0train")
    Xs, ys = X[msk], ye[msk]
    skf = StratifiedKFold(5, shuffle=True, random_state=42)
    accs, f1s, kps = [], [], []
    for tr, te in skf.split(Xs, ys):
        r = fit_eval(Xs[tr], ys[tr], Xs[te], ys[te])
        accs.append(r["acc"]); f1s.append(r["f1"]); kps.append(r["kappa"])
    records.append(dict(subject=s, protocol="B_within_session_5fold",
                        acc=np.mean(accs), acc_sd=np.std(accs),
                        f1=np.mean(f1s), kappa=np.mean(kps)))

# ---------- Protocol C: cross-session ----------
for s in ds.subject_list:
    mtr = (meta["subject"] == s) & (meta["session"] == "0train")
    mte = (meta["subject"] == s) & (meta["session"] == "1test")
    r = fit_eval(X[mtr], ye[mtr], X[mte], ye[mte])
    records.append(dict(subject=s, protocol="C_cross_session",
                        acc=r["acc"], acc_sd=np.nan,
                        f1=r["f1"], kappa=r["kappa"]))

# ---------- Protocol D: leave-one-subject-out ----------
for s in ds.subject_list:
    mte = meta["subject"] == s
    mtr = ~mte
    r = fit_eval(X[mtr], ye[mtr], X[mte], ye[mte])
    records.append(dict(subject=s, protocol="D_LOSO",
                        acc=r["acc"], acc_sd=np.nan,
                        f1=r["f1"], kappa=r["kappa"]))

df = pd.DataFrame(records)
df.to_csv(RESULTS / "results_per_subject.csv", index=False)
summary = (df.groupby("protocol")
             .agg(acc_mean=("acc", "mean"), acc_std=("acc", "std"),
                  f1_mean=("f1", "mean"), kappa_mean=("kappa", "mean"))
             .reset_index())
summary.to_csv(RESULTS / "results_summary.csv", index=False)

# ---------- Statistical tests (paired Wilcoxon + Holm) ----------
piv = df.pivot_table(index="subject", columns="protocol", values="acc")
pairs = [("A_random5fold_mixed_sessions", "C_cross_session"),
         ("B_within_session_5fold",       "C_cross_session"),
         ("A_random5fold_mixed_sessions", "D_LOSO"),
         ("C_cross_session",              "D_LOSO"),
         ("A_random5fold_mixed_sessions", "B_within_session_5fold")]
rows = []
for a, b in pairs:
    s, p = wilcoxon(piv[a], piv[b])
    rows.append(dict(pair=f"{a} vs {b}",
                     median_diff=float(np.median(piv[a] - piv[b])),
                     mean_diff=float(np.mean(piv[a] - piv[b])),
                     W=float(s), p=float(p), n=len(piv)))
sdf = pd.DataFrame(rows)
sdf["p_holm"] = multipletests(sdf["p"], method="holm")[1]
sdf.to_csv(RESULTS / "stat_tests.csv", index=False)

# ---------- Window-leakage experiment ----------
def make_windows(Xs, ys, win=500, stride=167):
    Xw, yw, src = [], [], []
    for i in range(Xs.shape[0]):
        for s_ in range(0, Xs.shape[2] - win + 1, stride):
            Xw.append(Xs[i, :, s_:s_ + win]); yw.append(ys[i]); src.append(i)
    return np.array(Xw), np.array(yw), np.array(src)


leaky = []
for s in ds.subject_list:
    msk = (meta["subject"] == s) & (meta["session"] == "0train")
    Xs, ys = X[msk], ye[msk]
    Xw, yw, src = make_windows(Xs, ys)
    skf = StratifiedKFold(5, shuffle=True, random_state=42)
    accs_l = [fit_eval(Xw[tr], yw[tr], Xw[te], yw[te])["acc"]
              for tr, te in skf.split(Xw, yw)]
    gkf = GroupKFold(5)
    accs_g = [fit_eval(Xw[tr], yw[tr], Xw[te], yw[te])["acc"]
              for tr, te in gkf.split(Xw, yw, groups=src)]
    leaky.append(dict(subject=s,
                      leaky_acc=np.mean(accs_l),
                      grouped_acc=np.mean(accs_g)))

ldf = pd.DataFrame(leaky)
ldf["leakage_inflation"] = ldf["leaky_acc"] - ldf["grouped_acc"]
ldf.to_csv(RESULTS / "window_leakage_results.csv", index=False)

# ---------- Console summary ----------
print(summary.round(3))
print(sdf.round(4))
print(ldf.round(3))
print("Wilcoxon leakage:", wilcoxon(ldf.leaky_acc, ldf.grouped_acc))
print(f"Wrote CSVs to {RESULTS}")
print(f"(Re-run a plotting step or use figures in {FIGS} for the paper figures.)")
