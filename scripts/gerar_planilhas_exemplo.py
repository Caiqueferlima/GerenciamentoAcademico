"""Gera 4 planilhas .xlsx no mesmo formato dos arquivos da coordenação
para você testar a importação sem precisar dos originais."""
from pathlib import Path
import pandas as pd

SAIDA = Path(__file__).resolve().parent.parent / "exemplos"
SAIDA.mkdir(exist_ok=True)


def _alunos_sem_periodo():
    dados = [
        # matrícula, nome, sexo, período ingresso, situação, turno, ...
        ("20231035000017", "CAIQUE FERNANDES DE LIMA", "M", "2023/1", "Matriculado", "Matutino", "Vespertino", 6, "Pública Estadual", "Urbana", "RFP <= 0,5 SM"),
        ("20221035000320", "ALEF MOREIRA GOUVEIA DE SOUSA", "M", "2022/1", "Matriculado", "Vespertino", "Noturno", 8, "Pública Estadual", "Urbana", "0,5 SM < RFP <= 1 SM"),
        ("20171035000222", "ALEX ALVES DOS SANTOS", "M", "2017/1", "Formado", "Noturno", "Noturno", 8, "Pública Estadual", "Urbana", ""),
        ("20191035000065", "ALEXANDRE DE LIMA PINHEIRO", "M", "2019/1", "Abandono", "Noturno", "Noturno", 1, "Pública Municipal", "Urbana", ""),
    ]
    df = pd.DataFrame(dados, columns=[
        "Matrícula", "Nome", "Sexo", "Per. Let. Inigresso", "Situação Matrícula",
        "Turno", "Turno Ingresso", "Qtd Períodos", "Escola de Origem",
        "Area Procedência Escola Origem", "Renda Familiar Per Capita",
    ])
    df.to_excel(SAIDA / "AlunosSemPeriodo.xlsx", index=False)


def _matricula_ativa():
    dados = [
        ("20231035000017", "CAIQUE FERNANDES DE LIMA", "M", "Matriculado", "Matriculado",
         "2023/1", "Matutino", "Bacharelado em Sistemas de Informação", 6, "Vespertino",
         "Reabertura de Matrícula", "Até 1 salário", "Ampla Concorrência",
         "RFP <= 0,5 SM", "Pública Estadual", "Urbana", "2 - CAMPUS CEDRO"),
        ("20221035000320", "ALEF MOREIRA GOUVEIA DE SOUSA", "M", "Matriculado", "Matriculado",
         "2022/1", "Vespertino", "Bacharelado em Sistemas de Informação", 8, "Noturno",
         "Renovação por Aprovação", "1 a 2 salários", "Não possui",
         "0,5 SM < RFP <= 1 SM", "Pública Estadual", "Urbana", "2 - CAMPUS CEDRO"),
        ("20171035000222", "ALEX ALVES DOS SANTOS", "M", "Formado", "Concluiu",
         "2017/1", "Noturno", "Bacharelado em Sistemas de Informação", 8, "Noturno",
         "Renovação por Aprovação", "", "L2 Esc Publica, Renda<1.5sm, Raca",
         "", "Pública Estadual", "Urbana", "2 - CAMPUS CEDRO"),
        ("20191035000065", "ALEXANDRE DE LIMA PINHEIRO", "M", "Abandono", "Abandonou",
         "2019/1", "Noturno", "Bacharelado em Sistemas de Informação", 1, "Noturno",
         "Renovação por Aprovação", "", "Ampla Concorrência",
         "", "Pública Municipal", "Urbana", "2 - CAMPUS CEDRO"),
    ]
    df = pd.DataFrame(dados, columns=[
        "Matrícula", "Nome", "Sexo", "Situação Matrícula", "Situação Período",
        "Per. Letivo Inicial", "Turno Ingresso", "Curso", "Período", "Turno",
        "Tipo Forma Ingresso no Período", "Renda Familiar", "Cota",
        "Renda Familiar Per Capita", "Escola de Origem",
        "Area Procedência Escola Origem", "Agrupamento",
    ])
    df.to_excel(SAIDA / "MatriculaAtiva.xlsx", index=False)


def _percentual():
    cols = [
        "Matrícula", "Nome", "Per. Letivo Inicial", "Curso", "Período",
        "C.H. Prevista", "C.H. Cumprida", "% Cumprido",
        "Cr. Prev.", "Cr. Cumpr.", "% Cr. Cumprido",
        "Ano Conclusão Grad.", "Ano Conclusão Pós-Grad.",
        "C.H. Obrigatória Prev.", "C.H. Obrigatório Cumpr.",
        "C.H. Optativa Prev.", "C.H. Optativa Cumpr.",
        "C.H. Complementar Prev.", "C.H. Complementar Cumpr.",
        "C.H. Projeto Prev.", "C.H. Projeto Cumpr.",
        "C.H. Estágio Prev.", "C.H. Estágio Cumpr.",
        "C.H. Eletiva Prev.", "C.H. Eletiva Cump.",
        "Cr. Obrigatório Prev.", "Cr. Obrigatório Cumpr.",
        "Cr. Optativo Prev.", "Cr. Optativo Cumpr.",
        "Situação Período", "Situação Matrícula",
    ]
    dados = [
        ("20231035000017", "CAIQUE FERNANDES DE LIMA", "2023/1", "03500", 6,
         3400, 2240, "65,88", 156, 102, "65,38",
         None, None,
         3120, 2040, 80, 0, 200, 200, 0, 0, 0, 0, 0, 0,
         156, 102, 0, 0, "Matriculado", "Matriculado"),
        ("20221035000320", "ALEF MOREIRA GOUVEIA DE SOUSA", "2022/1", "03500", 8,
         3400, 3080, "90,59", 156, 150, "96,15",
         None, None,
         3120, 3000, 80, 80, 200, 0, 0, 0, 0, 0, 0, 0,
         156, 150, 0, 0, "Matriculado", "Matriculado"),
    ]
    df = pd.DataFrame(dados, columns=cols)
    df.to_excel(SAIDA / "PercentualDeConclusão.xlsx", index=False)


def _pendentes():
    dados = [
        ("03500.45", "TRABALHO DE CONCLUSÃO DE CURSO", "20231035000017", "CAIQUE FERNANDES DE LIMA", "03500 - Bacharelado em Sistemas de Informação"),
        ("03500.32", "PROJETO INTEGRADOR I", "20231035000017", "CAIQUE FERNANDES DE LIMA", "03500 - Bacharelado em Sistemas de Informação"),
        ("03500.45", "TRABALHO DE CONCLUSÃO DE CURSO", "20221035000320", "ALEF MOREIRA GOUVEIA DE SOUSA", "03500 - Bacharelado em Sistemas de Informação"),
    ]
    df = pd.DataFrame(dados, columns=["Sigla", "Disciplina", "Matrícula", "Nome do Aluno", "Curso"])
    df.to_excel(SAIDA / "DisciplinasPendentes.xlsx", index=False)


if __name__ == "__main__":
    _alunos_sem_periodo()
    _matricula_ativa()
    _percentual()
    _pendentes()
    print(f"Planilhas geradas em {SAIDA}")