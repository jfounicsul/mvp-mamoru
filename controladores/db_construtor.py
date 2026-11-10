"""
Construção da base de dados local em SQLite (nativo, sem ORM).
Responsabilidade única: criar a estrutura do banco e gravar dados
de pedidos e estoque lidos das planilhas (leitura_planilha.py).
A leitura do banco é feita pelo módulo leitor_db.py.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from controladores import leitor_planilha, entidades


CAMINHO_DB = Path(__file__).parent.parent / "dados" / "mamoru.db"


def executar_no_banco(comandos: list, parametros: list = None) -> None:
    """
    Abre conexão, executa um ou mais comandos SQL, faz commit e fecha.
    - comandos: lista de strings SQL (ex.: [CREATE TABLE ...])
    - parametros: lista opcional de listas de parâmetros por comando
    """
    CAMINHO_DB.parent.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(CAMINHO_DB)
    try:
        for index, comando in enumerate(comandos):
            params = parametros[index] if parametros else None
            if params:
                conexao.executemany(comando, params)
            else:
                conexao.execute(comando)
        conexao.commit()
    finally:
        conexao.close()


def inicializar_banco() -> None:
    """
    Cria a pasta e as tabelas vazias de estoque e pedidos (idempotente)
    a partir de dados fornecidos pelas planilhas.
    """
    sql_estoque = """
        CREATE TABLE IF NOT EXISTS estoque (
            produto TEXT PRIMARY KEY,
            quantidade_disponivel INTEGER NOT NULL
        )
    """

    sql_pedidos = """
        CREATE TABLE IF NOT EXISTS pedidos (
            numero TEXT PRIMARY KEY,
            cliente TEXT NOT NULL,
            produto TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            data_pedido TEXT NOT NULL,
            prazo TEXT,
            caminho_arte TEXT,
            status TEXT NOT NULL DEFAULT 'PENDENTE'
        )
    """

    executar_no_banco([sql_estoque, sql_pedidos])


def salvar_estoque(estoque: dict) -> None:
    """
    Grava um dicionário {produto: quantidade_disponivel} na tabela estoque.
    Usa INSERT OR REPLACE: reimportar a planilha atualiza os pedidos.
    """
    if not estoque:
        return

    sql = "INSERT OR REPLACE INTO estoque (produto, quantidade_disponivel) VALUES (?, ?)"
    parametros = [(produto, quantidade) for produto, quantidade in estoque.items()]

    executar_no_banco([sql], [parametros])


def salvar_pedidos(pedidos: list) -> None:
    """
    Grava uma lista de entidades.Pedido na tabela pedidos.
    Usa INSERT OR REPLACE por 'numero': reimportar a planilha atualiza os pedidos.
    """
    if not pedidos:
        return

    sql = """
        INSERT OR REPLACE INTO pedidos
            (numero, cliente, produto, quantidade, data_pedido, prazo, caminho_arte, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    parametros = [
        (
            entidades.numero,
            entidades.cliente,
            entidades.produto,
            entidades.quantidade,
            entidades.data_pedido,
            entidades.prazo,
            entidades.caminho_arte,
            "PENDENTE",
        )
        for pedido in pedidos
    ]

    executar_no_banco([sql], [parametros])


# DADOS FICTÍCIOS (FALLBACK PARA TESTES RÁPIDOS)
def importar_pedidos_ficticios() -> list[entidades.Pedido]:
    """Mantido para testes sem arquivo (fallback)."""
    hoje = datetime.now()  # <--- MUDOU AQUI: data real do sistema

    return [
        entidades.Pedido(
            "001",
            "Maria Silva",
            "Camiseta M",
            1,
            leitor_planilha.formatar_data_hora(hoje),
            leitor_planilha.formatar_data_hora(hoje + timedelta(days=7)),
            "arte_maria.png"
        ),
        entidades.Pedido(
            "002",
            "João Souza",
            "Caneca",
            2,
            leitor_planilha.formatar_data_hora(hoje),
            leitor_planilha.formatar_data_hora(hoje + timedelta(days=5)),
            None
        ),
        entidades.Pedido(
            "003",
            "Ana Aparecida",
            "Camiseta P",
            1,
            leitor_planilha.formatar_data_hora(hoje),
            leitor_planilha.formatar_data_hora(hoje.replace(hour=18)),  # Hoje às 18h
            "arte_ana.png"
        ),
        entidades.Pedido(
            "004",
            "Claudio Conceição",
            "Camiseta M",
            2,
            leitor_planilha.formatar_data_hora(hoje),
            leitor_planilha.formatar_data_hora(hoje + timedelta(days=2)),
            "arte_claudio.png"
        ),
        entidades.Pedido(
            "005",
            "Pedro Perez",
            "Copo",
            5,
            leitor_planilha.formatar_data_hora(hoje),
            leitor_planilha.formatar_data_hora(hoje + timedelta(days=10)),
            "arte_pedro.png"
        ),
    ]


def importar_estoque_ficticio() -> dict:
    """
    Fallback de estoque para testes sem planilha.
    Cobre os produtos usados em importar_pedidos_ficticios().
    """
    return {
        "Camiseta P": 20,
        "Camiseta M": 20,
        "Caneca": 10,
        "Copo": 10,
    }