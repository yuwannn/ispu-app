# Prediksi Kategori ISPU H+1 DKI Jakarta (Streamlit)

## Menjalankan
```
pip install -r requirements.txt
streamlit run app.py
```

## Memasang model asli
1. Salin `model_random_forest.joblib` ke folder `models/` (opsional: `model_decision_tree.joblib`, `model_logistic_regression.joblib`).
2. Jalankan `python cek_model.py` — harus menampilkan "Fitur belum dikenali: tidak ada (aman)".
3. Samakan versi `scikit-learn` di `requirements.txt` dengan versi di komputer tempat model dilatih.
4. (Opsional) Salin `confusion_matrix_3_model.png` dan `fitur_penting_pohon.png` ke folder `assets/`.

Selama file asli belum ada, aplikasi memakai `models/demo_random_forest.joblib` (model pengganti, diberi peringatan di halaman Prediksi). Hapus file demo itu setelah model asli terpasang.

## Struktur
- `app.py` — antarmuka (Prediksi, Eksplorasi Data, Evaluasi Model, Tentang)
- `ispu.py` — pembuatan fitur dan pemuatan model (nama fitur dibaca dari bundle `.joblib`)
- `cek_model.py` — memeriksa kecocokan model asli dengan pembuat fitur
- `make_demo_model.py` — membuat model demo
- `data/` — `data_bersih.xlsx`, `perbandingan_model.csv`
