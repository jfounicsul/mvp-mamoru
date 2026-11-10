"""
Tela 2 — Importação do Excel e validação.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

from constantes import estilo
from interface import fabricas
from controladores import db_construtor, db_leitor, validador_pedidos, leitor_planilha


class TelaImportacao:
    def __init__(self, root, aplicacao):
        self.root = root
        self.aplicacao = aplicacao
        self.frame = None

    def construir(self) -> tk.Frame:
        self.frame = fabricas.criar_frame(self.root, bg=estilo.Cor.Fundo.PRINCIPAL)

        container = fabricas.criar_frame(
            self.frame,
            bg=estilo.Cor.Fundo.PRINCIPAL,
            padx=estilo.Padding.GRANDE,
            pady=estilo.Padding.GRANDE,
        )
        container.place(relx=0.5, rely=0.5, anchor="center")

        fabricas.criar_label(
            container, "Bem-vindo ao Mamoru", estilo.Fonte.Tamanho.TITULO, bg=estilo.Cor.Fundo.PRINCIPAL
        ).pack(pady=(0, estilo.Padding.PEQUENO))

        fabricas.criar_label(
            container,
            "Para começar, importe o arquivo Excel exportado pelo AJXCommerce\n"
            "para iniciar a leitura dos pedidos.",
            estilo.Fonte.Tamanho.NORMAL,
            cor=estilo.Cor.Texto.MUTED,
            bg=estilo.Cor.Fundo.PRINCIPAL,
        ).pack(pady=(0, estilo.Padding.GRANDE))

        btn = fabricas.criar_botao(
            container, 
            "Importar arquivo Excel (.xlxs)", 
            self.importar, 
            largura=estilo.Dimensao.Botao.Importacao.LARGURA
        )
        btn.pack()

        return self.frame

    def importar(self):
        caminho_arquivo = filedialog.askopenfilename(
            title="Mamoru — Selecione a planilha de pedidos exportada pelo AJXCommerce",
            filetypes=[("Planilhas", "*.xlsx *.ods"), ("Todos os arquivos", "*.*")]
        )

        if not caminho_arquivo:
            return

        try:
            pedidos_reais = leitor_planilha.ler_planilha_pedidos(caminho_arquivo)

            if not pedidos_reais:
                messagebox.showwarning(
                    "Mamoru — Erro", 
                    "Nenhum pedido válido foi encontrado na planilha."
                )
                return

            db_construtor.inicializar_banco()
            db_construtor.salvar_pedidos(pedidos_reais)
            
            self.aplicacao.pedidos_importados = db_leitor.carregar_pedidos()
            self.aplicacao.estoque_atual = db_leitor.carregar_estoque()

            self.aplicacao.resultados_validacao = {}
            for pedido in self.aplicacao.pedidos_importados:
                resultado = validador_pedidos.validar_pedido(pedido, self.aplicacao.estoque_atual)
                self.aplicacao.resultados_validacao[pedido.numero] = resultado

            self.aplicacao.carregar_dashboard()

        except Exception as erro:
            messagebox.showerror(
                "Mamoru — Erro", 
                f"Ocorreu um erro ao ler a planilha:\n{erro}"
            )