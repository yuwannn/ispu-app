"""Cek apakah file model asli cocok dengan pembuat fitur aplikasi.

Jalankan:  python cek_model.py [models/model_random_forest.joblib]
"""
import sys

import joblib
import sklearn

import ispu

path = sys.argv[1] if len(sys.argv) > 1 else str(ispu.BASE / "models" / "model_random_forest.joblib")
b = joblib.load(path)
print("scikit-learn terpasang:", sklearn.__version__)
print("Jumlah fitur di model :", len(b["fitur"]))
print("Kelas                 :", b["kelas"])
print("Daftar fitur          :", b["fitur"])
buruk = ispu.cek_fitur(b["fitur"])
print("\nFitur belum dikenali  :", buruk if buruk else "tidak ada (aman)")
