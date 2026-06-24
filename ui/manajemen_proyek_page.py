import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLineEdit, QComboBox, QDateEdit,
    QDialog, QMessageBox, QLabel, QFrame,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from PySide6.QtUiTools import QUiLoader
from models.proyek_model import ProyekModel
from assets import icon


class ProyekDialog(QDialog):
    def __init__(self, parent=None, proyek_data=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Proyek" if proyek_data is None else "Edit Proyek")
        self.setModal(True)
        self.setMinimumWidth(450)

        layout = QFormLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        self.txt_nama_proyek = QLineEdit()
        self.txt_nama_proyek.setPlaceholderText("Masukkan nama proyek")
        self.txt_klien = QLineEdit()
        self.txt_klien.setPlaceholderText("Masukkan nama klien")
        self.date_deadline = QDateEdit()
        self.date_deadline.setCalendarPopup(True)
        self.date_deadline.setDate(QDate.currentDate())
        self.date_deadline.setDisplayFormat("yyyy-MM-dd")
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Aktif", "Selesai", "Tunda"])

        layout.addRow("Nama Proyek:", self.txt_nama_proyek)
        layout.addRow("Klien:", self.txt_klien)
        layout.addRow("Deadline:", self.date_deadline)
        layout.addRow("Status:", self.cmb_status)

        btn_layout = QHBoxLayout()
        self.btn_simpan = QPushButton("Simpan")
        self.btn_batal  = QPushButton("Batal")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_batal)
        btn_layout.addWidget(self.btn_simpan)
        layout.addRow(btn_layout)

        self.btn_simpan.clicked.connect(self._validate_and_accept)
        self.btn_batal.clicked.connect(self.reject)

        if proyek_data:
            self.txt_nama_proyek.setText(proyek_data["nama_proyek"])
            self.txt_klien.setText(proyek_data["klien"])
            deadline = QDate.fromString(proyek_data["deadline"], "yyyy-MM-dd")
            if deadline.isValid():
                self.date_deadline.setDate(deadline)
            self.cmb_status.setCurrentText(proyek_data["status"])

    def _validate_and_accept(self):
        if not self.txt_nama_proyek.text().strip():
            QMessageBox.warning(self, "Validasi", "Nama proyek tidak boleh kosong.")
            return
        if not self.txt_klien.text().strip():
            QMessageBox.warning(self, "Validasi", "Klien tidak boleh kosong.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "nama_proyek": self.txt_nama_proyek.text().strip(),
            "klien":       self.txt_klien.text().strip(),
            "deadline":    self.date_deadline.date().toString("yyyy-MM-dd"),
            "status":      self.cmb_status.currentText(),
        }


