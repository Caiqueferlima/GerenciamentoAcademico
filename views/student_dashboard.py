from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QScrollArea
from database.db import get_session
from database.models import Aluno
from views.dashboard_widgets import MetricCard, Gauge


class StudentDashboard(QWidget):
    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self._build_ui()
        self._carregar_dados()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)
        title = QLabel("Meu desempenho acadêmico")
        title.setObjectName("title")
        root.addWidget(title)
        self.subtitle = QLabel()
        self.subtitle.setObjectName("subtitle")
        root.addWidget(self.subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(14)
        scroll.setWidget(content)
        root.addWidget(scroll)
        self.setStyleSheet("""
            QWidget { background: #f4f7fa; color: #172b3a; }
            QLabel#title { font-size: 24px; font-weight: bold; }
            QLabel#subtitle { color: #526474; font-size: 13px; }
            QScrollArea { border: 0; background: transparent; }
        """)

    def _carregar_dados(self):
        session = get_session()
        try:
            aluno = session.query(Aluno).filter_by(usuario_id=self.usuario["id"]).first()
            if not aluno:
                self.subtitle.setText("Não encontramos dados acadêmicos para este usuário.")
                return
            conclusao = aluno.conclusao
            curso = aluno.curso.nome if aluno.curso else "Bacharelado em Sistemas de Informação"
            situacao = aluno.situacao_matricula or "Não informado"
            self.subtitle.setText(f"{aluno.nome} | Matrícula: {aluno.matricula} | {curso}")

            ano, _, semestre = (aluno.periodo_ingresso or "-/-").partition("/")
            self.content_layout.addLayout(self._cards([
                MetricCard("Situação da matrícula", situacao),
                MetricCard("Período de ingresso", f"{ano}/{semestre}"),
                MetricCard("Carga horária cumprida", self._format_number(conclusao.ch_cumprida if conclusao else None)),
                MetricCard("Carga horária prevista", self._format_number(conclusao.ch_prevista if conclusao else None)),
            ]))

            pct_cumprido = self._number(conclusao.pct_cumprido if conclusao else None)
            ch_obrigatoria = self._number(conclusao.ch_obrigatoria_cumpr if conclusao else None)
            ch_obrigatoria_max = self._number(conclusao.ch_obrigatoria_prev if conclusao else None)
            ch_complementar = self._number(conclusao.ch_complementar_cumpr if conclusao else None)
            ch_complementar_max = self._number(conclusao.ch_complementar_prev if conclusao else None)
            ch_optativa = self._number(conclusao.ch_optativa_cumpr if conclusao else None)
            ch_optativa_max = self._number(conclusao.ch_optativa_prev if conclusao else None)
            gauges = QHBoxLayout()
            gauges.addWidget(Gauge("Percentual concluído", pct_cumprido, 100, f"{pct_cumprido:.1f}%"))
            gauges.addWidget(Gauge("CH obrigatória", ch_obrigatoria, ch_obrigatoria_max, f"{ch_obrigatoria:.0f} h"))
            gauges.addWidget(Gauge("CH complementar", ch_complementar, ch_complementar_max, f"{ch_complementar:.0f} h"))
            gauges.addWidget(Gauge("CH optativa", ch_optativa, ch_optativa_max, f"{ch_optativa:.0f} h"))
            self.content_layout.addLayout(gauges)
        finally:
            session.close()

    def _cards(self, cards):
        grid = QGridLayout()
        grid.setSpacing(10)
        for index, card in enumerate(cards):
            grid.addWidget(card, 0, index)
        return grid

    @staticmethod
    def _number(value):
        return float(value or 0)

    @staticmethod
    def _format_number(value):
        return f"{value}" if value is not None else "Não informado"
