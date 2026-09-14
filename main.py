import sys
from PySide6.QtWidgets import QApplication
from database.db import init_db
from views.login_window import LoginWindow
from views.main_window import MainWindow


class AppController:
    """Controla o fluxo entre janelas (login ↔ área interna)."""

    def __init__(self):
        self.login_window: LoginWindow | None = None
        self.main_window: MainWindow | None = None

    def iniciar(self):
        self.login_window = LoginWindow()
        self.login_window.login_sucesso.connect(self._on_login)
        self.login_window.show()

    def _on_login(self, usuario: dict):
        self.login_window.hide()
        self.main_window = MainWindow(usuario)
        self.main_window.logout_solicitado.connect(self._on_logout)
        self.main_window.show()

    def _on_logout(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        self.login_window.input_senha.clear()
        self.login_window.show()


def main():
    init_db()
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema Acadêmico")
    controller = AppController()
    controller.iniciar()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()