from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from controllers.auth_controller import autenticar


class LoginWindow(QWidget):
    login_sucesso = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Acadêmico — Login")
        self.setMinimumSize(400, 320)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("🎓 Sistema Acadêmico")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 22px; font-weight: bold; padding: 5px;")
        layout.addWidget(titulo)

        subtitulo = QLabel("Faça login para continuar")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(subtitulo)

        layout.addWidget(QLabel("E-mail:"))
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("seu@email.com")
        layout.addWidget(self.input_email)

        layout.addWidget(QLabel("Senha:"))
        self.input_senha = QLineEdit()
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.returnPressed.connect(self._fazer_login)
        layout.addWidget(self.input_senha)

        self.btn_login = QPushButton("Entrar")
        self.btn_login.setStyleSheet("padding: 8px; font-weight: bold;")
        self.btn_login.clicked.connect(self._fazer_login)
        layout.addWidget(self.btn_login)

        self.btn_cadastro = QPushButton("Não tenho conta — Cadastrar")
        self.btn_cadastro.clicked.connect(self._abrir_cadastro)
        layout.addWidget(self.btn_cadastro)

        self.setLayout(layout)

    def _fazer_login(self):
        email = self.input_email.text().strip()
        senha = self.input_senha.text()

        if not email or not senha:
            QMessageBox.warning(self, "Campos obrigatórios", "Informe e-mail e senha.")
            return

        usuario, erro = autenticar(email, senha)
        if erro:
            QMessageBox.critical(self, "Falha no login", erro)
            return

        QMessageBox.information(self, "Bem-vindo", f"Login realizado com sucesso!\nOlá, {usuario['nome']}.")
        self.input_senha.clear()
        self.login_sucesso.emit(usuario)

    def _abrir_cadastro(self):
        from views.register_window import RegisterWindow
        self.register_window = RegisterWindow()
        self.register_window.show()