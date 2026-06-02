# TaskAI

Aplikasi desktop manajemen proyek dan tugas berbasis PySide6 dengan dukungan AI untuk prediksi prioritas tugas dan ekspor laporan PDF/CSV.

## Anggota Kelompok

| Nama | NIM | Tugas |
|---|---|---|
| Toriq | F1D02310031 | Arsitektur aplikasi, manajemen proyek, database |
| Afif | F1D02310125 | Manajemen tugas, AI/ML prediksi prioritas |
| Izzul | F1D02410077 | Dashboard laporan, export PDF/CSV, styling |

## Fitur

- Manajemen proyek (CRUD) dengan QTableView
- Manajemen tugas dengan filter, search, dan sorting
- Prediksi prioritas tugas berbasis AI (Scikit-learn)
- Dashboard ringkasan dan statistik
- Export laporan ke CSV dan PDF (ber-watermark)
- Dark/Light mode
- Navigasi sidebar dengan QStackedWidget

## Cara Menjalankan

1. Install dependensi:
   ```
   pip install -r requirements.txt
   ```
2. Jalankan aplikasi:
   ```
   python main.py
   ```

## Teknologi

- PySide6 (GUI)
- SQLite (Database)
- Scikit-learn (AI/ML)
- ReportLab (Export PDF)
- Pandas (Data processing)
