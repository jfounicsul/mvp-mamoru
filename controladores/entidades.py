"""
Entidades de domínio do Mamoru: as estruturas de dados que representam o negócio.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ItemEstoque:
    """Representa um produto no estoque, com a quantidade física disponível."""
    produto: str
    quantidade_disponivel: int


@dataclass
class Pedido:
    """Representa um pedido feito por um cliente, pronto para ser conferido."""
    numero: str
    cliente: str
    produto: str
    quantidade: int
    data_pedido: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    prazo: Optional[str] = None
    caminho_arte: Optional[str] = None


@dataclass
class ResultadoValidacao:
    """Armazena o veredito da conferência de um pedido e o motivo do bloqueio, se houver."""
    status: str          # "VÁLIDO" ou "RETIDO"
    motivo: str = ""