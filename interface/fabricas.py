"""
Widgets padronizados do Mamoru.
"""

import tkinter

from constantes import estilo


def criar_botao(parent, texto, comando, largura=estilo.Dimensao.Botao.LARGURA):
    return tkinter.Button(
        parent,
        text=texto,
        command=comando,
        width=largura,
        height=estilo.Dimensao.Botao.ALTURA,
        bg=estilo.Cor.Botao.FUNDO,
        fg=estilo.Cor.Texto.PADRAO,
        activebackground=estilo.Cor.Botao.ATIVO,
        activeforeground=estilo.Cor.Texto.PADRAO,
        font=(estilo.Fonte.FAMILIA, estilo.Fonte.Tamanho.NORMAL),
        relief="raised",
        cursor="hand2",
        borderwidth=2,
        highlightthickness=2
    )


def criar_campo(parent, mostrar_caracteres=False):
    return tkinter.Entry(
        parent,
        show="*" if mostrar_caracteres else "",
        font=(estilo.Fonte.FAMILIA, estilo.Fonte.Tamanho.NORMAL),
        relief="solid",
        borderwidth=1,
        highlightthickness=0
    )


def criar_label(
        parent, 
        texto, 
        tamanho=estilo.Fonte.Tamanho.NORMAL, 
        cor=estilo.Cor.Texto.PADRAO, 
        bg=estilo.Cor.Fundo.PRINCIPAL,
        bold=False
    ):
    return tkinter.Label(
        parent,
        text=texto,
        bg=bg,
        fg=cor,
        font=(estilo.Fonte.FAMILIA, tamanho, "bold" if bold else "normal"),
        bd=0,                
        borderwidth=0,         
        highlightthickness=0  
    )



def criar_frame(
        parent, 
        bg=estilo.Cor.Fundo.PRINCIPAL, 
        highlightbackground=None, 
        highlightthickness=0, 
        **kwargs
    ):
    return tkinter.Frame(
        parent, 
        bg=bg,
        bd=0,
        highlightbackground=highlightbackground if highlightbackground else bg,
        highlightthickness=highlightthickness,
        **kwargs
    )

def criar_canvas(
        parent, 
        bg=estilo.Cor.Fundo.PRINCIPAL
    ):
    return tkinter.Canvas(
        parent, 
        bg=bg,
        bd=0,

    )

def criar_scrollbar(parent, **kwargs):
    return tkinter.Scrollbar(parent, **kwargs)


def criar_label_emoji(
        parent, 
        texto, 
        tamanho=estilo.Fonte.Tamanho.NORMAL, 
        cor=estilo.Cor.Texto.PADRAO, 
        bg=estilo.Cor.Fundo.PRINCIPAL
    ):
    return tkinter.Label(
        parent, 
        text=texto, 
        bg=bg, 
        fg=cor,
        font=("Segoe UI Emoji", tamanho),
        bd=0, 
        borderwidth=0, 
        highlightthickness=0
    )