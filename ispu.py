"""Logika inti: data, pembuatan fitur, dan pemuatan model untuk prediksi ISPU H+1.

Fitur dibuat berdasarkan DAFTAR NAMA FITUR yang tersimpan di dalam file .joblib
(bundle["fitur"]), sehingga urutan dan nama kolom selalu sama dengan saat pelatihan.
"""
from __future__ import annotations

import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

BASE = Path(__file__).parent
POLUTAN = ["pm10", "so2", "co", "o3", "no2"]
KELAS = ["BAIK", "SEDANG", "TIDAK SEHAT"]
NAMA_POLUTAN = {"pm10": "PM10", "so2": "SO₂", "co": "CO", "o3": "O₃", "no2": "NO₂"}

MODEL_FILES = {
    "Random Forest": "model_random_forest.joblib",
    "Decision Tree": "model_decision_tree.joblib",
    "Logistic Regression": "model_logistic_regression.joblib",
}
DEMO_FILE = "demo_random_forest.joblib"

# Bulan musim hujan untuk fitur `musim_hujan` (asumsi: Nov–Apr, pola hujan Jakarta/BMKG).
# SAMAKAN dengan definisi di notebook pembuatan fitur jika berbeda.
MUSIM_HUJAN = {11, 12, 1, 2, 3, 4}

_HARI = {"hari", "hari_minggu", "hari_dalam_minggu", "dayofweek", "day_of_week", "weekday"}
_BULAN = {"bulan", "month"}


class FiturTidakDikenal(Exception):
    def __init__(self, names):
        self.names = list(names)
        super().__init__("Nama fitur belum dikenali: " + ", ".join(self.names[:10]))


# --------------------------------------------------------------------------- data
def load_data() -> pd.DataFrame:
    df = pd.read_excel(BASE / "data" / "data_bersih.xlsx", sheet_name="data_bersih")
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df.sort_values(["stasiun", "tanggal"]).reset_index(drop=True)


def kategori_dari_nilai(maks: float) -> str:
    """Perkiraan kategori dari sub-indeks tertinggi (3 kelas hasil penggabungan)."""
    if maks <= 50:
        return "BAIK"
    if maks <= 100:
        return "SEDANG"
    return "TIDAK SEHAT"


# ------------------------------------------------------------------------ fitur
def _stasiun_cocok(suffix: str, stasiun: str) -> bool:
    a, b = suffix.strip().lower(), stasiun.strip().lower()
    return a == b or b.startswith(a + " ") or a.startswith(b.split(" ")[0])


def _nilai_fitur(name, seri, t, stasiun, daftar_stasiun):
    """Nilai satu fitur. `seri[p]` = Series harian (indeks tanggal kalender) sampai t."""
    if name in POLUTAN:
        return seri[name].get(t, np.nan)
    m = re.fullmatch(r"(pm10|so2|co|o3|no2)_lag(\d+)", name)
    if m:
        return seri[m.group(1)].get(t - pd.Timedelta(days=int(m.group(2))), np.nan)
    m = re.fullmatch(r"(pm10|so2|co|o3|no2)_(?:ma|rata|mean)(\d+)", name)
    if m:
        k = int(m.group(2))
        w = seri[m.group(1)].loc[t - pd.Timedelta(days=k - 1): t]
        return w.mean() if w.notna().any() else np.nan
    if name in _BULAN:
        return t.month
    if name in _HARI:
        return t.dayofweek
    if name == "musim_hujan":
        return int(t.month in MUSIM_HUJAN)
    if name == "bulan_sin":
        return np.sin(2 * np.pi * t.month / 12)
    if name == "bulan_cos":
        return np.cos(2 * np.pi * t.month / 12)
    if name in ("is_weekend", "akhir_pekan"):
        return int(t.dayofweek >= 5)
    if name.startswith("stasiun_"):
        return int(_stasiun_cocok(name[len("stasiun_"):], stasiun))
    if name in ("stasiun", "stasiun_kode", "stasiun_enc"):
        return sorted(daftar_stasiun).index(stasiun)
    raise KeyError(name)


def cek_fitur(fitur) -> list[str]:
    """Daftar nama fitur yang belum dikenali oleh pembuat fitur (kosong = aman)."""
    kosong = {p: pd.Series(dtype=float) for p in POLUTAN}
    t = pd.Timestamp("2020-01-10")
    buruk = []
    for f in fitur:
        try:
            _nilai_fitur(f, kosong, t, "DKI1 (X)", ["DKI1 (X)"])
        except KeyError:
            buruk.append(f)
    return buruk


