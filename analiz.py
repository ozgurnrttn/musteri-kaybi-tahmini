# -*- coding: utf-8 -*-
"""IBM Telco churn verisi: blog yazisi icin gercek sayilari uretir."""
import json, os
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix,
                             average_precision_score, brier_score_loss)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

VERI = r"C:/Users/USER/Documents/Codex/2026-10-16/bu/outputs/musteri-kaybi-projesi/data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
KLASOR = os.path.dirname(os.path.abspath(__file__))
TOHUM = 42

ham = pd.read_csv(VERI)
df = ham.copy()
df["TotalCharges"] = pd.to_numeric(
    df["TotalCharges"].replace(r"^\s*$", pd.NA, regex=True), errors="coerce")
df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})
df = df.drop_duplicates(subset="customerID").reset_index(drop=True)

print("########## 1. VERI ##########")
print("satir:", len(ham), " tekil musteri:", len(df),
      " yinelenen:", len(ham) - len(df))
print("sutun:", df.shape[1])
print("TotalCharges eksik:", int(df["TotalCharges"].isna().sum()))
print("eksik olanlarin tenure degerleri:",
      sorted(df.loc[df["TotalCharges"].isna(), "tenure"].unique().tolist()))
print("kayip orani: %.4f" % df["Churn"].mean())
print("kalan: %d  ayrilan: %d" % ((df.Churn == 0).sum(), (df.Churn == 1).sum()))

print("\n--- Sozlesme turune gore ---")
t = df.groupby("Contract")["Churn"].agg(musteri="size", oran="mean")
print(t.assign(oran=lambda d: (d.oran * 100).round(1)).to_string())
print("\n--- Internet hizmetine gore ---")
t = df.groupby("InternetService")["Churn"].agg(musteri="size", oran="mean")
print(t.assign(oran=lambda d: (d.oran * 100).round(1)).to_string())
print("\n--- Odeme yontemine gore ---")
t = df.groupby("PaymentMethod")["Churn"].agg(musteri="size", oran="mean")
print(t.assign(oran=lambda d: (d.oran * 100).round(1)).sort_values("oran", ascending=False).to_string())
print("\n--- Kidem dilimlerine gore ---")
kesim = pd.cut(df.tenure, [-1, 6, 12, 24, 48, 72],
               labels=["0-6 ay", "7-12 ay", "13-24 ay", "25-48 ay", "49-72 ay"])
t = df.groupby(kesim, observed=True)["Churn"].agg(musteri="size", oran="mean")
print(t.assign(oran=lambda d: (d.oran * 100).round(1)).to_string())
print("\n--- Teknik destek ---")
t = df.groupby("TechSupport")["Churn"].agg(musteri="size", oran="mean")
print(t.assign(oran=lambda d: (d.oran * 100).round(1)).to_string())

X = df.drop(columns=["customerID", "Churn"])
y = df["Churn"].astype(int)
sayisal = X.select_dtypes(include="number").columns.tolist()
kategorik = X.select_dtypes(exclude="number").columns.tolist()
print("\nsayisal degisken:", sayisal)
print("kategorik degisken sayisi:", len(kategorik))

onisle = ColumnTransformer([
    ("num", Pipeline([("i", SimpleImputer(strategy="median")),
                      ("s", StandardScaler())]), sayisal),
    ("cat", Pipeline([("i", SimpleImputer(strategy="most_frequent")),
                      ("o", OneHotEncoder(handle_unknown="ignore"))]), kategorik),
])
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2,
                                      random_state=TOHUM, stratify=y)
print("egitim:", len(Xtr), " test:", len(Xte),
      " test kayip orani: %.4f" % yte.mean())

modeller = {
    "Lojistik regresyon": LogisticRegression(max_iter=2000, class_weight="balanced",
                                             random_state=TOHUM),
    "Rastgele orman": RandomForestClassifier(n_estimators=350, min_samples_leaf=3,
                                             class_weight="balanced", n_jobs=-1,
                                             random_state=TOHUM),
    "Extra Trees": ExtraTreesClassifier(n_estimators=350, min_samples_leaf=3,
                                        class_weight="balanced", n_jobs=-1,
                                        random_state=TOHUM),
}
print("\n########## 2. MODELLER ##########")
print("%-20s %8s %8s %8s %8s %8s %8s %8s" %
      ("Model", "Acc", "Precision", "Recall", "F1", "ROC-AUC", "PR-AUC", "Brier"))
