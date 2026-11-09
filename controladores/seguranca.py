"""
Segurança e criptografia de senhas (PBKDF2 com salt) e proteção anti-brute-force.
"""

import hashlib
import os
import secrets
import time


# Dicionário em memória para rastrear tentativas falhas: {username: [tentativas, timestamp_bloqueio]}
_tentativas_falhas = {}

MAX_TENTATIVAS = 3
TEMPO_BLOQUEIO_SEGUNDOS = 5 * 60


def gerar_hash_senha(senha: str) -> str:
    """Gera um hash seguro para a senha usando PBKDF2 com SHA-256."""
    salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}${hash_bytes.hex()}"


def verificar_senha(senha: str, hash_salvo: str) -> bool:
    """Verifica se a senha digitada corresponde ao hash salvo (com proteção contra timing attacks)."""
    try:
        salt_hex, hash_hex = hash_salvo.split('$')
        salt = bytes.fromhex(salt_hex)
        hash_esperado = bytes.fromhex(hash_hex)
        
        hash_digitado = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt, 100000)
        
        # compare_digest evita Timing Attacks (análise de tempo de resposta)
        return secrets.compare_digest(hash_digitado, hash_esperado)
    except Exception:
        return False


def esta_bloqueado(username: str) -> tuple[bool, int]:
    """
    Verifica se o usuário está bloqueado.
    Retorna (True, segundos_restantes) ou (False, 0).
    """
    if username not in _tentativas_falhas:
        return False, 0

    tentativas, timestamp_bloqueio = _tentativas_falhas[username]

    if tentativas >= MAX_TENTATIVAS:
        tempo_passado = time.time() - timestamp_bloqueio
        if tempo_passado < TEMPO_BLOQUEIO_SEGUNDOS:
            # Ainda bloqueado
            segundos_restantes = int(TEMPO_BLOQUEIO_SEGUNDOS - tempo_passado)
            return True, segundos_restantes
        else:
            # Tempo expirou, reseta o contador
            del _tentativas_falhas[username]
            return False, 0

    return False, 0


def registrar_tentativa(username: str, sucesso: bool) -> None:
    """Registra uma tentativa de login (sucesso ou falha)."""
    if sucesso:
        # Se acertou a senha, limpa o histórico
        if username in _tentativas_falhas:
            del _tentativas_falhas[username]
        return

    # Se falhou, incrementa o contador
    if username not in _tentativas_falhas:
        _tentativas_falhas[username] = [1, 0]
    else:
        _tentativas_falhas[username][0] += 1
        # Se atingiu o limite, grava o timestamp do bloqueio
        if _tentativas_falhas[username][0] >= MAX_TENTATIVAS:
            _tentativas_falhas[username][1] = time.time()