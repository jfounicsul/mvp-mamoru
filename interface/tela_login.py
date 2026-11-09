"""Tela 1 — Login / Primeiro Acesso."""

import tkinter as tk
from tkinter import messagebox

from constantes import estilo
from interface import fabricas
from controladores import db_usuarios, seguranca


class TelaLogin:
    def __init__(self, root, aplicacao):
        self.root = root
        self.aplicacao = aplicacao
        self.primeiro_acesso = not db_usuarios.tem_usuarios()
        self.frame = None
        self.campo_usuario = None
        self.campo_senha = None
        self.campo_senha_confirma = None

    def construir(self) -> tk.Frame:
        self.frame = fabricas.criar_frame(self.root, bg=estilo.Cor.Fundo.PRINCIPAL)

        container = fabricas.criar_frame(
            self.frame,
            bg=estilo.Cor.Fundo.PRINCIPAL,
            padx=estilo.Padding.Frame.LOGIN,
            pady=estilo.Padding.Frame.LOGIN,
        )
        container.place(relx=0.5, rely=0.5, anchor="center")

        fabricas.criar_label(
            container, 
            "Mamoru", 
            estilo.Fonte.Tamanho.TITULO,
            bg=estilo.Cor.Fundo.PRINCIPAL,
            bold=True
        ).pack(pady=(0, estilo.Padding.PEQUENO))

        subtitulo_texto = (
            "Por favor, crie sua conta para realizar o primeiro acesso."
            if self.primeiro_acesso else
            "Por favor, insira seu usuário e senha para acessar o sistema."
        )

        fabricas.criar_label(
            container,
            subtitulo_texto,
            estilo.Fonte.Tamanho.NORMAL,
            cor=estilo.Cor.Texto.MUTED,
            bg=estilo.Cor.Fundo.PRINCIPAL,
        ).pack(pady=estilo.Padding.PADRAO)

        # Campo Usuário
        fabricas.criar_label(container, "Usuário", bg=estilo.Cor.Fundo.PRINCIPAL).pack(anchor="w")
        self.campo_usuario = fabricas.criar_campo(container)
        self.campo_usuario.pack(fill="x", pady=estilo.Padding.PADRAO)

        # Campo Senha
        fabricas.criar_label(container, "Senha", bg=estilo.Cor.Fundo.PRINCIPAL).pack(anchor="w")
        self.campo_senha = fabricas.criar_campo(container, mostrar_caracteres=True)
        self.campo_senha.pack(fill="x", pady=estilo.Padding.PADRAO)

        # Campo Confirmar Senha (só no primeiro acesso)
        if self.primeiro_acesso:
            fabricas.criar_label(
                container, "Confirme a senha", bg=estilo.Cor.Fundo.PRINCIPAL
            ).pack(anchor="w")
            self.campo_senha_confirma = fabricas.criar_campo(container, mostrar_caracteres=True)
            self.campo_senha_confirma.pack(fill="x", pady=estilo.Padding.PADRAO)

        # Botão
        texto_botao = "Cadastrar" if self.primeiro_acesso else "Entrar"
        btn = fabricas.criar_botao(container, texto_botao, self.acao_principal)
        btn.config(highlightthickness=0)
        btn.pack(pady=estilo.Padding.PADRAO)

        return self.frame

    def acao_principal(self):
        username = self.campo_usuario.get().strip()
        senha = self.campo_senha.get()

        if not username or not senha:
            messagebox.showwarning(
                "Mamoru — Aviso", 
                "Por favor, preencha todos os campos\n"
                "para efetuar seu cadastro.")
            return

        if self.primeiro_acesso:
            self.processar_cadastro(username, senha)
        else:
            self.processar_login(username, senha)

    def processar_cadastro(self, username, senha):
        confirma = self.campo_senha_confirma.get()
        if senha != confirma:
            messagebox.showerror(
                "Mamoru — Erro", 
                "As senhas não coincidem.\n"
                "Por favor, tente novamente."
            )
            return
        
        if db_usuarios.cadastrar_usuario(username, senha):
            messagebox.showinfo(
                "Mamoru — Sucesso", 
                "Usuário criado com sucesso.\n"
                "Faça login para continuar.")
            self.reiniciar_tela()
        else:
            messagebox.showerror(
                "Mamoru — Erro", 
                "Este usuário já existe.\n"
                "Por favor, tente novamente."
            )

    def processar_login(self, username, senha):
        bloqueado, segundos = seguranca.esta_bloqueado(username)
        if bloqueado:
            messagebox.showerror(
                "Mamoru — Acesso Bloqueado", 
                f"Senha e/ou usuário incorreto inserido três (3) vezes seguidas.\n"
                "Por favor, tente novamente em {segundos} segundos."
            )
            return

        if db_usuarios.verificar_credenciais(username, senha):
            seguranca.registrar_tentativa(username, sucesso=True)
            self.aplicacao.ao_fazer_login()
        else:
            seguranca.registrar_tentativa(username, sucesso=False)
            
            bloqueado_agora, segundos = seguranca.esta_bloqueado(username)
            if bloqueado_agora:
                messagebox.showerror(
                    "Mamoru — Acesso Bloqueado", 
                    f"Senha e/ou usuário incorreto inserido três (3) vezes seguidas.\n"
                    f"Por favor, tente novamente em {segundos} segundos."
                )
            else:
                messagebox.showerror(
                    "Mamoru — Acesso Negado", 
                    "Usuário e/ou senha inválidos."
                    )
            
            self.campo_senha.delete(0, tk.END)

    def reiniciar_tela(self):
        self.frame.destroy()
        nova_tela = TelaLogin(self.root, self.aplicacao)
        nova_tela.construir().pack(fill="both", expand=True)
        self.aplicacao.tela_login = nova_tela.frame