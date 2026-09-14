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

    def _carregar_dados(self):
        session = get_session()
        try:
            aluno = session.query(Aluno).filter_by(usuario_id=self.usuario["id"]).first()
            if not aluno:
                self.label_info.setText("⚠ Dados de aluno não encontrados.")
                return

            curso_nome = aluno.curso.nome if aluno.curso else "—"
            horas_status = "✔ Concluídas" if aluno.horas_complementares_ok else "⏳ Pendentes"

            self.label_info.setText(
                f"<b>Matrícula:</b> {aluno.matricula}<br>"
                f"<b>Curso:</b> {curso_nome}<br>"
                f"<b>Ingresso:</b> {aluno.ano_ingresso or '—'} / "
                f"{aluno.semestre_ingresso or '—'}º semestre<br>"
                f"<b>Horas complementares:</b> {horas_status}"
            )

            self.tabela.setRowCount(0)
            for i, m in enumerate(aluno.matriculas):
                self.tabela.insertRow(i)
                self.tabela.setItem(i, 0, QTableWidgetItem(m.disciplina.nome))
                self.tabela.setItem(
                    i, 1,
                    QTableWidgetItem(f"{m.ano or '—'}/{m.semestre or '—'}")
                )
                self.tabela.setItem(
                    i, 2,
                    QTableWidgetItem(
                        f"{m.nota_final:.1f}" if m.nota_final is not None else "—"
                    )
                )
                self.tabela.setItem(i, 3, QTableWidgetItem(m.situacao.value))
        finally:
            session.close()