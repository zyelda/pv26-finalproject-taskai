from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from assets import icon, pixmap
from database.db_manager import daftar_pengguna, username_tersedia


class RegisterPage(QWidget):
    """Halaman pendaftaran akun baru. Desainnya mengikuti LoginPage agar
    pengalaman visual konsisten antara login dan daftar."""

    register_success = Signal()
    kembali_ke_login = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskAI - Daftar")
        self.setWindowIcon(icon("taskai.png"))
        self.setFixedSize(420, 600)
        self._setup_ui()
        self.btn_daftar.clicked.connect(self._daftar)
        self.btn_ke_login.clicked.connect(self.kembali_ke_login.emit)
        self.txt_username.returnPressed.connect(self.txt_password.setFocus)
        self.txt_password.returnPressed.connect(self.txt_konfirm.setFocus)
        self.txt_konfirm.returnPressed.connect(self._daftar)

    def _setup_ui(self):
        # Background gelap/terang ikut system stylesheet (sama seperti login)
        self.setObjectName("login_bg")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 32, 32, 32)
        outer.addStretch(1)

        # ── Card ──────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("login_card")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(14)

        # Logo
        lbl_logo = QLabel()
        pm = pixmap("taskai.png")
        if not pm.isNull():
            lbl_logo.setPixmap(pm.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lbl_logo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(lbl_logo)

        # Judul
        lbl_judul = QLabel("Buat Akun")
        lbl_judul.setObjectName("login_title")
        lbl_judul.setAlignment(Qt.AlignCenter)
        lbl_judul.setFont(QFont("Segoe UI", 20, QFont.Bold))
        card_layout.addWidget(lbl_judul)

        lbl_sub = QLabel("Daftar untuk mulai menggunakan TaskAI")
        lbl_sub.setObjectName("login_subtitle")
        lbl_sub.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(lbl_sub)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setObjectName("login_divider")
        card_layout.addWidget(div)
        card_layout.addSpacing(4)

        # Username
        lbl_u = QLabel("Username")
        lbl_u.setObjectName("login_field_label")
        card_layout.addWidget(lbl_u)
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Buat username")
        self.txt_username.setFixedHeight(42)
        self.txt_username.setObjectName("login_input")
        card_layout.addWidget(self.txt_username)

        # Password
        lbl_p = QLabel("Password")
        lbl_p.setObjectName("login_field_label")
        card_layout.addWidget(lbl_p)
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Buat password")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setFixedHeight(42)
        self.txt_password.setObjectName("login_input")
        card_layout.addWidget(self.txt_password)

        # Konfirmasi Password
        lbl_k = QLabel("Konfirmasi Password")
        lbl_k.setObjectName("login_field_label")
        card_layout.addWidget(lbl_k)
        self.txt_konfirm = QLineEdit()
        self.txt_konfirm.setPlaceholderText("Ulangi password")
        self.txt_konfirm.setEchoMode(QLineEdit.Password)
        self.txt_konfirm.setFixedHeight(42)
        self.txt_konfirm.setObjectName("login_input")
        card_layout.addWidget(self.txt_konfirm)

        card_layout.addSpacing(6)

        # Tombol daftar
        self.btn_daftar = QPushButton("Daftar")
        self.btn_daftar.setFixedHeight(44)
        self.btn_daftar.setCursor(Qt.PointingHandCursor)
        self.btn_daftar.setObjectName("btn_login_submit")
        self.btn_daftar.setFont(QFont("Segoe UI", 10, QFont.Bold))
        card_layout.addWidget(self.btn_daftar)

        # Baris "Sudah punya akun? Masuk"
        switch_row = QHBoxLayout()
        switch_row.setSpacing(4)
        switch_row.addStretch()
        lbl_switch = QLabel("Sudah punya akun?")
        lbl_switch.setObjectName("login_switch_label")
        switch_row.addWidget(lbl_switch)
        self.btn_ke_login = QPushButton("Masuk di sini")
        self.btn_ke_login.setCursor(Qt.PointingHandCursor)
        self.btn_ke_login.setObjectName("btn_auth_link")
        switch_row.addWidget(self.btn_ke_login)
        switch_row.addStretch()
        card_layout.addLayout(switch_row)

        outer.addWidget(card)
        outer.addStretch(1)

        lbl_hint = QLabel("Pemrograman Visual — Semester Genap 2025/2026")
        lbl_hint.setObjectName("login_footer")
        lbl_hint.setAlignment(Qt.AlignCenter)
        outer.addWidget(lbl_hint)

    def _daftar(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        konfirmasi = self.txt_konfirm.text().strip()

        if not username or not password or not konfirmasi:
            QMessageBox.warning(self, "Daftar Gagal", "Semua kolom wajib diisi.")
            return
        if len(username) < 3:
            QMessageBox.warning(self, "Daftar Gagal", "Username minimal 3 karakter.")
            return
        if len(password) < 4:
            QMessageBox.warning(self, "Daftar Gagal", "Password minimal 4 karakter.")
            return
        if password != konfirmasi:
            QMessageBox.warning(self, "Daftar Gagal", "Konfirmasi password tidak cocok.")
            self.txt_konfirm.clear()
            self.txt_konfirm.setFocus()
            return
        if not username_tersedia(username):
            QMessageBox.warning(self, "Daftar Gagal", "Username sudah digunakan, pilih yang lain.")
            self.txt_username.setFocus()
            return

        berhasil = daftar_pengguna(username, password)
        if berhasil:
            QMessageBox.information(
                self, "Berhasil", "Akun berhasil dibuat. Silakan masuk."
            )
            self.register_success.emit()
        else:
            QMessageBox.warning(self, "Daftar Gagal", "Username sudah digunakan, pilih yang lain.")