kurulu, tahminler = {}, {}
for ad, m in modeller.items():
    p = Pipeline([("prep", onisle), ("model", m)]).fit(Xtr, ytr)
    tah, olas = p.predict(Xte), p.predict_proba(Xte)[:, 1]
    kurulu[ad], tahminler[ad] = p, (tah, olas)
    print("%-20s %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f" % (
        ad, accuracy_score(yte, tah), precision_score(yte, tah, zero_division=0),
        recall_score(yte, tah, zero_division=0), f1_score(yte, tah, zero_division=0),
        roc_auc_score(yte, olas), average_precision_score(yte, olas),
        brier_score_loss(yte, olas)))

kazanan = max(kurulu, key=lambda a: roc_auc_score(yte, tahminler[a][1]))
print("\nen yuksek ROC-AUC:", kazanan)
tah, olas = tahminler[kazanan]
cm = confusion_matrix(yte, tah)
print("karisiklik matrisi (satir=gercek, sutun=tahmin):\n", cm)
print("taban oran (cogunluk sinifi): %.4f" % max(yte.mean(), 1 - yte.mean()))

print("\n--- Esik taramasi (%s) ---" % kazanan)
print("%6s %8s %10s %10s %8s %12s" % ("esik", "acc", "duyarlilik", "kesinlik", "F1", "hedeflenen"))
for e in [0.3, 0.4, 0.5, 0.6, 0.7]:
    pr = (olas > e).astype(int)
    print("%6.1f %8.4f %10.4f %10.4f %8.4f %12d" % (
        e, accuracy_score(yte, pr), recall_score(yte, pr, zero_division=0),
        precision_score(yte, pr, zero_division=0), f1_score(yte, pr, zero_division=0),
        int(pr.sum())))

print("\n--- Risk dilimlerinde gercek kayip orani (lift) ---")
s = pd.DataFrame({"olas": olas, "gercek": yte.values}).sort_values("olas", ascending=False)
n = len(s)
for pay in [0.05, 0.10, 0.20, 0.30, 0.50]:
    k = int(n * pay)
    dilim = s.head(k)
    print("  ilk %%%-3d (%3d musteri): kayip orani %.3f  yakalanan %3d / %d  (%%%.1f)  lift %.2fx" % (
        pay * 100, k, dilim.gercek.mean(), int(dilim.gercek.sum()),
        int(s.gercek.sum()), 100 * dilim.gercek.sum() / s.gercek.sum(),
        dilim.gercek.mean() / yte.mean()))

print("\n--- Permutation importance (ROC-AUC dususu, ilk 10) ---")
pi = permutation_importance(kurulu[kazanan], Xte, yte, n_repeats=8,
                            random_state=TOHUM, scoring="roc_auc", n_jobs=-1)
imp = (pd.DataFrame({"degisken": Xte.columns, "etki": pi.importances_mean,
                     "sd": pi.importances_std})
       .sort_values("etki", ascending=False).head(10))
print(imp.to_string(index=False, float_format=lambda v: "%.4f" % v))

lr = Pipeline([("prep", onisle), ("model", LogisticRegression(
    max_iter=2000, class_weight="balanced", random_state=TOHUM))]).fit(Xtr, ytr)
adlar = lr.named_steps["prep"].get_feature_names_out()
kat = pd.Series(lr.named_steps["model"].coef_[0], index=adlar)
print("\n--- Lojistik regresyon: en guclu 8 pozitif ve 8 negatif katsayi (odds orani) ---")
for ad, v in pd.concat([kat.nlargest(8), kat.nsmallest(8)]).items():
    print("  %-52s %+7.3f   OR=%5.2f" % (ad.split("__")[-1], v, np.exp(v)))
