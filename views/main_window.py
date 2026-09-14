from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal


class MainWindow(QMainWindow):
    logout_solicitado = Signal()

    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle(f"Sistema Acadêmico — {usuario['nome']} ({usuario['perfil']})")
        self.setMinimumSize(1000, 650)

        toolbar = self.addToolBar("Principal")
        toolbar.setMovable(False)

        acao_logout = QAction("🚪 Encerrar sessão", self)
        acao_logout.triggered.connect(self._logout)
        toolbar.addAction(acao_logout)

        if usuario["perfil"] == "PROFESSOR":
            from views.professor_dashboard import ProfessorDashboard
            self.setCentralWidget(ProfessorDashboard(usuario))
        else:
            from views.student_dashboard import StudentDashboard
            self.setCentralWidget(StudentDashboard(usuario))

    def _logout(self):
        resp = QMessageBox.question(
            self, "Encerrar sessão",
            "Deseja realmente sair do sistema?",
        )
        # QMessageBox.question retorna StandardButton
        from PySide6.QtWidgets import QMessageBox as MB
        if resp == MB.StandardButton.Yes:
            self.logout_solicitado.emit()