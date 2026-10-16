# -*- coding: utf-8 -*-
"""Portfolyo raporu icin risk gruplari, gelir etkisi ve grafik verileri."""
import json, os
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

VERI = r"C:/Users/USER/Documents/Codex/2026-10-16/bu/outputs/musteri-kaybi-projesi/data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
KLASOR = os.path.dirname(os.path.abspath(__file__))
TOHUM = 42

df = pd.read_csv(VERI)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].replace(r"^\s*$", pd.NA, regex=True), errors="coerce")
df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})
df = df.drop_duplicates(subset="customerID").reset_index(drop=True)

X = df.drop(columns=["customerID", "Churn"])
y = df["Churn"].astype(int)
sayisal = X.select_dtypes(include="number").columns.tolist()
kategorik = X.select_dtypes(exclude="number").columns.tolist()
onisle = ColumnTransformer([
    ("num", Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler())]), sayisal),
    ("cat", Pipeline([("i", SimpleImputer(strategy="most_frequent")),
                      ("o", OneHotEncoder(handle_unknown="ignore"))]), kategorik),
])
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=TOHUM, stratify=y)

lr = Pipeline([("prep", onisle), ("model", LogisticRegression(
    max_iter=2000, class_weight="balanced", random_state=TOHUM))]).fit(Xtr, ytr)
olas = lr.predict_proba(Xte)[:, 1]

cikti = {}

# --- 5 katli capraz dogrulama (tek bolunmeye guvenmemek icin)
print("--- 5 katli CV (ROC-AUC) ---")
kat = StratifiedKFold(n_splits=5, shuffle=True, random_state=TOHUM)
for ad, m in [("Lojistik regresyon", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=TOHUM)),
              ("Rastgele orman", RandomForestClassifier(n_estimators=350, min_samples_leaf=3,
                                                        class_weight="balanced", n_jobs=-1, random_state=TOHUM)),
              ("Extra Trees", ExtraTreesClassifier(n_estimators=350, min_samples_leaf=3,
                                                   class_weight="balanced", n_jobs=-1, random_state=TOHUM))]:
    s = cross_val_score(Pipeline([("prep", onisle), ("model", m)]), X, y,
                        cv=kat, scoring="roc_auc", n_jobs=-1)
    print("%-20s ort=%.4f  sd=%.4f  (%.4f - %.4f)" % (ad, s.mean(), s.std(), s.min(), s.max()))
    cikti.setdefault("cv", {})[ad] = {"ort": s.mean(), "sd": s.std(), "min": s.min(), "max": s.max()}

# --- Risk gruplari
test = Xte.copy()
test["gercek"] = yte.values
test["olasilik"] = olas
test["grup"] = pd.cut(olas, [-0.001, 0.30, 0.60, 1.001], labels=["Düşük", "Orta", "Yüksek"])

print("\n--- Risk gruplari (test seti, 1409 musteri) ---")
g = test.groupby("grup", observed=True).agg(
    musteri=("gercek", "size"), gercek_kayip=("gercek", "sum"),
    kayip_orani=("gercek", "mean"), ort_aylik=("MonthlyCharges", "mean"),
    ort_kidem=("tenure", "mean"))
g["aylik_gelir"] = test.groupby("grup", observed=True)["MonthlyCharges"].sum()
g["risk_altinda_gelir"] = test.groupby("grup", observed=True).apply(
    lambda d: (d["MonthlyCharges"] * d["gercek"]).sum(), include_groups=False)
print(g.to_string(float_format=lambda v: "%.2f" % v))
cikti["gruplar"] = {str(k): {kk: float(vv) for kk, vv in v.items()} for k, v in g.to_dict("index").items()}

print("\nToplam test aylik geliri: %.2f" % test["MonthlyCharges"].sum())
print("Kaybedilen musterilerin aylik geliri: %.2f (%%%.1f)" % (
    (test["MonthlyCharges"] * test["gercek"]).sum(),
    100 * (test["MonthlyCharges"] * test["gercek"]).sum() / test["MonthlyCharges"].sum()))

# --- ROC egrisi noktalari (grafik icin)
fpr, tpr, _ = roc_curve(yte, olas)
adim = max(1, len(fpr) // 60)
cikti["roc"] = {"fpr": [round(float(v), 4) for v in fpr[::adim]] + [1.0],
                "tpr": [round(float(v), 4) for v in tpr[::adim]] + [1.0],
                "auc": float(roc_auc_score(yte, olas))}

# --- Kumulatif kazanim egrisi (lift chart)
s = pd.DataFrame({"o": olas, "g": yte.values}).sort_values("o", ascending=False)
toplam = s.g.sum()
yuzdeler = list(range(0, 101, 5))
cikti["kazanim"] = [{"yuzde": p,
                     "yakalanan": round(100 * s.head(max(1, int(len(s) * p / 100))).g.sum() / toplam, 1) if p else 0.0}
                    for p in yuzdeler]
print("\n--- Kumulatif kazanim (ilk %%N -> yakalanan kayip %%) ---")
for k in cikti["kazanim"][::4]:
    print("  %%%-3d -> %%%.1f" % (k["yuzde"], k["yakalanan"]))

cm = confusion_matrix(yte, (olas > 0.5).astype(int))
cikti["karisiklik"] = cm.tolist()
cikti["ozet"] = {"musteri": int(len(df)), "degisken": int(df.shape[1]),
                 "kayip_orani": float(y.mean()), "egitim": int(len(Xtr)), "test": int(len(Xte)),
                 "taban_oran": float(max(yte.mean(), 1 - yte.mean()))}

json.dump(cikti, open(os.path.join(KLASOR, "rapor_verisi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nyazildi: rapor_verisi.json")
