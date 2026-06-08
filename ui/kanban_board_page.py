"""
ui/kanban_board_page.py
Halaman 2 — Kanban Board
Fitur: tampilan 3 kolom (Todo / In Progress / Done), CRUD tugas,
       search & filter, integrasi AI predictor prioritas.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QScrollArea, QFrame, QDialog,
    QFormLayout, QTextEdit, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from models.tugas_model import TugasModel
from utils.ai_predictor import predict_prioritas


# ---------------------------------------------------------------------------
# Warna per kolom
# ---------------------------------------------------------------------------
KOLOM_STYLE = {
    "Todo":        {"bg": "#EEF2FF", "header": "#4F46E5", "badge": "#C7D2FE", "teks": "#3730A3"},
    "In Progress": {"bg": "#FFF7ED", "header": "#EA580C", "badge": "#FED7AA", "teks": "#9A3412"},
    "Done":        {"bg": "#F0FDF4", "header": "#16A34A", "badge": "#BBF7D0", "teks": "#166534"},
}

PRIORITAS_STYLE = {
    "Tinggi": ("#FEE2E2", "#DC2626"),
    "Sedang": ("#FEF9C3", "#B45309"),
    "Rendah": ("#DCFCE7", "#15803D"),
}


# ---------------------------------------------------------------------------
# Widget kartu tugas individual
# ---------------------------------------------------------------------------
class TugasCard(QFrame):
    diedit  = Signal(int)   # tugas_id
    dihapus = Signal(int)   # tugas_id
    dipindah = Signal(int, str)  # tugas_id, status_baru

    STATUS_URUTAN = ["Todo", "In Progress", "Done"]

    def __init__(self, row, parent=None):
        super().__init__(parent)
        self._id       = row[0]
        self._status   = row[5] if len(row) > 5 else "Todo"
        self._prioritas = row[4] if len(row) > 4 else "Sedang"

        nama       = row[2] if len(row) > 2 else "-"
        deskripsi  = row[3] if len(row) > 3 else ""

        bg, border = PRIORITAS_STYLE.get(self._prioritas, ("#F9FAFB", "#6B7280"))

        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #E5E7EB;
                border-left: 4px solid {border};
                border-radius: 8px;
                margin: 4px 2px;
            }}
            QFrame:hover {{ border-color: #6366F1; background: #FAFAFA; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        # Baris judul + badge prioritas
        top = QHBoxLayout()
        lbl_nama = QLabel(nama)
        lbl_nama.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_nama.setWordWrap(True)
        lbl_nama.setStyleSheet("color: #111827; border: none;")
        top.addWidget(lbl_nama, 1)

        badge = QLabel(self._prioritas)
        badge.setFixedHeight(20)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"""
            background: {bg}; color: {border};
            border-radius: 10px; padding: 0 8px;
            font-size: 10px; font-weight: bold; border: none;
        """)
        top.addWidget(badge)
        layout.addLayout(top)

        # Deskripsi singkat
        if deskripsi:
            lbl_desk = QLabel(deskripsi[:80] + ("…" if len(deskripsi) > 80 else ""))
            lbl_desk.setStyleSheet("color: #6B7280; font-size: 9pt; border: none;")
            lbl_desk.setWordWrap(True)
            layout.addWidget(lbl_desk)

        # Tombol aksi
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)

        idx = self.STATUS_URUTAN.index(self._status) if self._status in self.STATUS_URUTAN else 0

        if idx > 0:
            btn_back = self._btn("◀", "#6B7280")
            btn_back.setToolTip(f"Pindah ke {self.STATUS_URUTAN[idx-1]}")
            btn_back.clicked.connect(lambda: self.dipindah.emit(self._id, self.STATUS_URUTAN[idx-1]))
            btn_row.addWidget(btn_back)

        btn_row.addStretch()

        btn_edit = self._btn("✎ Edit", "#6366F1")
        btn_edit.clicked.connect(lambda: self.diedit.emit(self._id))
        btn_row.addWidget(btn_edit)

        btn_del = self._btn("🗑", "#EF4444")
        btn_del.clicked.connect(lambda: self.dihapus.emit(self._id))
        btn_row.addWidget(btn_del)

        if idx < len(self.STATUS_URUTAN) - 1:
            btn_fwd = self._btn("▶", "#16A34A")
            btn_fwd.setToolTip(f"Pindah ke {self.STATUS_URUTAN[idx+1]}")
            btn_fwd.clicked.connect(lambda: self.dipindah.emit(self._id, self.STATUS_URUTAN[idx+1]))
            btn_row.addWidget(btn_fwd)

        layout.addLayout(btn_row)

    @staticmethod
    def _btn(teks, warna):
        b = QPushButton(teks)
        b.setCursor(Qt.PointingHandCursor)
        b.setFixedHeight(26)
        b.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {warna};
                border: 1px solid {warna}; border-radius: 5px;
                padding: 0 8px; font-size: 9pt;
            }}
            QPushButton:hover {{ background: {warna}22; }}
        """)
        return b


