"""
Camada de regras de negócio do Mamoru: valida pedidos segundo o RF01 (prazo, arte, quantidade, estoque).
Devolve VÁLIDO ou BLOQUEADO com motivos acumulados; puro por design, testável sem UI, banco ou disco.
"""

from controladores import entidades


def validar_pedido(pedido_obj: entidades.Pedido, estoque: dict) -> entidades.ResultadoValidacao:
    """
    Aplica as regras do RF01 e devolve status + motivo.
    Acumula todos os motivos de bloqueio (não para no primeiro erro).
    """
    motivos = []

    # Regra 1: prazo informado
    if not pedido_obj.prazo:
        motivos.append("Prazo não informado.")

    # Regra 2: arte anexada
    if not pedido_obj.caminho_arte:
        motivos.append("Arte não anexada.")

    # Regra 3: quantidade válida (> 0)
    if pedido_obj.quantidade <= 0:
        motivos.append(f"Quantidade inválida ({pedido_obj.quantidade}).")

    # Regra 4: estoque suficiente (case-insensitive)
    disponivel = buscar_no_estoque(estoque, pedido_obj.produto)
    if pedido_obj.quantidade > disponivel:
        motivos.append(
            f"Estoque insuficiente"
            f"(disponível: {disponivel}, solicitado: {pedido_obj.quantidade})."
        )

    if motivos:
        return entidades.ResultadoValidacao("RETIDO", " ".join(motivos))

    return entidades.ResultadoValidacao("VÁLIDO")


def buscar_no_estoque(estoque: dict, produto: str) -> int:
    """
    Busca a quantidade disponível de um produto no estoque,
    ignorando diferenças de maiúsculas/minúsculas.
    Retorna 0 se não encontrar.
    """
    if not produto:
        return 0

    alvo = produto.strip().lower()
    for nome, quantidade in estoque.items():
        if nome.strip().lower() == alvo:
            return quantidade
    return 0