"""Estado compartilhado da aplicação Mamoru."""

class AplicacaoMamoru:
    """Só guarda estado. Não constrói UI."""

    def __init__(self, root):
        self.root = root

        # Estado de navegação
        self.tela_atual = "login"
        
        # Referências dos objetos (para controle de estado)
        self.tela_login_obj = None
        self.tela_importacao_obj = None
        self.tela_dashboard_obj = None
        
        # Referências dos frames (para pack/forget)
        self.tela_login = None
        self.tela_importacao = None
        self.tela_dashboard = None

        # Estado de negócio
        self.estoque_atual = {}
        self.pedidos_importados = []
        self.resultados_validacao = {}

    def iniciar(self):
        """Mostra a primeira tela (login)."""
        if self.tela_login is None:
            from interface.tela_login import TelaLogin
            self.tela_login_obj = TelaLogin(self.root, self)
            self.tela_login = self.tela_login_obj.construir()
        
        self.tela_login.pack(fill="both", expand=True)
        self.tela_atual = "login"

    def ao_fazer_login(self):
        """Orquestrador: decide se vai para Dashboard ou Importação."""
        from controladores import db_leitor

        pedidos_existentes = db_leitor.carregar_pedidos()

        if pedidos_existentes:
            self.carregar_dashboard()
        else:
            self.ir_para_importacao()

    def ir_para_importacao(self):
        """Navega para a tela de importação."""
        if self.tela_importacao is None:
            from interface.tela_importacao import TelaImportacao
            self.tela_importacao_obj = TelaImportacao(self.root, self)
            self.tela_importacao = self.tela_importacao_obj.construir()
        
        if self.tela_login:
            self.tela_login.pack_forget()
            
        self.tela_importacao.pack(fill="both", expand=True)
        self.tela_atual = "importacao"

    def carregar_dashboard(self):
        """Carrega dados do banco, valida e navega para o dashboard."""
        from controladores import db_leitor, validador_pedidos
        from interface.tela_dashboard import TelaDashboard

        self.pedidos_importados = db_leitor.carregar_pedidos()
        self.estoque_atual = db_leitor.carregar_estoque()

        self.resultados_validacao = {}
        for pedido in self.pedidos_importados:
            resultado = validador_pedidos.validar_pedido(pedido, self.estoque_atual)
            self.resultados_validacao[pedido.numero] = resultado

        # Cria nova instância da TelaDashboard
        self.tela_dashboard_obj = TelaDashboard(self.root, self)
        self.tela_dashboard = self.tela_dashboard_obj.construir()

        if self.tela_importacao:
            self.tela_importacao.pack_forget()
        if self.tela_login:
            self.tela_login.pack_forget()

        self.tela_dashboard.pack(fill="both", expand=True)
        self.tela_atual = "dashboard"