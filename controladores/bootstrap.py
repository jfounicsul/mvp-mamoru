"""Inicialização ordenada da aplicação Mamoru."""

from controladores import (
    aplicacao,
    db_construtor,
    db_leitor,
)
from interface import tela_login


def inicializar_aplicacao(root) -> aplicacao.AplicacaoMamoru:
    """Ordem: estado → banco → interface. Cada passo isolado."""

    # 1. Estado
    app = aplicacao.AplicacaoMamoru(root)

    # 2. Banco (SQLite local)
    db_construtor.inicializar_banco()
    app.estoque_atual = db_leitor.carregar_estoque()

    # 3. Interface
    app.tela_login = tela_login.construir_tela_login(root, app)

    # (As telas de importação e dashboard serão construídas sob demanda
    # pelas próprias telas anteriores, economizando memória).

    return app