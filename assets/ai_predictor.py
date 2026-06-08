"""
utils/ai_predictor.py
Prediksi prioritas tugas menggunakan scikit-learn pipeline (TF-IDF + Naive Bayes).
Dipanggil dari halaman Kanban saat pengguna menambah atau mengedit tugas.
"""

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


# ---------------------------------------------------------------------------
# Data latih — diperluas agar model lebih akurat
# Tambahkan contoh baru di sini kalau mau meningkatkan akurasi
# ---------------------------------------------------------------------------
_TRAINING_DATA = [
    # Tinggi
    ("perbaiki bug kritis login gagal error server",         "Tinggi"),
    ("deploy produksi deadline hari ini urgent",             "Tinggi"),
    ("keamanan data bocor celah kerentanan sistem",          "Tinggi"),
    ("server down crash tidak bisa diakses",                 "Tinggi"),
    ("hotfix perbaikan segera darurat produksi",             "Tinggi"),
    ("payment gagal transaksi error kritis",                 "Tinggi"),
    ("hapus data penting akun pelanggan rusak",              "Tinggi"),
    ("laporan keuangan audit besok pagi",                    "Tinggi"),
    ("fitur utama tidak berfungsi pelanggan komplain",       "Tinggi"),
    ("integrasi API gagal seluruh layanan terhenti",         "Tinggi"),

    # Sedang
    ("tambah fitur baru filter pencarian produk",            "Sedang"),
    ("perbarui tampilan halaman profil pengguna",            "Sedang"),
    ("optimasi query database lambat response",              "Sedang"),
    ("buat laporan bulanan penjualan",                       "Sedang"),
    ("refactor kode modul pembayaran",                       "Sedang"),
    ("tulis unit test untuk fungsi kalkulasi",               "Sedang"),
    ("review pull request teman sebelum merge",              "Sedang"),
    ("update dependensi library ke versi terbaru",           "Sedang"),
    ("dokumentasi API endpoint baru",                        "Sedang"),
    ("perbaiki tampilan responsif mobile tablet",            "Sedang"),

    # Rendah
    ("ubah warna tombol sesuai desain baru",                 "Rendah"),
    ("perbaiki typo teks halaman about",                     "Rendah"),
    ("tambah komentar pada kode lama",                       "Rendah"),
    ("rapikan format file konfigurasi",                      "Rendah"),
    ("ganti ikon sidebar menu navigasi",                     "Rendah"),
    ("perbarui readme dokumentasi proyek",                   "Rendah"),
    ("hapus console log debug dari kode",                    "Rendah"),
    ("rename variabel agar lebih deskriptif",                "Rendah"),
    ("tambah tooltip pada tombol aksi",                      "Rendah"),
    ("pindahkan file aset ke folder yang benar",             "Rendah"),
]

_texts  = [t for t, _ in _TRAINING_DATA]
_labels = [l for _, l in _TRAINING_DATA]

# ---------------------------------------------------------------------------
# Pipeline: TF-IDF (unigram + bigram) → Multinomial Naive Bayes
# ---------------------------------------------------------------------------
_pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        analyzer="word",
        token_pattern=r"(?u)\b\w+\b",
    )),
    ("clf", MultinomialNB(alpha=0.5)),
])

_pipeline.fit(_texts, _labels)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def predict_prioritas(judul: str, deskripsi: str = "") -> str:
    """
    Prediksi prioritas tugas berdasarkan judul dan deskripsi.

    Parameters
    ----------
    judul     : str  — nama/judul tugas
    deskripsi : str  — deskripsi opsional (dikombinasikan dengan judul)

    Returns
    -------
    str  — salah satu dari: "Tinggi", "Sedang", "Rendah"
    """
    if not judul and not deskripsi:
        return "Sedang"

    teks_gabungan = f"{judul} {deskripsi}".strip().lower()
    prediksi = _pipeline.predict([teks_gabungan])[0]
    return prediksi


def predict_dengan_confidence(judul: str, deskripsi: str = "") -> dict:
    """
    Sama seperti predict_prioritas, tapi juga mengembalikan skor kepercayaan
    untuk setiap kelas. Berguna untuk debugging atau menampilkan progress bar.

    Returns
    -------
    dict — {"prediksi": str, "skor": {"Tinggi": float, "Sedang": float, "Rendah": float}}
    """
    if not judul and not deskripsi:
        return {"prediksi": "Sedang", "skor": {"Tinggi": 0.0, "Sedang": 1.0, "Rendah": 0.0}}

    teks_gabungan = f"{judul} {deskripsi}".strip().lower()
    proba  = _pipeline.predict_proba([teks_gabungan])[0]
    kelas  = _pipeline.classes_

    skor = {k: round(float(p), 3) for k, p in zip(kelas, proba)}
    prediksi = max(skor, key=skor.get)

    return {"prediksi": prediksi, "skor": skor}


# ---------------------------------------------------------------------------
# Quick self-test (jalankan langsung: python utils/ai_predictor.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    contoh = [
        ("server down crash produksi",         ""),
        ("tambah fitur export laporan",        ""),
        ("perbaiki typo di halaman about",     ""),
        ("bug kritis payment gagal",           "transaksi pelanggan tidak bisa bayar"),
        ("update readme",                      "tambah komentar dokumentasi"),
    ]

    print(f"{'JUDUL':<40} {'DESKRIPSI':<35} {'PREDIKSI'}")
    print("-" * 90)
    for judul, desk in contoh:
        hasil = predict_dengan_confidence(judul, desk)
        print(f"{judul:<40} {desk:<35} {hasil['prediksi']}  {hasil['skor']}")