class ManajemenProyekPage(QWidget):
    KOLOM_ID      = 0
    KOLOM_NAMA    = 1
    KOLOM_KLIEN   = 2
    KOLOM_DEADLINE = 3
    KOLOM_STATUS  = 4
    KOLOM_AKSI    = 5

    def __init__(self):
        super().__init__()

        loader  = QUiLoader()
        ui_path = os.path.join(os.path.dirname(__file__), "manajemen_proyek.ui")
        self.ui = loader.load(ui_path)

        # ── Layout luar: header + konten ────────────────────────────
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header bar — gunakan object name agar dark-mode QSS bisa target
        header_bar = QFrame()
        header_bar.setObjectName("header_bar")
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(24, 16, 24, 16)
        header_layout.setSpacing(0)

        title_col = QVBoxLayout(); title_col.setSpacing(2)
        lbl_title = QLabel("Manajemen Proyek")
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_title.setObjectName("page_title_header")
        title_col.addWidget(lbl_title)
        lbl_sub = QLabel("Kelola daftar proyek dan klien")
        lbl_sub.setObjectName("page_sub_header")
        title_col.addWidget(lbl_sub)
        header_layout.addLayout(title_col)
        header_layout.addStretch()

        outer.addWidget(header_bar)

        # Konten
        content = QWidget()
        content.setObjectName("manajemen_content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(12)
        content_layout.addWidget(self.ui)
        outer.addWidget(content, 1)

        # ── Ambil widget dari .ui ────────────────────────────────────
        self.tbl: QTableWidget      = self.ui.findChild(QTableWidget, "tbl_proyek")
        self.txt_search: QLineEdit  = self.ui.findChild(QLineEdit,    "txt_search")
        self.cmb_filter: QComboBox  = self.ui.findChild(QComboBox,    "cmb_filter_status")
        self.btn_tambah: QPushButton = self.ui.findChild(QPushButton,  "btn_tambah")

        self.btn_tambah.setIcon(icon("add.png"))
        self.btn_tambah.setText("+ Tambah Proyek")
        self.btn_tambah.setFixedHeight(38)
        self.btn_tambah.setCursor(Qt.PointingHandCursor)
        self.btn_tambah.setStyleSheet(
            "QPushButton { background-color: #3b82f6; color: #ffffff; border: none;"
            " border-radius: 7px; padding: 0 16px; font-weight: 600; font-size: 10pt; }"
            "QPushButton:hover { background-color: #2563eb; }"
            "QPushButton:pressed { background-color: #1d4ed8; }"
        )

        self.txt_search.setPlaceholderText("  Cari nama proyek atau klien...")
        self.txt_search.setFixedHeight(38)

        self.cmb_filter.setFixedHeight(38)

        self._setup_table()
        self._connect_signals()
        self.load_data()

    def _setup_table(self):
        headers = ["ID", "Nama Proyek", "Klien", "Deadline", "Status", "Aksi"]
        self.tbl.setColumnCount(len(headers))
        self.tbl.setHorizontalHeaderLabels(headers)
        self.tbl.setColumnHidden(self.KOLOM_ID, True)
        self.tbl.horizontalHeader().setSectionResizeMode(self.KOLOM_NAMA,  QHeaderView.Stretch)
        self.tbl.horizontalHeader().setSectionResizeMode(self.KOLOM_KLIEN, QHeaderView.Stretch)
        self.tbl.setColumnWidth(self.KOLOM_DEADLINE, 110)
        self.tbl.setColumnWidth(self.KOLOM_STATUS,    90)
        self.tbl.setColumnWidth(self.KOLOM_AKSI,     185)
        self.tbl.verticalHeader().setDefaultSectionSize(46)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setSelectionBehavior(QTableWidget.SelectRows)

    def _connect_signals(self):
        self.btn_tambah.clicked.connect(self._open_tambah_dialog)
        self.txt_search.textChanged.connect(self._filter_table)
        self.cmb_filter.currentIndexChanged.connect(self._filter_table)

    def load_data(self):
        self.tbl.setRowCount(0)
        for proyek in ProyekModel.get_all_proyek():
            row = self.tbl.rowCount()
            self.tbl.insertRow(row)

            id_item = QTableWidgetItem(str(proyek["id"]))
            id_item.setData(Qt.UserRole, proyek["id"])
            self.tbl.setItem(row, self.KOLOM_ID,       id_item)
            self.tbl.setItem(row, self.KOLOM_NAMA,     QTableWidgetItem(proyek["nama_proyek"]))
            self.tbl.setItem(row, self.KOLOM_KLIEN,    QTableWidgetItem(proyek["klien"]))
            self.tbl.setItem(row, self.KOLOM_DEADLINE, QTableWidgetItem(proyek["deadline"]))

            status_item = QTableWidgetItem(proyek["status"])
            status_item.setTextAlignment(Qt.AlignCenter)
            self.tbl.setItem(row, self.KOLOM_STATUS, status_item)

            self._setup_action_buttons(row)

    def _setup_action_buttons(self, row: int):
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        btn_edit = QPushButton(icon("edit.png"), " Edit")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setFixedHeight(30)
        btn_edit.setMinimumWidth(72)
        btn_edit.setStyleSheet(
            "QPushButton { background-color: #f59e0b; color: #ffffff; border: none;"
            " border-radius: 6px; padding: 0 10px; font-weight: 600; font-size: 9pt; }"
            "QPushButton:hover { background-color: #d97706; }"
        )

        btn_hapus = QPushButton(icon("delete.png"), " Hapus")
        btn_hapus.setCursor(Qt.PointingHandCursor)
        btn_hapus.setFixedHeight(30)
        btn_hapus.setMinimumWidth(72)
        btn_hapus.setStyleSheet(
            "QPushButton { background-color: #ef4444; color: #ffffff; border: none;"
            " border-radius: 6px; padding: 0 10px; font-weight: 600; font-size: 9pt; }"
            "QPushButton:hover { background-color: #dc2626; }"
        )

        btn_edit.clicked.connect(lambda checked, r=row: self._open_edit_dialog(r))
        btn_hapus.clicked.connect(lambda checked, r=row: self._confirm_hapus(r))

        layout.addWidget(btn_edit)
        layout.addWidget(btn_hapus)
        layout.addStretch()
        self.tbl.setCellWidget(row, self.KOLOM_AKSI, container)

    def _open_tambah_dialog(self):
        dialog = ProyekDialog(self)
        if dialog.exec() == QDialog.Accepted:
            d = dialog.get_data()
            ProyekModel.add_proyek(d["nama_proyek"], d["klien"], d["deadline"], d["status"])
            self.load_data()

    def _open_edit_dialog(self, row: int):
        id_item = self.tbl.item(row, self.KOLOM_ID)
        if not id_item:
            return
        proyek_data = {
            "id":          int(id_item.text()),
            "nama_proyek": self.tbl.item(row, self.KOLOM_NAMA).text(),
            "klien":       self.tbl.item(row, self.KOLOM_KLIEN).text(),
            "deadline":    self.tbl.item(row, self.KOLOM_DEADLINE).text(),
            "status":      self.tbl.item(row, self.KOLOM_STATUS).text(),
        }
        dialog = ProyekDialog(self, proyek_data)
        if dialog.exec() == QDialog.Accepted:
            d = dialog.get_data()
            ProyekModel.update_proyek(
                proyek_data["id"], d["nama_proyek"], d["klien"],
                d["deadline"], d["status"],
            )
            self.load_data()

    def _confirm_hapus(self, row: int):
        id_item = self.tbl.item(row, self.KOLOM_ID)
        if not id_item:
            return
        nama = self.tbl.item(row, self.KOLOM_NAMA).text()
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus proyek '{nama}'?\n"
            "Semua tugas dalam proyek ini akan ikut terhapus.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            ProyekModel.delete_proyek(int(id_item.text()))
            self.load_data()

    def _filter_table(self):
        search_text   = self.txt_search.text().strip().lower()
        filter_status = self.cmb_filter.currentText()
        for row in range(self.tbl.rowCount()):
            nama   = self.tbl.item(row, self.KOLOM_NAMA).text().lower()
            klien  = self.tbl.item(row, self.KOLOM_KLIEN).text().lower()
            status = self.tbl.item(row, self.KOLOM_STATUS).text()
            match_search = not search_text or search_text in nama or search_text in klien
            match_filter = filter_status == "Semua Status" or status == filter_status
            self.tbl.setRowHidden(row, not (match_search and match_filter))
