"""Gera um arquivo alunos_exemplo.xlsx para você testar a importação."""
import pandas as pd

dados = [
    {"matricula": "20231001", "nome": "Ana Silva",    "email": "ana@aluno.com",   "ano_ingresso": 2023, "semestre_ingresso": 1},
    {"matricula": "20231002", "nome": "Bruno Costa",  "email": "bruno@aluno.com", "ano_ingresso": 2023, "semestre_ingresso": 1},
    {"matricula": "20232003", "nome": "Carla Souza",  "email": "carla@aluno.com", "ano_ingresso": 2023, "semestre_ingresso": 2},
    {"matricula": "20241001", "nome": "Diego Ramos",  "email": "diego@aluno.com", "ano_ingresso": 2024, "semestre_ingresso": 1},
]

df = pd.DataFrame(dados)
df.to_excel("alunos_exemplo.xlsx", index=False)
print("Arquivo 'alunos_exemplo.xlsx' gerado com sucesso.")