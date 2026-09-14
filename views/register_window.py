from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from controllers.auth_controller import cadastrar_usuario


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro de Usuário")
        self.setMinimumSize(420, 520)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(30, 20, 30, 20)

        titulo = QLabel("Criar conta")
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

        layout.addWidget(QLabel("Perfil:"))
        self.combo_perfil = QComboBox()
        self.combo_perfil.addItem("Aluno", "ALUNO")
        self.combo_perfil.addItem("Professor", "PROFESSOR")
        self.combo_perfil.currentIndexChanged.connect(self._atualizar_campos)
        layout.addWidget(self.combo_perfil)

        # --- Campos específicos de Aluno ---
        self.label_matricula = QLabel("Matrícula:")
        self.input_matricula = QLineEdit()
        layout.addWidget(self.label_matricula)
        layout.addWidget(self.input_matricula)

        self.label_ano = QLabel("Ano de ingresso:")
        self.input_ano = QLineEdit()
        self.input_ano.setPlaceholderText("Ex: 2023")
        layout.addWidget(self.label_ano)
        layout.addWidget(self.input_ano)

        self.label_semestre = QLabel("Semestre de ingresso:")
        self.combo_semestre = QComboBox()
        self.combo_semestre.addItem("1º semestre", 1)
        self.combo_semestre.addItem("2º semestre", 2)
        layout.addWidget(self.label_semestre)
        layout.addWidget(self.combo_semestre)

        # --- Campo específico de Professor ---
        self.label_departamento = QLabel("Departamento:")
        self.input_departamento = QLineEdit()
        layout.addWidget(self.label_departamento)
        layout.addWidget(self.input_departamento)

        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setStyleSheet("padding: 8px; font-weight: bold;")
        self.btn_cadastrar.clicked.connect(self._cadastrar)
        layout.addWidget(self.btn_cadastrar)

        self.setLayout(layout)
        self._atualizar_campos()

    def _atualizar_campos(self):
        is_aluno = self.combo_perfil.currentData() == "ALUNO"
        for w in (self.label_matricula, self.input_matricula,
                  self.label_ano, self.input_ano,
                  self.label_semestre, self.combo_semestre):
            w.setVisible(is_aluno)
        for w in (self.label_departamento, self.input_departamento):
            w.setVisible(not is_aluno)

    def _cadastrar(self):
        nome = self.input_nome.text().strip()
        email = self.input_email.text().strip()
        senha = self.input_senha.text()
        senha2 = self.input_senha2.text()
        perfil = self.combo_perfil.currentData()

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

        kwargs = {}
        if perfil == "ALUNO":
            matricula = self.input_matricula.text().strip()
            if not matricula:
                QMessageBox.warning(self, "Matrícula obrigatória", "Informe a matrícula.")
                return
            ano_txt = self.input_ano.text().strip()
            ano = int(ano_txt) if ano_txt.isdigit() else None
            kwargs = {
                "matricula": matricula,
                "ano": ano,
                "semestre": self.combo_semestre.currentData(),
            }
        else:
            kwargs = {"departamento": self.input_departamento.text().strip()}

        _, erro = cadastrar_usuario(nome, email, senha, perfil, **kwargs)
        if erro:
            QMessageBox.critical(self, "Erro no cadastro", erro)
            return

        QMessageBox.information(self, "Sucesso", "Usuário cadastrado com sucesso!")
        self.close()