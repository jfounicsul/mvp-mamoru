"""
Inicialização ordenada da aplicação Mamoru.
"""

from controladores import aplicacao, db_construtor, db_leitor, db_usuarios
from interface import tela_login


def inicializar_aplicacao(root) -> aplicacao.AplicacaoMamoru:
    # 1. Estado
    app = aplicacao.AplicacaoMamoru(root)

    # 2. Banco de Dados
    db_construtor.inicializar_banco()
    db_usuarios.inicializar_tabela()
    app.estoque_atual = db_leitor.carregar_estoque()

    # 3. Interface
    tela_login_obj = tela_login.TelaLogin(root, app)
    app.tela_login = tela_login_obj.construir()
    app.tela_login_obj = tela_login_obj # Guarda a referência do objeto

    return app