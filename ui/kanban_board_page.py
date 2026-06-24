"""
ui/kanban_board_page.py
Halaman Kanban Board — 3 kolom (Todo / In Progress / Done)
Fitur: CRUD tugas, search & filter, AI prediksi prioritas.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QScrollArea, QFrame, QDialog,
    QFormLayout, QTextEdit, QMessageBox, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from models.tugas_model import TugasModel
from utils.ai_predictor import predict_prioritas


# ── Konstanta warna ─────────────────────────────────────────────────────────
KOLOM_STYLE = {
    "Todo":        {"bg": "#EEF2FF", "header": "#4F46E5", "teks": "#3730A3"},
    "In Progress": {"bg": "#FFF7ED", "header": "#EA580C", "teks": "#9A3412"},
    "Done":        {"bg": "#F0FDF4", "header": "#16A34A", "teks": "#166534"},
}

PRIORITAS_STYLE = {
    "Tinggi": ("#FEE2E2", "#DC2626"),
    "Sedang": ("#FEF9C3", "#B45309"),
    "Rendah": ("#DCFCE7", "#15803D"),
}


# ── Kartu Tugas ─────────────────────────────────────────────────────────────
class TugasCard(QFrame):
    diedit   = Signal(int)
    dihapus  = Signal(int)
    dipindah = Signal(int, str)

    STATUS_URUTAN = ["Todo", "In Progress", "Done"]

    def __init__(self, row, parent=None):
        super().__init__(parent)
        self._id       = row[0]
        self._status   = row[5] if len(row) > 5 else "Todo"
        self._prioritas = row[4] if len(row) > 4 else "Sedang"
        nama      = row[2] if len(row) > 2 else "-"
        deskripsi = row[3] if len(row) > 3 else ""

        bg, border = PRIORITAS_STYLE.get(self._prioritas, ("#F9FAFB", "#6B7280"))

        self.setObjectName("kanban_card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame#kanban_card {{
                background: white;
                border: 1px solid #E5E7EB;
                border-left: 4px solid {border};
                border-radius: 8px;
                margin: 4px 2px;
            }}
            QFrame#kanban_card:hover {{ border-color: #6366F1; background: #FAFAFA; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        # Judul + badge prioritas
        top = QHBoxLayout()
        lbl_nama = QLabel(nama)
        lbl_nama.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_nama.setWordWrap(True)
        lbl_nama.setStyleSheet("color: #111827; border: none; background: transparent;")
        top.addWidget(lbl_nama, 1)

        badge = QLabel(self._prioritas)
        badge.setFixedHeight(20)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"""
            background: {bg}; color: {border};
            border-radius: 10px; padding: 0 8px;
            font-size: 9px; font-weight: bold; border: none;
        """)
        top.addWidget(badge)
        layout.addLayout(top)

        # Deskripsi
        if deskripsi:
            lbl_desk = QLabel(deskripsi[:80] + ("…" if len(deskripsi) > 80 else ""))
            lbl_desk.setStyleSheet("color: #6B7280; font-size: 9pt; border: none; background: transparent;")
            lbl_desk.setWordWrap(True)
            layout.addWidget(lbl_desk)

        # Tombol aksi
        btn_row = QHBoxLayout(); btn_row.setSpacing(4)
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


# ── Kolom Kanban ─────────────────────────────────────────────────────────────
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

        header = QLabel(status)
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(34)
        header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        header.setStyleSheet(
            f"background: {style['header']}; color: white; border-radius: 8px; padding: 4px;"
        )
        outer.addWidget(header)

        self.lbl_count = QLabel("0 tugas")
        self.lbl_count.setAlignment(Qt.AlignCenter)
        self.lbl_count.setStyleSheet(f"color: {style['teks']}; font-size: 9pt; background: transparent;")
        outer.addWidget(self.lbl_count)

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
        while self._inner.count():
            item = self._inner.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for card in cards:
            self._inner.addWidget(card)
        n = len(cards)
        self.lbl_count.setText(f"{n} tugas")


# ── Dialog Tambah/Edit Tugas ─────────────────────────────────────────────────
class TugasDialog(QDialog):
    def __init__(self, parent=None, proyek_list=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Tugas" if data is None else "Edit Tugas")
        self.setMinimumWidth(420)
        self.setModal(True)

        form = QFormLayout(self)
        form.setRowWrapPolicy(QFormLayout.WrapAllRows)
        form.setSpacing(12)
        form.setContentsMargins(20, 20, 20, 20)

        # Proyek
        self.cmb_proyek = QComboBox()
        for p in (proyek_list or []):
            self.cmb_proyek.addItem(p["nama_proyek"], p["id"])
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

        # Prioritas + badge AI
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
        btn_simpan.setCursor(Qt.PointingHandCursor)
        btn_simpan.setStyleSheet(
            "QPushButton { background:#4F46E5; color:white; border-radius:6px; padding:8px 24px; font-weight:bold; }"
            "QPushButton:hover { background:#4338CA; }"
        )
        btn_batal = QPushButton("Batal")
        btn_batal.setCursor(Qt.PointingHandCursor)
        btn_batal.setStyleSheet(
            "QPushButton { background:#F3F4F6; color:#374151; border-radius:6px; padding:8px 16px; }"
            "QPushButton:hover { background:#E5E7EB; }"
        )
        btn_simpan.clicked.connect(self._simpan)
        btn_batal.clicked.connect(self.reject)
        btn_row.addStretch(); btn_row.addWidget(btn_batal); btn_row.addWidget(btn_simpan)
        form.addRow(btn_row)

        # Isi data jika edit
        if data:
            from models.proyek_model import ProyekModel
            proyek_list_full = ProyekModel.get_all_proyek() if proyek_list is None else proyek_list
            idx = self.cmb_proyek.findData(data[1])
            if idx >= 0:
                self.cmb_proyek.setCurrentIndex(idx)
            self.txt_nama.setText(data[2])
            self.txt_desk.setPlainText(data[3] or "")
            idx_p = self.cmb_prioritas.findText(data[4])
            if idx_p >= 0:
                self.cmb_prioritas.setCurrentIndex(idx_p)
            idx_s = self.cmb_status.findText(data[5])
            if idx_s >= 0:
                self.cmb_status.setCurrentIndex(idx_s)

    def _auto_predict(self):
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
        if not self.txt_nama.text().strip():
            QMessageBox.warning(self, "Validasi", "Nama tugas tidak boleh kosong.")
            return
        if self.cmb_proyek.count() == 0:
            QMessageBox.warning(self, "Validasi", "Tidak ada proyek. Tambah proyek dulu.")
            return
        self.accept()

    def get_data(self):
        return {
            "proyek_id":  self.cmb_proyek.currentData(),
            "nama_tugas": self.txt_nama.text().strip(),
            "deskripsi":  self.txt_desk.toPlainText().strip(),
            "prioritas":  self.cmb_prioritas.currentText(),
            "status":     self.cmb_status.currentText(),
        }


# ── Halaman Utama Kanban Board ───────────────────────────────────────────────
class KanbanBoardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._proyek_list = []
        self._setup_ui()
        self._load_proyek()
        self.refresh()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar (konsisten dengan halaman lain) ──────────────
        header_bar = QFrame()
        header_bar.setObjectName("header_bar")
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(24, 16, 24, 16)

        title_col = QVBoxLayout(); title_col.setSpacing(2)
        lbl_title = QLabel("Kanban Board")
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_title.setObjectName("page_title_header")
        title_col.addWidget(lbl_title)
        lbl_sub = QLabel("Kelola tugas per kolom status")
        lbl_sub.setObjectName("page_sub_header")
        title_col.addWidget(lbl_sub)
        header_layout.addLayout(title_col)
        header_layout.addStretch()
        root.addWidget(header_bar)

        # ── Konten ──────────────────────────────────────────────────
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 12, 16, 16)
        content_layout.setSpacing(12)

        # Toolbar
        toolbar = QHBoxLayout(); toolbar.setSpacing(8)

        toolbar.addWidget(QLabel("Proyek:"))
        self.cmb_filter_proyek = QComboBox()
        self.cmb_filter_proyek.setFixedWidth(180)
        self.cmb_filter_proyek.setStyleSheet(self._combo_style())
        self.cmb_filter_proyek.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.cmb_filter_proyek)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Cari tugas...")
        self.txt_search.setFixedWidth(200)
        self.txt_search.setStyleSheet(self._input_style())
        self.txt_search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.txt_search)

        self.cmb_filter_prioritas = QComboBox()
        self.cmb_filter_prioritas.addItems(["Semua Prioritas", "Tinggi", "Sedang", "Rendah"])
        self.cmb_filter_prioritas.setFixedWidth(150)
        self.cmb_filter_prioritas.setStyleSheet(self._combo_style())
        self.cmb_filter_prioritas.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.cmb_filter_prioritas)

        toolbar.addStretch()

        btn_tambah = QPushButton("+ Tambah Tugas")
        btn_tambah.setCursor(Qt.PointingHandCursor)
        btn_tambah.setStyleSheet(
            "QPushButton { background:#4F46E5; color:white; border-radius:8px;"
            " padding:8px 18px; font-weight:bold; font-size:10pt; }"
            "QPushButton:hover { background:#4338CA; }"
        )
        btn_tambah.clicked.connect(self._tambah_tugas)
        toolbar.addWidget(btn_tambah)
        content_layout.addLayout(toolbar)

        # Tiga kolom kanban
        self.kolom_todo = KolomKanban("Todo")
        self.kolom_prog = KolomKanban("In Progress")
        self.kolom_done = KolomKanban("Done")

        board = QHBoxLayout(); board.setSpacing(12)
        board.addWidget(self.kolom_todo)
        board.addWidget(self.kolom_prog)
        board.addWidget(self.kolom_done)
        content_layout.addLayout(board)

        root.addWidget(content, 1)

    @staticmethod
    def _input_style():
        return (
            "QLineEdit { border:1.5px solid #D1D5DB; border-radius:6px;"
            " padding:6px 10px; background:white; color:#111827; }"
            "QLineEdit:focus { border-color:#6366F1; }"
        )

    @staticmethod
    def _combo_style():
        return (
            "QComboBox { border:1.5px solid #D1D5DB; border-radius:6px;"
            " padding:5px 10px; background:white; color:#111827; }"
            "QComboBox:focus { border-color:#6366F1; }"
        )

    def _load_proyek(self):
        from models.proyek_model import ProyekModel
        try:
            self._proyek_list = ProyekModel.get_all_proyek()
        except Exception:
            self._proyek_list = []

        self.cmb_filter_proyek.blockSignals(True)
        self.cmb_filter_proyek.clear()
        self.cmb_filter_proyek.addItem("Semua Proyek", None)
        for p in self._proyek_list:
            self.cmb_filter_proyek.addItem(p["nama_proyek"], p["id"])
        self.cmb_filter_proyek.blockSignals(False)

    # ── CRUD ────────────────────────────────────────────────────────────────
    def _tambah_tugas(self):
        if not self._proyek_list:
            QMessageBox.information(
                self, "Info",
                "Tambah proyek terlebih dahulu di halaman Manajemen Proyek."
            )
            return
        dialog = TugasDialog(self, proyek_list=self._proyek_list)
        if dialog.exec() == QDialog.Accepted:
            d = dialog.get_data()
            TugasModel.add_tugas(
                d["proyek_id"], d["nama_tugas"],
                d["deskripsi"], d["prioritas"], d["status"]
            )
            self.refresh()

    def _edit_tugas(self, tugas_id):
        row = TugasModel.get_tugas_by_id(tugas_id)
        if not row:
            return
        dialog = TugasDialog(self, proyek_list=self._proyek_list, data=row)
        if dialog.exec() == QDialog.Accepted:
            d = dialog.get_data()
            TugasModel.update_tugas(
                tugas_id, d["nama_tugas"],
                d["deskripsi"], d["prioritas"], d["status"]
            )
            self.refresh()

    def _hapus_tugas(self, tugas_id):
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            "Yakin ingin menghapus tugas ini?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            TugasModel.delete_tugas(tugas_id)
            self.refresh()

    def _pindah_status(self, tugas_id, status_baru):
        TugasModel.update_status_tugas(tugas_id, status_baru)
        self.refresh()

    # ── Refresh board ────────────────────────────────────────────────────────
    def refresh(self):
        keyword   = self.txt_search.text().strip()
        proyek_id = self.cmb_filter_proyek.currentData()
        prioritas = self.cmb_filter_prioritas.currentText()
        prioritas = None if prioritas == "Semua Prioritas" else prioritas

        # FIX: search dan filter proyek/prioritas berjalan bersamaan
        if keyword:
            rows = TugasModel.search_tugas(keyword)
            # Terapkan filter proyek/prioritas pada hasil search juga
            if proyek_id is not None:
                rows = [r for r in rows if r[1] == proyek_id]
            if prioritas is not None:
                rows = [r for r in rows if (r[4] if len(r) > 4 else "") == prioritas]
        else:
            rows = TugasModel.filter_tugas(proyek_id=proyek_id, prioritas=prioritas)

        buckets = {"Todo": [], "In Progress": [], "Done": []}
        for row in rows:
            s = row[5] if len(row) > 5 else "Todo"
            if s in buckets:
                buckets[s].append(row)

        for kolom, key in [
            (self.kolom_todo, "Todo"),
            (self.kolom_prog, "In Progress"),
            (self.kolom_done, "Done"),
        ]:
            cards = []
            for row in buckets[key]:
                card = TugasCard(row)
                card.diedit.connect(self._edit_tugas)
                card.dihapus.connect(self._hapus_tugas)
                card.dipindah.connect(self._pindah_status)
                cards.append(card)
            kolom.set_cards(cards)
