from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QGridLayout, QScrollArea
)
from database.db import get_session
from database.models import Aluno
from views.dashboard_widgets import MetricCard, BarChart, PieChart


class ProfessorDashboard(QWidget):
    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self._build_ui()
        self._carregar_dados()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("SAD - Sistema de Apoio à Decisão")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        self.btn_importar = QPushButton("Importar dados")
        self.btn_importar.setToolTip("Substitui os dados acadêmicos pelo novo conjunto de planilhas")
        self.btn_importar.clicked.connect(self._importar_planilha)
        header.addWidget(self.btn_importar)
        root.addLayout(header)

        subtitle = QLabel(f"Visão geral do curso BSI | Professor: {self.usuario['nome']}")
        subtitle.setObjectName("subtitle")
        root.addWidget(subtitle)

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
            QPushButton { background: #1769aa; color: white; border: 0; border-radius: 5px; padding: 9px 15px; font-weight: bold; }
            QPushButton:hover { background: #125488; }
            QScrollArea { border: 0; background: transparent; }
        """)

    def _card_grid(self, cards):
        grid = QGridLayout()
        grid.setSpacing(10)
        for index, card in enumerate(cards):
            grid.addWidget(card, index // 3, index % 3)
        self.content_layout.addLayout(grid)

    def _carregar_dados(self):
        session = get_session()
        try:
            alunos = session.query(Aluno).all()
            total = len(alunos)
            matriculados = sum(1 for aluno in alunos if aluno.situacao_matricula == "Matriculado")
            formados = sum(1 for aluno in alunos if aluno.situacao_matricula == "Formado")
            abandono = sum(1 for aluno in alunos if aluno.situacao_matricula == "Abandono")
            trancados = sum(1 for aluno in alunos if aluno.situacao_matricula == "Trancado")
            pct = lambda value, denominator=total: value / denominator * 100 if denominator else 0
            sem_matriculados_den = total - matriculados

            self._limpar_graficos()
            self._card_grid([
                MetricCard("Total geral de alunos", str(total)),
                MetricCard("Alunos matriculados", str(matriculados)),
                MetricCard("Percentual de conclusão geral", f"{pct(formados):.2f}%"),
                MetricCard("Conclusão sem matriculados", f"{pct(formados, sem_matriculados_den):.2f}%"),
                MetricCard("Percentual de abandono", f"{pct(abandono):.2f}%"),
                MetricCard("Percentual de trancamento", f"{pct(trancados):.2f}%"),
            ])

            charts = QHBoxLayout()
            situacoes = {}
            for aluno in alunos:
                situacao = aluno.situacao_matricula or "Não informado"
                situacoes[situacao] = situacoes.get(situacao, 0) + 1
            situacoes = dict(sorted(situacoes.items(), key=lambda item: item[1], reverse=True))
            charts.addWidget(BarChart("Contagem de alunos por situação da matrícula", situacoes), 2)
            sexos = {"M": sum(1 for a in alunos if getattr(a.sexo, "value", a.sexo) == "M"),
                     "F": sum(1 for a in alunos if getattr(a.sexo, "value", a.sexo) == "F")}
            sexos = {key: value for key, value in sexos.items() if value}
            charts.addWidget(PieChart("Contagem de alunos por sexo", sexos), 1)
            self.content_layout.addLayout(charts)
        finally:
            session.close()

    def _limpar_graficos(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._limpar_layout(item.layout())

    def _limpar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._limpar_layout(item.layout())

    def _importar_planilha(self):
        caminhos, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecione as planilhas acadêmicas",
            "",
            "Planilhas acadêmicas (*.xlsx *.xls *.csv);;Todos os arquivos (*)",
        )
        if not caminhos:
            return
        from utils.excel_importer import importar_varios
        resultados = importar_varios(caminhos, substituir=True)
        partes = ["<b>Atualização concluída</b><br>"]
        for resultado in resultados:
            partes.extend([resultado.resumo(), ""])
        QMessageBox.information(self, "Resultado da importação", "<br>".join(partes))
        self._carregar_dados()
