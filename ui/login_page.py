from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from assets import icon, pixmap
from database.db_manager import verifikasi_login


class LoginPage(QWidget):
    login_success = Signal()
    daftar_diminta = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskAI - Login")
        self.setWindowIcon(icon("taskai.png"))
        self.setFixedSize(420, 560)
        self._setup_ui()
        self.btn_login.clicked.connect(self._login)
        self.btn_daftar.clicked.connect(self.daftar_diminta.emit)
        self.txt_password.returnPressed.connect(self._login)
        self.txt_username.returnPressed.connect(self.txt_password.setFocus)

    def _setup_ui(self):
        # Background gelap/terang ikut system stylesheet
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

        # Judul — pakai object name agar dark-mode QSS bisa target
        lbl_judul = QLabel("TaskAI")
        lbl_judul.setObjectName("login_title")
        lbl_judul.setAlignment(Qt.AlignCenter)
        lbl_judul.setFont(QFont("Segoe UI", 20, QFont.Bold))
        card_layout.addWidget(lbl_judul)

        lbl_sub = QLabel("Sistem Manajemen Proyek & Tugas")
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
        self.txt_username.setPlaceholderText("Masukkan username")
        self.txt_username.setFixedHeight(42)
        self.txt_username.setObjectName("login_input")
        card_layout.addWidget(self.txt_username)

        # Password
        lbl_p = QLabel("Password")
        lbl_p.setObjectName("login_field_label")
        card_layout.addWidget(lbl_p)
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Masukkan password")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setFixedHeight(42)
        self.txt_password.setObjectName("login_input")
        card_layout.addWidget(self.txt_password)

        card_layout.addSpacing(6)

        # Tombol login
        self.btn_login = QPushButton("Masuk")
        self.btn_login.setFixedHeight(44)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setObjectName("btn_login_submit")
        self.btn_login.setFont(QFont("Segoe UI", 10, QFont.Bold))
        card_layout.addWidget(self.btn_login)

        # Baris "Belum punya akun? Daftar di sini"
        switch_row = QHBoxLayout()
        switch_row.setSpacing(4)
        switch_row.addStretch()
        lbl_switch = QLabel("Belum punya akun?")
        lbl_switch.setObjectName("login_switch_label")
        switch_row.addWidget(lbl_switch)
        self.btn_daftar = QPushButton("Daftar di sini")
        self.btn_daftar.setCursor(Qt.PointingHandCursor)
        self.btn_daftar.setObjectName("btn_auth_link")
        switch_row.addWidget(self.btn_daftar)
        switch_row.addStretch()
        card_layout.addLayout(switch_row)

        outer.addWidget(card)
        outer.addStretch(1)

        lbl_hint = QLabel("Pemrograman Visual — Semester Genap 2025/2026")
        lbl_hint.setObjectName("login_footer")
        lbl_hint.setAlignment(Qt.AlignCenter)
        outer.addWidget(lbl_hint)

    def _login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Gagal", "Username dan password tidak boleh kosong.")
            return

        if verifikasi_login(username, password):
            self.login_success.emit()
        else:
            QMessageBox.warning(self, "Login Gagal", "Username atau password salah.")
            self.txt_password.clear()
            self.txt_password.setFocus()

    def reset_form(self):
        """Bersihkan form, dipanggil saat kembali ke halaman login (mis. setelah logout)."""
        self.txt_username.clear()
        self.txt_password.clear()
        self.txt_username.setFocus()
