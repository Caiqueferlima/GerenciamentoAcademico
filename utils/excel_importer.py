"""
Importador dos 4 relatórios do sistema acadêmico.

Detecta o tipo pelo nome do arquivo e faz upsert por matrícula.
"""
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from database.db import get_session
from database.models import (
    Usuario, Aluno, Curso, Disciplina, Pendencia, Conclusao,
    PerfilEnum, SexoEnum,
)
from utils.security import hash_senha


CURSO_PADRAO = ("03500", "Bacharelado em Sistemas de Informação")


# --------------------------------------------------------------------- utils
@dataclass
class ImportResult:
    tipo: str = ""
    inseridos: int = 0
    atualizados: int = 0
    ignorados: int = 0
    erros: list = field(default_factory=list)

    def resumo(self) -> str:
        linhas = [f"<b>{self.tipo}</b>"]
        linhas.append(f"Inseridos: {self.inseridos}")
        linhas.append(f"Atualizados: {self.atualizados}")
        if self.ignorados:
            linhas.append(f"Ignorados: {self.ignorados}")
        if self.erros:
            linhas.append(f"Erros ({len(self.erros)}):")
            linhas.extend(self.erros[:5])
        return "<br>".join(linhas)


def _to_int(v):
    """Converte '9,4118' → 9, '10.26' → 10, '' → None."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip().replace(",", ".")
    try:
        return int(round(float(s)))
    except (ValueError, TypeError):
        return None


def _to_str(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    return s if s and s.lower() != "nan" else None


def _limpar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
    return df


def _ler_planilha(caminho: Path) -> pd.DataFrame:
    """Lê Excel ou CSV, incluindo exportações do relatório de pendências."""
    if caminho.suffix.lower() == ".csv":
        df = _limpar_colunas(pd.read_csv(caminho, sep=None, engine="python"))
    else:
        df = _limpar_colunas(pd.read_excel(caminho))

    # Algumas exportações de pendências chegam sem a linha de cabeçalho.
    if _detectar_tipo(caminho.name) == "disciplinas_pendentes" and "Sigla" not in df.columns:
        if len(df.columns) >= 5:
            df = df.iloc[:, :5].copy()
            df.columns = ["Sigla", "Disciplina", "Matrícula", "Nome do Aluno", "Curso"]
    return df


def _normalizar_coluna(nome: str) -> str:
    texto = unicodedata.normalize("NFKD", str(nome))
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]", "", texto.lower())


def _get_col(row, *nomes):
    """Retorna o primeiro valor não-nulo dentre os nomes de coluna."""
    for nome in nomes:
        if nome in row and pd.notna(row[nome]):
            return row[nome]
    return None


def _curso_codigo_da_matricula(matricula: str) -> str:
    """20231035000017 → '03500'."""
    if len(matricula) >= 10:
        return matricula[5:10]
    return CURSO_PADRAO[0]


def _garantir_curso(session) -> Curso:
    curso = session.get(Curso, CURSO_PADRAO[0])
    if not curso:
        curso = Curso(codigo=CURSO_PADRAO[0], nome=CURSO_PADRAO[1])
        session.add(curso)
        session.flush()
    return curso


def _criar_usuario_para_aluno(session, aluno: Aluno):
    """Cria Usuario com login=matrícula e senha=últimos 4 dígitos."""
    if aluno.usuario_id:
        return
    login = aluno.matricula
    if session.query(Usuario).filter_by(login=login).first():
        return
    senha = aluno.matricula[-4:]
    usuario = Usuario(
        login=login,
        nome=aluno.nome,
        senha_hash=hash_senha(senha),
        perfil=PerfilEnum.ALUNO,
        precisa_trocar_senha=True,
    )
    session.add(usuario)
    session.flush()
    aluno.usuario_id = usuario.id


# ------------------------------------------------------------ tipo de arquivo
def _detectar_tipo(nome_arquivo: str) -> str:
    n = nome_arquivo.lower()
    if "listagem_alunos_sem" in n or "alunossemperiodo" in n:
        return "alunos_sem_periodo"
    if "listagem_alunos1" in n or "matriculaativa" in n:
        return "matricula_ativa"
    if "percentual" in n and "conclus" in n:
        return "percentual_conclusao"
    if "disciplinas_pendentes" in n or "disciplinaspendentes" in n:
        return "disciplinas_pendentes"
    return "desconhecido"


def _detectar_tipo_por_colunas(colunas) -> str:
    """Reconhece relatórios mesmo quando o usuário renomeia o arquivo."""
    colunas = {_normalizar_coluna(coluna) for coluna in colunas}
    if {"sigla", "disciplina", "matricula"}.issubset(colunas):
        return "disciplinas_pendentes"
    if "chprevista" in colunas and "cumprido" in colunas:
        return "percentual_conclusao"
    if "perletivoinicial" in colunas:
        return "matricula_ativa"
    if "matricula" in colunas and "situacaomatricula" in colunas:
        return "alunos_sem_periodo"
    return "desconhecido"


def _tipo_do_arquivo(caminho: str) -> str:
    caminho_path = Path(caminho)
    tipo = _detectar_tipo(caminho_path.name)
    if tipo != "desconhecido":
        return tipo
    try:
        return _detectar_tipo_por_colunas(_ler_planilha(caminho_path).columns)
    except Exception:
        return "desconhecido"


# -------------------------------------------------------------- importadores
def _importar_alunos_sem_periodo(caminho: Path) -> ImportResult:
    res = ImportResult(tipo="AlunosSemPeriodo")
    df = _ler_planilha(caminho)

    session = get_session()
    try:
        _garantir_curso(session)

        for _, row in df.iterrows():
            matricula = _to_str(_get_col(row, "Matrícula"))
            nome = _to_str(_get_col(row, "Nome"))
            if not matricula or not nome:
                res.ignorados += 1
                continue

            aluno = session.get(Aluno, matricula)
            criado = aluno is None
            if criado:
                aluno = Aluno(matricula=matricula, nome=nome)
                session.add(aluno)

            aluno.nome = nome
            aluno.curso_codigo = aluno.curso_codigo or _curso_codigo_da_matricula(matricula)

            sexo = _to_str(_get_col(row, "Sexo"))
            if sexo in ("M", "F"):
                aluno.sexo = SexoEnum(sexo)

            # A coluna tem um typo no arquivo original ("Inigresso")
            aluno.periodo_ingresso = (
                _to_str(_get_col(row, "Per. Let. Inigresso", "Per. Let. Ingresso"))
                or aluno.periodo_ingresso
            )
            aluno.situacao_matricula = _to_str(_get_col(row, "Situação Matrícula")) or aluno.situacao_matricula
            aluno.sit_ult_periodo_letivo = _to_str(_get_col(row, "Sit. Últ. Per. Letivo")) or aluno.sit_ult_periodo_letivo
            aluno.turno = _to_str(_get_col(row, "Turno")) or aluno.turno
            aluno.turno_ingresso = _to_str(_get_col(row, "Turno Ingresso")) or aluno.turno_ingresso
            aluno.qtd_periodos = _to_int(_get_col(row, "Qtd Períodos")) or aluno.qtd_periodos
            aluno.escola_origem = _to_str(_get_col(row, "Escola de Origem")) or aluno.escola_origem
            aluno.area_procedencia = _to_str(_get_col(row, "Area Procedência Escola Origem")) or aluno.area_procedencia
            aluno.renda_familiar_per_capita = _to_str(_get_col(row, "Renda Familiar Per Capita")) or aluno.renda_familiar_per_capita

            _criar_usuario_para_aluno(session, aluno)

            if criado:
                res.inseridos += 1
            else:
                res.atualizados += 1

        session.commit()
    except Exception as e:
        session.rollback()
        res.erros.append(str(e))
    finally:
        session.close()
    return res


def _importar_matricula_ativa(caminho: Path) -> ImportResult:
    res = ImportResult(tipo="MatriculaAtiva")
    df = _ler_planilha(caminho)

    session = get_session()
    try:
        _garantir_curso(session)

        for _, row in df.iterrows():
            matricula = _to_str(_get_col(row, "Matrícula"))
            nome = _to_str(_get_col(row, "Nome"))
            if not matricula or not nome:
                res.ignorados += 1
                continue

            aluno = session.get(Aluno, matricula)
            criado = aluno is None
            if criado:
                aluno = Aluno(matricula=matricula, nome=nome)
                session.add(aluno)

            aluno.nome = nome
            aluno.curso_codigo = aluno.curso_codigo or _curso_codigo_da_matricula(matricula)

            sexo = _to_str(_get_col(row, "Sexo"))
            if sexo in ("M", "F"):
                aluno.sexo = SexoEnum(sexo)

            aluno.periodo_ingresso = _to_str(_get_col(row, "Per. Letivo Inicial")) or aluno.periodo_ingresso
            aluno.situacao_matricula = _to_str(_get_col(row, "Situação Matrícula")) or aluno.situacao_matricula
            aluno.turno = _to_str(_get_col(row, "Turno")) or aluno.turno
            aluno.turno_ingresso = _to_str(_get_col(row, "Turno Ingresso")) or aluno.turno_ingresso
            aluno.tipo_forma_ingresso = _to_str(_get_col(row, "Tipo Forma Ingresso no Período")) or aluno.tipo_forma_ingresso
            aluno.escola_origem = _to_str(_get_col(row, "Escola de Origem")) or aluno.escola_origem
            aluno.area_procedencia = _to_str(_get_col(row, "Area Procedência Escola Origem")) or aluno.area_procedencia
            aluno.agrupamento = _to_str(_get_col(row, "Agrupamento")) or aluno.agrupamento
            aluno.renda_familiar = _to_str(_get_col(row, "Renda Familiar")) or aluno.renda_familiar
            aluno.renda_familiar_per_capita = _to_str(_get_col(row, "Renda Familiar Per Capita")) or aluno.renda_familiar_per_capita

            _criar_usuario_para_aluno(session, aluno)

            if criado:
                res.inseridos += 1
            else:
                res.atualizados += 1

        session.commit()
    except Exception as e:
        session.rollback()
        res.erros.append(str(e))
    finally:
        session.close()
    return res


def _importar_percentual(caminho: Path) -> ImportResult:
    res = ImportResult(tipo="PercentualDeConclusao")
    df = _ler_planilha(caminho)

    session = get_session()
    try:
        for _, row in df.iterrows():
            matricula = _to_str(_get_col(row, "Matrícula"))
            if not matricula:
                res.ignorados += 1
                continue
            if not session.get(Aluno, matricula):
                res.ignorados += 1
                continue

            conc = session.get(Conclusao, matricula)
            criado = conc is None
            if criado:
                conc = Conclusao(matricula=matricula)
                session.add(conc)

            conc.pct_cr_cumprido = _to_int(_get_col(row, "% Cr. Cumprido"))
            conc.pct_cumprido = _to_int(_get_col(row, "% Cumprido"))

            conc.ch_obrigatoria_cumpr = _to_int(_get_col(row, "C.H. Obrigatório Cumpr."))
            conc.ch_obrigatoria_prev = _to_int(_get_col(row, "C.H. Obrigatória Prev."))
            conc.ch_optativa_cumpr = _to_int(_get_col(row, "C.H. Optativa Cumpr."))
            conc.ch_optativa_prev = _to_int(_get_col(row, "C.H. Optativa Prev."))
            conc.ch_eletiva_cumpr = _to_int(_get_col(row, "C.H. Eletiva Cump."))
            conc.ch_eletiva_prev = _to_int(_get_col(row, "C.H. Eletiva Prev."))
            conc.ch_estagio_cumpr = _to_int(_get_col(row, "C.H. Estágio Cumpr."))
            conc.ch_estagio_prev = _to_int(_get_col(row, "C.H. Estágio Prev."))
            conc.ch_complementar_cumpr = _to_int(_get_col(row, "C.H. Complementar Cumpr."))
            conc.ch_complementar_prev = _to_int(_get_col(row, "C.H. Complementar Prev."))
            conc.ch_projeto_cumpr = _to_int(_get_col(row, "C.H. Projeto Cumpr."))
            conc.ch_projeto_prev = _to_int(_get_col(row, "C.H. Projeto Prev."))
            conc.ch_cumprida = _to_int(_get_col(row, "C.H. Cumprida"))
            conc.ch_prevista = _to_int(_get_col(row, "C.H. Prevista"))

            conc.cr_cumpr = _to_int(_get_col(row, "Cr. Cumpr."))
            conc.cr_prev = _to_int(_get_col(row, "Cr. Prev."))
            conc.cr_obrigatorio_cumpr = _to_int(_get_col(row, "Cr. Obrigatório Cumpr."))
            conc.cr_obrigatorio_prev = _to_int(_get_col(row, "Cr. Obrigatório Prev."))
            conc.cr_optativo_cumpr = _to_int(_get_col(row, "Cr. Optativo Cumpr."))
            conc.cr_optativo_prev = _to_int(_get_col(row, "Cr. Optativo Prev."))

            conc.ano_conclusao_grad = _to_int(_get_col(row, "Ano Conclusão Grad."))
            conc.ano_conclusao_pos = _to_int(_get_col(row, "Ano Conclusão Pós-Grad."))

            if criado:
                res.inseridos += 1
            else:
                res.atualizados += 1

        session.commit()
    except Exception as e:
        session.rollback()
        res.erros.append(str(e))
    finally:
        session.close()
    return res


def _extrair_curso_da_string(texto: str):
    """'03500 - Bacharelado...' → ('03500', 'Bacharelado...')"""
    if not texto:
        return None, None
    m = re.match(r"\s*(\d+)\s*-\s*(.+)", texto)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return None, texto.strip()


def _importar_disciplinas_pendentes(caminho: Path) -> ImportResult:
    res = ImportResult(tipo="DisciplinasPendentes")
    df = _ler_planilha(caminho)

    session = get_session()
    try:
        # Remove cabeçalho duplicado no meio do arquivo
        df = df[df["Sigla"].astype(str).str.strip().str.lower() != "sigla"]

        # Descobre quais alunos serão tocados (para deletar as pendências antigas)
        matriculas_tocadas = set()
        linhas_validas = []
        pendencias_vistas = set()
        for _, row in df.iterrows():
            sigla = _to_str(_get_col(row, "Sigla"))
            matricula = _to_str(_get_col(row, "Matrícula"))
            nome_disc = _to_str(_get_col(row, "Disciplina"))
            curso_str = _to_str(_get_col(row, "Curso"))
            if not sigla or not matricula or not nome_disc:
                continue
            chave = (matricula, sigla)
            if chave in pendencias_vistas:
                res.ignorados += 1
                continue
            pendencias_vistas.add(chave)
            linhas_validas.append((matricula, sigla, nome_disc, curso_str))
            matriculas_tocadas.add(matricula)

        # Apaga pendências antigas dos alunos presentes
        if matriculas_tocadas:
            session.query(Pendencia).filter(
                Pendencia.matricula.in_(matriculas_tocadas)
            ).delete(synchronize_session=False)

        # Insere novas
        for matricula, sigla, nome_disc, curso_str in linhas_validas:
            # Disciplina
            disc = session.get(Disciplina, sigla)
            if not disc:
                cod, _ = _extrair_curso_da_string(curso_str)
                disc = Disciplina(
                    sigla=sigla,
                    nome=nome_disc,
                    curso_codigo=cod or CURSO_PADRAO[0],
                )
                session.add(disc)
                session.flush()
            elif disc.nome != nome_disc:
                disc.nome = nome_disc

            # Só cria pendência se o aluno existir
            if not session.get(Aluno, matricula):
                continue

            session.add(Pendencia(matricula=matricula, disciplina_sigla=sigla))
            res.inseridos += 1

        session.commit()
    except Exception as e:
        session.rollback()
        res.erros.append(str(e))
    finally:
        session.close()
    return res


# ------------------------------------------------------------------ API pública
def importar_arquivo(caminho: str) -> ImportResult:
    p = Path(caminho)
    tipo = _tipo_do_arquivo(caminho)

    if tipo == "alunos_sem_periodo":
        return _importar_alunos_sem_periodo(p)
    if tipo == "matricula_ativa":
        return _importar_matricula_ativa(p)
    if tipo == "percentual_conclusao":
        return _importar_percentual(p)
    if tipo == "disciplinas_pendentes":
        return _importar_disciplinas_pendentes(p)

    return ImportResult(tipo=p.name, erros=["Tipo de arquivo não reconhecido."])


def _limpar_dados_academicos():
    """Remove o retrato acadêmico anterior, preservando contas de professores."""
    session = get_session()
    try:
        session.query(Pendencia).delete(synchronize_session=False)
        session.query(Conclusao).delete(synchronize_session=False)
        session.query(Aluno).delete(synchronize_session=False)
        session.query(Disciplina).delete(synchronize_session=False)
        session.query(Usuario).filter(Usuario.perfil == PerfilEnum.ALUNO).delete(
            synchronize_session=False
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def importar_varios(caminhos: list[str], substituir: bool = False) -> list[ImportResult]:
    """Importa o conjunto selecionado, opcionalmente substituindo os dados anteriores."""
    ordem = {
        "alunos_sem_periodo": 0,
        "matricula_ativa": 1,
        "percentual_conclusao": 2,
        "disciplinas_pendentes": 3,
        "desconhecido": 99,
    }
    caminhos = sorted(caminhos, key=lambda c: ordem[_tipo_do_arquivo(c)])
    if substituir:
        _limpar_dados_academicos()
    return [importar_arquivo(c) for c in caminhos]