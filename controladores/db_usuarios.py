"""
Gerenciamento da tabela de usuários (cadastro e autenticação).
"""

from controladores import db_construtor, db_leitor, seguranca


def inicializar_tabela() -> None:
    """Cria a tabela de usuários se ela não existir."""
    sql = """
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            senha_hash TEXT NOT NULL
        )
    """
    db_construtor.executar_no_banco([sql])


def cadastrar_usuario(username: str, senha: str) -> bool:
    """
    Cadastra um novo usuário no banco.
    Retorna False se o username já existir.
    """
    # Verifica se já existe
    if db_leitor.consultar_banco("SELECT 1 FROM usuarios WHERE username = ?", (username,)):
        return False

    hash_senha = seguranca.gerar_hash_senha(senha)
    db_construtor.executar_no_banco(
        ["INSERT INTO usuarios (username, senha_hash) VALUES (?, ?)"],
        [[(username, hash_senha)]]
    )
    return True


def verificar_credenciais(username: str, senha: str) -> bool:
    """Verifica se o usuário existe e a senha confere."""
    linhas = db_leitor.consultar_banco(
        "SELECT senha_hash FROM usuarios WHERE username = ?", (username,)
    )
    if not linhas:
        return False
    return seguranca.verificar_senha(senha, linhas[0][0])


def tem_usuarios() -> bool:
    """Retorna True se já existir pelo menos um usuário cadastrado."""
    linhas = db_leitor.consultar_banco("SELECT 1 FROM usuarios LIMIT 1")
    return bool(linhas)