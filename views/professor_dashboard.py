from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QHeaderView, QFrame
)
from database.db import get_session
from database.models import Aluno


class ProfessorDashboard(QWidget):
    def __init__(self, usuario: dict):
        super().__init__()
        self.usuario = usuario
        self._build_ui()
        self._carregar_dados()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        header = QLabel(f"👨‍🏫 Área do Professor — Olá, {self.usuario['nome']}")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)

        # Barra de ações
        acoes = QHBoxLayout()
        self.btn_importar = QPushButton("📥 Importar Planilha de Alunos")
        self.btn_importar.clicked.connect(self._importar_planilha)
        acoes.addWidget(self.btn_importar)
        acoes.addStretch()
        layout.addLayout(acoes)

        # Filtros
        filtros = QHBoxLayout()
        filtros.addWidget(QLabel("Ano de ingresso:"))
        self.combo_ano = QComboBox()
        self.combo_ano.addItem("Todos", None)
        self.combo_ano.currentIndexChanged.connect(self._carregar_dados)
        filtros.addWidget(self.combo_ano)

        filtros.addWidget(QLabel("Semestre:"))
        self.combo_semestre = QComboBox()
        self.combo_semestre.addItem("Todos", None)
        self.combo_semestre.addItem("1º", 1)
        self.combo_semestre.addItem("2º", 2)
        self.combo_semestre.currentIndexChanged.connect(self._carregar_dados)
        filtros.addWidget(self.combo_semestre)
        filtros.addStretch()
        layout.addLayout(filtros)

        # Painel de estatísticas
        self.frame_stats = QFrame()
        self.frame_stats.setStyleSheet(
            "background-color: #eef4fb; border-radius: 8px; padding: 12px;"
        )
        stats_layout = QVBoxLayout()
        self.label_stats = QLabel()
        self.label_stats.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(self.label_stats)
        self.frame_stats.setLayout(stats_layout)
        layout.addWidget(self.frame_stats)

        # Tabela de alunos
        layout.addWidget(QLabel("Alunos:"))
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(
            ["Matrícula", "Nome", "E-mail", "Ano", "Semestre", "Horas Compl."]
        )
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela)

        self.setLayout(layout)
        self.setStyleSheet(
            """
            QWidget { background-color: #f7f9fc; color: #243447; }
            QLabel { color: #243447; }
            QPushButton {
                background-color: #1769aa;
                color: #ffffff;
                border: 1px solid #125488;
                border-radius: 4px;
                padding: 7px 12px;
            }
            QPushButton:hover { background-color: #125488; }
            QComboBox {
                background-color: #ffffff;
                color: #243447;
                border: 1px solid #b8c4d1;
                border-radius: 4px;
                padding: 5px 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #243447;
                selection-background-color: #d8eaf8;
                selection-color: #172b3a;
            }
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

    # ------------------------------------------------------------------
    def _carregar_dados(self):
        session = get_session()
        try:
            # Atualiza a lista de anos disponíveis (mantendo a seleção atual)
            anos = sorted({
                a[0].split("/", 1)[0]
                for a in session.query(Aluno.periodo_ingresso).distinct().all()
                if a[0] and "/" in a[0]
            })
            selecao_atual = self.combo_ano.currentData()
            self.combo_ano.blockSignals(True)
            self.combo_ano.clear()
            self.combo_ano.addItem("Todos", None)
            for ano in anos:
                self.combo_ano.addItem(str(ano), ano)
            idx = self.combo_ano.findData(selecao_atual)
            if idx >= 0:
                self.combo_ano.setCurrentIndex(idx)
            self.combo_ano.blockSignals(False)

            # Aplica filtros
            query = session.query(Aluno)
            ano_f = self.combo_ano.currentData()
            sem_f = self.combo_semestre.currentData()
            if ano_f:
                query = query.filter(Aluno.periodo_ingresso.like(f"{ano_f}/%"))
            if sem_f:
                query = query.filter(Aluno.periodo_ingresso.like(f"%/{sem_f}"))

            alunos = query.all()

            total = len(alunos)
            com_horas = sum(
                1 for a in alunos
                if a.conclusao and a.conclusao.ch_complementar_cumpr is not None
                and a.conclusao.ch_complementar_prev is not None
                and a.conclusao.ch_complementar_cumpr >= a.conclusao.ch_complementar_prev
            )
            pendentes = total - com_horas
            taxa = (com_horas / total * 100) if total else 0

            self.label_stats.setText(
                f"<b>Total de alunos (filtro atual):</b> {total} &nbsp;|&nbsp; "
                f"<b>Horas complementares OK:</b> {com_horas} &nbsp;|&nbsp; "
                f"<b>Pendentes:</b> {pendentes} &nbsp;|&nbsp; "
                f"<b>Taxa de conclusão (horas):</b> {taxa:.1f}%"
            )

            self.tabela.setRowCount(0)
            for i, a in enumerate(alunos):
                self.tabela.insertRow(i)
                self.tabela.setItem(i, 0, QTableWidgetItem(a.matricula))
                self.tabela.setItem(i, 1, QTableWidgetItem(a.usuario.nome))
                self.tabela.setItem(i, 2, QTableWidgetItem(a.usuario.login if a.usuario else "-"))
                ano, _, semestre = (a.periodo_ingresso or "-/-").partition("/")
                self.tabela.setItem(i, 3, QTableWidgetItem(ano or "-"))
                self.tabela.setItem(i, 4, QTableWidgetItem(semestre or "-"))
                self.tabela.setItem(
                    i, 5,
                    QTableWidgetItem("✔ OK" if a.conclusao and a.conclusao.ch_complementar_cumpr is not None
                                     and a.conclusao.ch_complementar_prev is not None
                                     and a.conclusao.ch_complementar_cumpr >= a.conclusao.ch_complementar_prev
                                     else "⏳ Pendente")
                )
        finally:
            session.close()

    # ------------------------------------------------------------------
    def _importar_planilha(self):
        caminhos, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecione as planilhas (pode marcar várias)",
            "",
            "Planilhas Excel (*.xlsx *.xls)",
        )
        if not caminhos:
            return

        from utils.excel_importer import importar_varios
        resultados = importar_varios(caminhos)

        partes = ["<b>Importação concluída</b><br>"]
        for resultado in resultados:
            partes.append(resultado.resumo())
            partes.append("")

        QMessageBox.information(self, "Resultado", "<br>".join(partes))
        self._carregar_dados()