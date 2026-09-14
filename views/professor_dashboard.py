from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QHeaderView, QFrame
)
from database.db import get_session
from database.models import Aluno
from utils.excel_importer import importar_alunos


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

    # ------------------------------------------------------------------
    def _carregar_dados(self):
        session = get_session()
        try:
            # Atualiza a lista de anos disponíveis (mantendo a seleção atual)
            anos = sorted({
                a[0] for a in session.query(Aluno.ano_ingresso).distinct().all()
                if a[0]
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
                query = query.filter(Aluno.ano_ingresso == ano_f)
            if sem_f:
                query = query.filter(Aluno.semestre_ingresso == sem_f)

            alunos = query.all()

            total = len(alunos)
            com_horas = sum(1 for a in alunos if a.horas_complementares_ok)
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
                self.tabela.setItem(i, 2, QTableWidgetItem(a.usuario.email))
                self.tabela.setItem(i, 3, QTableWidgetItem(str(a.ano_ingresso or "-")))
                self.tabela.setItem(i, 4, QTableWidgetItem(str(a.semestre_ingresso or "-")))
                self.tabela.setItem(
                    i, 5,
                    QTableWidgetItem("✔ OK" if a.horas_complementares_ok else "⏳ Pendente")
                )
        finally:
            session.close()

    # ------------------------------------------------------------------
    def _importar_planilha(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecione a planilha de alunos", "",
            "Planilhas Excel (*.xlsx *.xls)"
        )
        if not caminho:
            return

        try:
            inseridos, ignorados, erros = importar_alunos(caminho)
        except Exception as e:
            QMessageBox.critical(self, "Erro na importação", str(e))
            return

        msg = (
            f"<b>Importação concluída!</b><br><br>"
            f"Alunos inseridos: <b>{inseridos}</b><br>"
            f"Ignorados (já existiam): <b>{ignorados}</b>"
        )
        if erros:
            msg += f"<br><br><b>Erros ({len(erros)}):</b><br>" + "<br>".join(erros[:5])
        QMessageBox.information(self, "Resultado", msg)
        self._carregar_dados()