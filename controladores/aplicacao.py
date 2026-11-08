"""
Estado compartilhado da aplicação Mamoru.
Guarda as informações vitais que precisam sobreviver à troca de telas.
"""


class AplicacaoMamoru:
    """Só guarda estado. Não constrói UI."""

    def __init__(self, root):
        self.root = root

        # Estado de navegação
        self.tela_atual = "login"
        self.tela_login = None
        self.tela_importacao = None
        self.tela_dashboard = None

        # Estado de negócio
        self.estoque_atual = {}
        self.pedidos_importados = []
        self.resultados_validacao = {}

    def iniciar(self):
        """Mostra a primeira tela (login)."""
        self.tela_login.pack(fill="both", expand=True)