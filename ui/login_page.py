from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QLabel, 
    QLineEdit, 
    QPushButton, 
    QMessageBox
)
from PySide6.QtCore import Qt, Signal
from assets import icon, pixmap


class LoginPage(QWidget):
    login_success = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskAI - Login")
        self.setWindowIcon(icon("taskai.png"))
        self.setFixedSize(400, 500)
        self.setup_ui()
        self.btn_login.clicked.connect(self.login)
        self.txt_password.returnPressed.connect(self.login)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(12)

        lbl_logo = QLabel()
        pm = pixmap("taskai.png")
        if not pm.isNull():
            lbl_logo.setPixmap(pm.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lbl_logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_logo)

        lbl_judul = QLabel("TaskAI")
        lbl_judul.setAlignment(Qt.AlignCenter)
        lbl_judul.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(lbl_judul)

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Username")
        self.txt_username.setFixedHeight(40)

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Password")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setFixedHeight(40)

        self.btn_login = QPushButton(icon("login.png"), "Login")
        self.btn_login.setFixedHeight(40)

        layout.addStretch()
        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.txt_username)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.txt_password)
        layout.addSpacing(10)
        layout.addWidget(self.btn_login)
        layout.addStretch()

        self.setLayout(layout)

    def login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Gagal", "Username dan password tidak boleh kosong.")
            return

        if username == "admin" and password == "admin":
            self.login_success.emit()
        else:
            QMessageBox.warning(self, "Login Gagal", "Username atau password salah.")
            self.txt_password.clear()
            self.txt_password.setFocus()