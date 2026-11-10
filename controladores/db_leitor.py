"""
Leitura da base de dados local em SQLite (nativo, sem ORM).
"""

import sqlite3

from controladores import db_construtor, entidades


def consultar_banco(sql: str, parametros: tuple = None) -> list:
    """
    Abre conexão, executa uma consulta SELECT, busca todas as linhas e fecha.
    Retorna lista de tuplas (ou lista vazia em caso de erro).
    """
    conexao = sqlite3.connect(db_construtor.CAMINHO_DB)
    try:
        cursor = conexao.execute(sql, parametros or ())
        return cursor.fetchall()
    finally:
        conexao.close()


def carregar_estoque() -> dict:
    """Retorna {produto: quantidade_disponivel}."""
    linhas = consultar_banco("SELECT produto, quantidade_disponivel FROM estoque")
    return {linha[0]: linha[1] for linha in linhas}


def carregar_pedidos() -> list:
    """Retorna lista de entidades.Pedido a partir da tabela pedidos."""
    linhas = consultar_banco(
        "SELECT numero, cliente, produto, quantidade, data_pedido, prazo, caminho_arte "
        "FROM pedidos"
    )
    return [
        entidades.Pedido(
            numero=linha[0],
            cliente=linha[1],
            produto=linha[2],
            quantidade=linha[3],
            data_pedido=linha[4],
            prazo=linha[5],
            caminho_arte=linha[6],
        )
        for linha in linhas
    ]