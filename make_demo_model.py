"""Membuat model PENGGANTI (demo) agar aplikasi bisa dijalankan sebelum file
model_random_forest.joblib asli tersedia. Bukan model proyek yang sebenarnya.

Jalankan:  python make_demo_model.py
"""
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

import ispu

df = ispu.load_data()
stasiun = sorted(df["stasiun"].unique())
fitur = []
for p in ispu.POLUTAN:
    fitur += [p] + [f"{p}_lag{k}" for k in range(1, 8)] + [f"{p}_ma3", f"{p}_ma7"]
fitur += ["bulan", "hari_minggu"] + [f"stasiun_{s}" for s in stasiun]

F = ispu.bangun_fitur_massal(df, fitur, stasiun)
F["target_h1"] = F.groupby("stasiun")["kategori"].shift(-1)  # hari berikutnya (kalender)
F = F.dropna(subset=["target_h1", "kategori"] + ispu.POLUTAN).copy()
F[fitur] = F[fitur].fillna(F[fitur].median())

batas = pd.Timestamp("2021-04-26")  # sama dengan batas latih/uji di notebook
tr, te = F[F.tanggal <= batas], F[F.tanggal > batas]
rf = RandomForestClassifier(n_estimators=80, max_depth=10, min_samples_leaf=20,
                            class_weight="balanced", random_state=42, n_jobs=-1)
rf.fit(tr[fitur], tr["target_h1"])
from sklearn.metrics import f1_score
print("F1 macro uji (demo):", round(f1_score(te["target_h1"], rf.predict(te[fitur]), average="macro"), 4))
joblib.dump({"model": rf, "fitur": fitur, "kelas": list(rf.classes_)},
            ispu.BASE / "models" / ispu.DEMO_FILE, compress=3)
print("Tersimpan:", ispu.DEMO_FILE, "| jumlah fitur:", len(fitur))