# ---------------------------------------------------------------------------
# Kolom Kanban (Todo / In Progress / Done)
# ---------------------------------------------------------------------------
class KolomKanban(QWidget):
    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.status = status
        style = KOLOM_STYLE[status]

        self.setMinimumWidth(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(f"background: {style['bg']}; border-radius: 12px;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        # Header kolom
        header = QLabel(status)
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(34)
        header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        header.setStyleSheet(f"""
            background: {style['header']}; color: white;
            border-radius: 8px; padding: 4px;
        """)
        outer.addWidget(header)

        # Counter jumlah kartu
        self.lbl_count = QLabel("0 tugas")
        self.lbl_count.setAlignment(Qt.AlignCenter)
        self.lbl_count.setStyleSheet(f"color: {style['teks']}; font-size: 9pt;")
        outer.addWidget(self.lbl_count)

        # Area scroll untuk kartu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._inner = QVBoxLayout(self._container)
        self._inner.setAlignment(Qt.AlignTop)
        self._inner.setContentsMargins(0, 0, 0, 0)
        self._inner.setSpacing(2)

        scroll.setWidget(self._container)
        outer.addWidget(scroll)

    def set_cards(self, cards: list):
        """Isi ulang kolom dengan daftar widget TugasCard."""
        while self._inner.count():
            item = self._inner.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for card in cards:
            self._inner.addWidget(card)
        self.lbl_count.setText(f"{len(cards)} tugas")


# ---------------------------------------------------------------------------
# Dialog tambah / edit tugas
# ---------------------------------------------------------------------------
class TugasDialog(QDialog):
    def __init__(self, parent=None, proyek_list=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Tugas" if data is None else "Edit Tugas")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._data = data

        form = QFormLayout(self)
        form.setRowWrapPolicy(QFormLayout.WrapAllRows)
        form.setSpacing(12)
        form.setContentsMargins(20, 20, 20, 20)

        # Pilih proyek
        self.cmb_proyek = QComboBox()
        self._proyek_list = proyek_list or []
        for p in self._proyek_list:
            self.cmb_proyek.addItem(p[1], p[0])   # nama, id
        form.addRow("Proyek *", self.cmb_proyek)

        # Nama tugas
        self.txt_nama = QLineEdit()
        self.txt_nama.setPlaceholderText("Nama tugas...")
        self.txt_nama.textChanged.connect(self._auto_predict)
        form.addRow("Nama Tugas *", self.txt_nama)

        # Deskripsi
        self.txt_desk = QTextEdit()
        self.txt_desk.setFixedHeight(80)
        self.txt_desk.setPlaceholderText("Deskripsi singkat (opsional)...")
        self.txt_desk.textChanged.connect(self._auto_predict)
        form.addRow("Deskripsi", self.txt_desk)

        # Prioritas + badge prediksi AI
        prio_row = QHBoxLayout()
        self.cmb_prioritas = QComboBox()
        self.cmb_prioritas.addItems(["Tinggi", "Sedang", "Rendah"])
        prio_row.addWidget(self.cmb_prioritas, 1)

        self.lbl_ai = QLabel("🤖 AI siap")
        self.lbl_ai.setStyleSheet("color: #6B7280; font-size: 9pt;")
        prio_row.addWidget(self.lbl_ai)
        form.addRow("Prioritas", prio_row)

        # Status
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Todo", "In Progress", "Done"])
        form.addRow("Status", self.cmb_status)

        # Tombol
        btn_row = QHBoxLayout()
        btn_simpan = QPushButton("💾 Simpan")
        btn_simpan.setObjectName("btn_simpan")
        btn_simpan.setCursor(Qt.PointingHandCursor)
        btn_simpan.setStyleSheet("""
            QPushButton { background:#4F46E5; color:white; border-radius:6px;
                          padding:8px 24px; font-weight:bold; }
            QPushButton:hover { background:#4338CA; }
        """)
        btn_simpan.clicked.connect(self._simpan)

        btn_batal = QPushButton("Batal")
        btn_batal.setCursor(Qt.PointingHandCursor)
        btn_batal.setStyleSheet("""
            QPushButton { background:#F3F4F6; color:#374151; border-radius:6px; padding:8px 16px; }
            QPushButton:hover { background:#E5E7EB; }
        """)
        btn_batal.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(btn_batal)
        btn_row.addWidget(btn_simpan)
        form.addRow(btn_row)

        # Isi data jika mode edit
        if data:
            idx_proyek = self.cmb_proyek.findData(data[1])
            if idx_proyek >= 0:
                self.cmb_proyek.setCurrentIndex(idx_proyek)
            self.txt_nama.setText(data[2])
            self.txt_desk.setPlainText(data[3] or "")
            idx_prio = self.cmb_prioritas.findText(data[4])
            if idx_prio >= 0:
                self.cmb_prioritas.setCurrentIndex(idx_prio)
            idx_status = self.cmb_status.findText(data[5])
            if idx_status >= 0:
                self.cmb_status.setCurrentIndex(idx_status)

    def _auto_predict(self):
        """Panggil AI predictor dan update combobox + label badge."""
        judul = self.txt_nama.text().strip()
        desk  = self.txt_desk.toPlainText().strip()
        if len(judul) < 3:
            return
        try:
            hasil = predict_prioritas(judul, desk)
            idx = self.cmb_prioritas.findText(hasil)
            if idx >= 0:
                self.cmb_prioritas.setCurrentIndex(idx)
            self.lbl_ai.setText(f"🤖 AI: {hasil}")
        except Exception:
            pass

    def _simpan(self):
        nama = self.txt_nama.text().strip()
        if not nama:
            QMessageBox.warning(self, "Validasi", "Nama tugas tidak boleh kosong.")
            return
        if self.cmb_proyek.count() == 0:
            QMessageBox.warning(self, "Validasi", "Tidak ada proyek. Tambah proyek dulu.")
            return
        self.accept()

    def get_data(self):
        return {
            "proyek_id": self.cmb_proyek.currentData(),
            "nama_tugas": self.txt_nama.text().strip(),
            "deskripsi":  self.txt_desk.toPlainText().strip(),
            "prioritas":  self.cmb_prioritas.currentText(),
            "status":     self.cmb_status.currentText(),
        }


# ---------------------------------------------------------------------------
# Halaman utama Kanban Board
# ---------------------------------------------------------------------------
class KanbanBoardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._proyek_list = []
        self._setup_ui()
        self._load_proyek()
        self.refresh()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # ── Judul ──────────────────────────────────────────────────────────
        lbl_judul = QLabel("📋 Kanban Board")
        lbl_judul.setFont(QFont("Segoe UI", 16, QFont.Bold))
        lbl_judul.setStyleSheet("color: #111827;")
        root.addWidget(lbl_judul)

        # ── Toolbar (filter proyek, search, filter status/prioritas, tambah) ──
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        # Filter proyek
        self.cmb_filter_proyek = QComboBox()
        self.cmb_filter_proyek.setObjectName("cmb_filter_proyek")
        self.cmb_filter_proyek.setFixedWidth(180)
        self.cmb_filter_proyek.setStyleSheet(self._combo_style())
        self.cmb_filter_proyek.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(QLabel("Proyek:"))
        toolbar.addWidget(self.cmb_filter_proyek)

        # Search
        self.txt_search_tugas = QLineEdit()
        self.txt_search_tugas.setObjectName("txt_search_tugas")
        self.txt_search_tugas.setPlaceholderText("🔍 Cari tugas...")
        self.txt_search_tugas.setFixedWidth(200)
        self.txt_search_tugas.setStyleSheet(self._input_style())
        self.txt_search_tugas.textChanged.connect(self.refresh)
        toolbar.addWidget(self.txt_search_tugas)

        # Filter prioritas
        self.cmb_filter_prioritas = QComboBox()
        self.cmb_filter_prioritas.setObjectName("cmb_filter_prioritas")
        self.cmb_filter_prioritas.addItems(["Semua Prioritas", "Tinggi", "Sedang", "Rendah"])
        self.cmb_filter_prioritas.setFixedWidth(150)
        self.cmb_filter_prioritas.setStyleSheet(self._combo_style())
        self.cmb_filter_prioritas.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.cmb_filter_prioritas)

        # Filter status (tersembunyi di kanban tapi berguna untuk pencarian)
        self.cmb_filter_status = QComboBox()
        self.cmb_filter_status.setObjectName("cmb_filter_status")
        self.cmb_filter_status.addItems(["Semua Status", "Todo", "In Progress", "Done"])
        self.cmb_filter_status.setFixedWidth(150)
        self.cmb_filter_status.setStyleSheet(self._combo_style())
        self.cmb_filter_status.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.cmb_filter_status)

        toolbar.addStretch()

        # Tombol tambah
        btn_tambah = QPushButton("+ Tambah Tugas")
        btn_tambah.setObjectName("btn_tambah_tugas")
        btn_tambah.setCursor(Qt.PointingHandCursor)
        btn_tambah.setStyleSheet("""
            QPushButton { background:#4F46E5; color:white; border-radius:8px;
                          padding:8px 18px; font-weight:bold; font-size:10pt; }
            QPushButton:hover { background:#4338CA; }
        """)
        btn_tambah.clicked.connect(self._tambah_tugas)
        toolbar.addWidget(btn_tambah)

        root.addLayout(toolbar)

        # ── Tiga kolom Kanban ────────────────────────────────────────────────
        self.kolom_todo    = KolomKanban("Todo")
        self.kolom_prog    = KolomKanban("In Progress")
        self.kolom_done    = KolomKanban("Done")

        board = QHBoxLayout()
        board.setSpacing(12)
        board.addWidget(self.kolom_todo)
        board.addWidget(self.kolom_prog)
        board.addWidget(self.kolom_done)
        root.addLayout(board)

    # ── Helpers ────────────────────────────────────────────────────────────
    @staticmethod
    def _input_style():
        return """
            QLineEdit { border:1.5px solid #D1D5DB; border-radius:6px;
                        padding:6px 10px; background:white; }
            QLineEdit:focus { border-color:#6366F1; }
        """

    @staticmethod
    def _combo_style():
        return """
            QComboBox { border:1.5px solid #D1D5DB; border-radius:6px;
                        padding:5px 10px; background:white; }
            QComboBox:focus { border-color:#6366F1; }
        """

    def _load_proyek(self):
        """Muat daftar proyek ke filter combobox."""
        try:
            from models.proyek_model import ProyekModel
            self._proyek_list = ProyekModel.get_all()
        except Exception:
            self._proyek_list = []

        self.cmb_filter_proyek.blockSignals(True)
        self.cmb_filter_proyek.clear()
        self.cmb_filter_proyek.addItem("Semua Proyek", None)
        for p in self._proyek_list:
            self.cmb_filter_proyek.addItem(p[1], p[0])
        self.cmb_filter_proyek.blockSignals(False)

    # ── CRUD ───────────────────────────────────────────────────────────────
    def _tambah_tugas(self):
        if not self._proyek_list:
            QMessageBox.information(self, "Info", "Tambah proyek terlebih dahulu di halaman Manajemen Proyek.")
            return
        dialog = TugasDialog(self, proyek_list=self._proyek_list)
        if dialog.exec() == QDialog.Accepted:
            d = dialog.get_data()
            TugasModel.add_tugas(d["proyek_id"], d["nama_tugas"],
                                 d["deskripsi"], d["prioritas"], d["status"])
            self.refresh()

    def _edit_tugas(self, tugas_id):
        row = TugasModel.get_tugas_by_id(tugas_id)
        if not row:
            return
        dialog = TugasDialog(self, proyek_list=self._proyek_list, data=row)
        if dialog.exec() == QDialog.Accepted:
            d = dialog.get_data()
            TugasModel.update_tugas(tugas_id, d["nama_tugas"],
                                    d["deskripsi"], d["prioritas"], d["status"])
            self.refresh()

    def _hapus_tugas(self, tugas_id):
        konfirm = QMessageBox.question(
            self, "Konfirmasi Hapus",
            "Yakin ingin menghapus tugas ini?",
            QMessageBox.Yes | QMessageBox.No
        )
        if konfirm == QMessageBox.Yes:
            TugasModel.delete_tugas(tugas_id)
            self.refresh()

    def _pindah_status(self, tugas_id, status_baru):
        TugasModel.update_status_tugas(tugas_id, status_baru)
        self.refresh()

    # ── Refresh board ──────────────────────────────────────────────────────
    def refresh(self):
        """Ambil ulang data dari DB, terapkan filter, dan render kartu."""
        keyword   = self.txt_search_tugas.text().strip()
        proyek_id = self.cmb_filter_proyek.currentData()
        prioritas = self.cmb_filter_prioritas.currentText()
        status    = self.cmb_filter_status.currentText()

        prioritas = None if prioritas == "Semua Prioritas" else prioritas
        status    = None if status    == "Semua Status"    else status

        # Ambil data
        if keyword:
            rows = TugasModel.search_tugas(keyword)
        else:
            rows = TugasModel.filter_tugas(
                proyek_id=proyek_id,
                prioritas=prioritas,
                status=status
            )

        # Pisah per kolom
        buckets = {"Todo": [], "In Progress": [], "Done": []}
        for row in rows:
            s = row[5] if len(row) > 5 else "Todo"
            if s in buckets:
                buckets[s].append(row)

        # Render
        for kolom, status_key in [
            (self.kolom_todo,  "Todo"),
            (self.kolom_prog,  "In Progress"),
            (self.kolom_done,  "Done"),
        ]:
            cards = []
            for row in buckets[status_key]:
                card = TugasCard(row)
                card.diedit.connect(self._edit_tugas)
                card.dihapus.connect(self._hapus_tugas)
                card.dipindah.connect(self._pindah_status)
                cards.append(card)
            kolom.set_cards(cards)
