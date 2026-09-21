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
        toolbar.setStyleSheet("""
            QToolBar { background: #101e2e; border: 0; border-bottom: 1px solid #2c4058; spacing: 8px; padding: 6px 12px; }
            QToolButton { color: #dce8f5; background: transparent; padding: 6px 10px; }
            QToolButton:hover { background: #1c3148; border-radius: 5px; }
        """)

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