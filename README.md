# TaskAI

Aplikasi desktop manajemen proyek dan tugas berbasis PySide6 dengan dukungan AI untuk prediksi prioritas tugas dan ekspor laporan PDF/CSV.

## Anggota Kelompok

| Nama | NIM | Tugas |
|------|-----|-------|
| Toriq | F1D02310031 | Arsitektur aplikasi, manajemen proyek, database |
| Afif | F1D02310125 | Manajemen tugas, Kanban Board, AI/ML prediksi prioritas |
| Izzul | F1D02410077 | Dashboard laporan, export PDF/CSV, dark mode, styling |

## Cara Menjalankan

1. Install dependensi:
   ```
   pip install -r requirements.txt
   ```
2. Jalankan aplikasi:
   ```
   python main.py
   ```

## Akun Default

| Username | Password |
|----------|----------|
| admin    | admin    |

Password dapat diganti melalui menu **File → Ganti Password** setelah login.

## Fitur

### Halaman 1 — Manajemen Proyek
- Tambah, edit, hapus proyek (CRUD lengkap) dengan konfirmasi QMessageBox
- Tabel data dengan QTableWidget: kolom Nama Proyek, Klien, Deadline, Status, Aksi
- Search realtime by nama proyek / klien
- Filter dropdown by status proyek (Aktif / Selesai / Tunda)
- Form validasi: field kosong ditolak dengan pesan error

### Halaman 2 — Kanban Board
- Tampilan 3 kolom: **Todo**, **In Progress**, **Done**
- Tambah, edit, hapus tugas dengan form dialog + validasi
- Pindahkan tugas antar kolom (tombol ◀ ▶ pada setiap kartu)
- Search tugas realtime
- Filter by proyek dan prioritas
- **AI/ML**: Prediksi otomatis prioritas tugas (Tinggi/Sedang/Rendah) berbasis TF-IDF + Naive Bayes

### Halaman 3 — Laporan Kinerja
- 4 kartu statistik: Total Proyek, Total Tugas, Tugas Done, Tugas Todo
- Progress bar visual tingkat penyelesaian tugas
- **Export CSV**: data seluruh tugas dalam format `.csv`
- **Export PDF**: laporan berformat tabel dengan watermark logo TaskAI

### Fitur Tambahan
- Login + ganti password via menu File
- **Dark / Light mode** toggle via menu File → Mode Gelap
- Navigasi sidebar dengan QStackedWidget (min. 3 halaman)
- Status bar menampilkan nama & NIM semua anggota kelompok
- Menu bar: File (Ekspor, Mode Gelap, Ganti Password, Exit) + Help (About)

## Struktur Proyek

```
project-root/
├── main.py              # Entry point
├── requirements.txt
├── README.md
├── taskai.db            # SQLite database (auto-created)
├── ui/
│   ├── login_page.py
│   ├── manajemen_proyek_page.py
│   ├── manajemen_proyek.ui  # Qt Designer file
│   ├── kanban_board_page.py
│   └── laporan_kinerja_page.py
├── database/
│   └── db_manager.py    # Setup & koneksi SQLite
├── models/
│   ├── proyek_model.py  # CRUD proyek
│   └── tugas_model.py   # CRUD tugas
├── utils/
│   ├── ai_predictor.py  # TF-IDF + Naive Bayes
│   └── data_exporter.py # Ekspor CSV & PDF
└── assets/
    ├── style.qss        # Stylesheet global
    ├── icons/           # Icon aplikasi
    └── __init__.py
```

## Teknologi

| Library      | Kegunaan                        |
|--------------|---------------------------------|
| PySide6      | GUI framework (Qt for Python)   |
| SQLite       | Database lokal                  |
| scikit-learn | AI/ML prediksi prioritas tugas  |
| ReportLab    | Export PDF                      |
| Pandas       | Pemrosesan data export          |
