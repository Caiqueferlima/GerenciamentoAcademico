from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from controllers.auth_controller import cadastrar_usuario


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro de Professor")
        self.setMinimumSize(420, 420)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(30, 20, 30, 20)

        titulo = QLabel("Cadastrar professor")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; padding: 5px;")
        layout.addWidget(titulo)

        layout.addWidget(QLabel("Nome completo:"))
        self.input_nome = QLineEdit()
        layout.addWidget(self.input_nome)

        layout.addWidget(QLabel("E-mail:"))
        self.input_email = QLineEdit()
        layout.addWidget(self.input_email)

        layout.addWidget(QLabel("Senha:"))
        self.input_senha = QLineEdit()
        self.input_senha.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_senha)

        layout.addWidget(QLabel("Confirme a senha:"))
        self.input_senha2 = QLineEdit()
        self.input_senha2.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_senha2)

        layout.addWidget(QLabel("Número de SIAPE:"))
        self.input_siape = QLineEdit()
        self.input_siape.setPlaceholderText("Informe o número de SIAPE")
        layout.addWidget(self.input_siape)

        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setStyleSheet("padding: 8px; font-weight: bold;")
        self.btn_cadastrar.clicked.connect(self._cadastrar)
        layout.addWidget(self.btn_cadastrar)

        self.setLayout(layout)

    def _cadastrar(self):
        nome = self.input_nome.text().strip()
        email = self.input_email.text().strip()
        senha = self.input_senha.text()
        senha2 = self.input_senha2.text()
        siape = self.input_siape.text().strip()

        if not nome or not email or not senha:
            QMessageBox.warning(self, "Campos obrigatórios", "Preencha nome, e-mail e senha.")
            return
        if "@" not in email:
            QMessageBox.warning(self, "E-mail inválido", "Informe um e-mail válido.")
            return
        if len(senha) < 4:
            QMessageBox.warning(self, "Senha curta", "A senha deve ter ao menos 4 caracteres.")
            return
        if senha != senha2:
            QMessageBox.warning(self, "Senhas diferentes", "As senhas não coincidem.")
            return

        if not siape:
            QMessageBox.warning(self, "SIAPE obrigatório", "Informe o número de SIAPE.")
            return

        _, erro = cadastrar_usuario(nome, email, senha, siape)
        if erro:
            QMessageBox.critical(self, "Erro no cadastro", erro)
            return

        QMessageBox.information(self, "Sucesso", "Usuário cadastrado com sucesso!")
        self.close()