def siapkan_riwayat(riwayat: pd.DataFrame, t: pd.Timestamp, hari: int = 14):
    """Reindex ke kalender harian dan isi celah. Mengembalikan (seri, jumlah_diisi)."""
    idx = pd.date_range(t - pd.Timedelta(days=hari - 1), t)
    r = riwayat.set_index("tanggal").reindex(idx)
    seri, diisi = {}, 0
    for p in POLUTAN:
        s = r[p].astype(float)
        asli = s.copy()
        s = s.ffill().bfill()
        diisi += int(asli.isna().sum() - s.isna().sum()) if asli.isna().any() else 0
        seri[p] = s
    return seri, diisi


def bangun_fitur(riwayat, t, stasiun, fitur, daftar_stasiun, median_polutan=None):
    """Satu baris fitur (DataFrame 1×n) untuk prediksi H+1 dari tanggal t.

    riwayat: DataFrame kolom tanggal + POLUTAN (hanya satu stasiun, tanggal <= t).
    Mengembalikan (X, jumlah_nilai_diisi_otomatis).
    """
    t = pd.Timestamp(t).normalize()
    seri, diisi = siapkan_riwayat(riwayat, t)
    if median_polutan:
        for p in POLUTAN:
            if seri[p].isna().any():
                seri[p] = seri[p].fillna(median_polutan[p])
                diisi += 1
    buruk, nilai = [], {}
    for f in fitur:
        try:
            nilai[f] = _nilai_fitur(f, seri, t, stasiun, daftar_stasiun)
        except KeyError:
            buruk.append(f)
    if buruk:
        raise FiturTidakDikenal(buruk)
    return pd.DataFrame([nilai], columns=list(fitur)).astype(float), diisi


def bangun_fitur_massal(df: pd.DataFrame, fitur, daftar_stasiun) -> pd.DataFrame:
    """Versi vektor untuk seluruh data (dipakai melatih model demo dan uji konsistensi)."""
    keluar = []
    for st, g in df.groupby("stasiun"):
        g = g.set_index("tanggal")
        g = g.reindex(pd.date_range(g.index.min(), g.index.max()))
        g.index.name = "tanggal"
        kolom = {"tanggal": g.index, "stasiun": st}
        for f in fitur:
            if f in POLUTAN:
                kolom[f] = g[f].values
                continue
            m = re.fullmatch(r"(pm10|so2|co|o3|no2)_lag(\d+)", f)
            if m:
                kolom[f] = g[m.group(1)].shift(int(m.group(2))).values
                continue
            m = re.fullmatch(r"(pm10|so2|co|o3|no2)_(?:ma|rata|mean)(\d+)", f)
            if m:
                kolom[f] = g[m.group(1)].rolling(int(m.group(2)), min_periods=1).mean().values
                continue
            if f in _BULAN:
                kolom[f] = g.index.month.values
            elif f in _HARI:
                kolom[f] = g.index.dayofweek.values
            elif f == "musim_hujan":
                kolom[f] = g.index.month.isin(list(MUSIM_HUJAN)).astype(int)
            elif f.startswith("stasiun_"):
                kolom[f] = int(_stasiun_cocok(f[len("stasiun_"):], st))
            else:
                raise FiturTidakDikenal([f])
        k = pd.DataFrame(kolom)
        k["kategori"] = g["kategori"].values
        keluar.append(k)
    return pd.concat(keluar, ignore_index=True)


# ------------------------------------------------------------------------ model
def muat_model(nama: str):
    """Muat bundle {'model','fitur','kelas'}. Mengembalikan (bundle, is_demo) atau (None, False)."""
    p = BASE / "models" / MODEL_FILES[nama]
    if p.exists():
        return joblib.load(p), False
    if nama == "Random Forest":
        d = BASE / "models" / DEMO_FILE
        if d.exists():
            return joblib.load(d), True
    return None, False


def model_tersedia() -> dict:
    out = {}
    for n in MODEL_FILES:
        if (BASE / "models" / MODEL_FILES[n]).exists():
            out[n] = "asli"
    if "Random Forest" not in out and (BASE / "models" / DEMO_FILE).exists():
        out["Random Forest"] = "demo"
    return out


def prediksi_proba(bundle, X: pd.DataFrame) -> dict:
    proba = bundle["model"].predict_proba(X[bundle["fitur"]])[0]
    peta = dict(zip(bundle["kelas"], proba))
    return {k: float(peta.get(k, 0.0)) for k in KELAS}