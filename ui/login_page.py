from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)

from PySide6.QtCore import Qt


class LoginPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()

        self.btn_login.clicked.connect(
            self.login
        )

    def setup_ui(self):

        layout = QVBoxLayout()

        self.lbl_judul = QLabel(
            "TaskAI Login"
        )

        self.lbl_judul.setAlignment(
            Qt.AlignCenter
        )

        self.txt_username = QLineEdit()

        self.txt_username.setPlaceholderText(
            "Username"
        )

        self.txt_password = QLineEdit()

        self.txt_password.setPlaceholderText(
            "Password"
        )

        self.txt_password.setEchoMode(
            QLineEdit.Password
        )

        self.btn_login = QPushButton(
            "Login"
        )

        layout.addWidget(
            self.lbl_judul
        )

        layout.addWidget(
            self.txt_username
        )

        layout.addWidget(
            self.txt_password
        )

        layout.addWidget(
            self.btn_login
        )

        layout.addStretch()

        self.setLayout(
            layout
        )

    def login(self):

        username = self.txt_username.text().strip()

        password = self.txt_password.text().strip()

        if username == "admin" and password == "admin":

            QMessageBox.information(
                self,
                "Berhasil",
                "Login berhasil"
            )

        else:

            QMessageBox.warning(
                self,
                "Login Gagal",
                "Username atau password salah"
            )