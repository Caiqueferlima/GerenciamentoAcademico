from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from database.db import get_session
from database.models import Aluno


class StudentDashboard(QWidget):
    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self._build_ui()
        self._carregar_dados()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel(f"🎒 Área do Aluno — Olá, {self.usuario['nome']}")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)

        # Painel de informações do aluno
        self.frame_info = QFrame()
        self.frame_info.setStyleSheet(
            "background-color: #f0f8ff; border-radius: 8px; padding: 15px;"
        )
        info_layout = QVBoxLayout()
        self.label_info = QLabel()
        self.label_info.setStyleSheet("font-size: 13px; line-height: 1.5;")
        # ← linha removida; o QLabel já detecta HTML automaticamente
        info_layout.addWidget(self.label_info)
        self.frame_info.setLayout(info_layout)
        layout.addWidget(self.frame_info)

        # Tabela de disciplinas
        layout.addWidget(QLabel("Minhas disciplinas:"))
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(
            ["Disciplina", "Ano/Semestre", "Nota", "Situação"]
        )
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela)

        self.setLayout(layout)
        self.setStyleSheet(
            """
            QWidget { background-color: #f7f9fc; color: #243447; }
            QLabel { color: #243447; }
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f2f6fa;
                color: #243447;
                gridline-color: #d5dde5;
                selection-background-color: #cfe5f5;
                selection-color: #172b3a;
            }
            QTableWidget QHeaderView::section {
                background-color: #dce8f2;
                color: #172b3a;
                border: 1px solid #c4d1dc;
                padding: 6px;
                font-weight: bold;
            }
            """
        )

    def _carregar_dados(self):
        session = get_session()
        try:
            aluno = session.query(Aluno).filter_by(usuario_id=self.usuario["id"]).first()
            if not aluno:
                self.label_info.setText("⚠ Dados de aluno não encontrados.")
                return

            curso_nome = aluno.curso.nome if aluno.curso else "—"
            conclusao = aluno.conclusao
            horas_ok = (
                conclusao is not None
                and conclusao.ch_complementar_cumpr is not None
                and conclusao.ch_complementar_prev is not None
                and conclusao.ch_complementar_cumpr >= conclusao.ch_complementar_prev
            )
            horas_status = "✔ Concluídas" if horas_ok else "⏳ Pendentes"
            ano, _, semestre = (aluno.periodo_ingresso or "—/—").partition("/")

            self.label_info.setText(
                f"<b>Matrícula:</b> {aluno.matricula}<br>"
                f"<b>Curso:</b> {curso_nome}<br>"
                f"<b>Ingresso:</b> {ano or '—'} / "
                f"{semestre or '—'}º semestre<br>"
                f"<b>Horas complementares:</b> {horas_status}"
            )

            self.tabela.setRowCount(0)
            for i, pendencia in enumerate(aluno.pendencias):
                self.tabela.insertRow(i)
                self.tabela.setItem(i, 0, QTableWidgetItem(pendencia.disciplina.nome))
                self.tabela.setItem(
                    i, 1,
                    QTableWidgetItem("Pendente")
                )
                self.tabela.setItem(i, 2, QTableWidgetItem("—"))
                self.tabela.setItem(i, 3, QTableWidgetItem("Pendente"))
        finally:
            session.close()