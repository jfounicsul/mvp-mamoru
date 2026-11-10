"""
Janela modal com informações complementares do pedido.
"""

import tkinter as tk
from datetime import datetime

from constantes import estilo
from interface import fabricas, animacao


def abrir_janela_informacoes(root, pedido):
    """Abre uma janela centralizada com os detalhes do pedido."""
    
    janela = tk.Toplevel(root)
    janela.title(f"Mamoru — Detalhes do Pedido {pedido.numero}")
    janela.resizable(False, False)
    janela.configure(bg=estilo.Cor.Fundo.PRINCIPAL)
    
    # 1. Esconde a janela antes de configurar 
    # (Evita um "flicker" no canto que passa impressão amadora)
    janela.withdraw()

    # 2. Calcula o centro da tela principal
    root.update_idletasks()
    largura_janela = 500
    altura_janela = 400
    x = root.winfo_x() + (root.winfo_width() // 2) - (largura_janela // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (altura_janela // 2)
    janela.geometry(f"{largura_janela}x{altura_janela}+{x}+{y}")

    # Trava a janela principal enquanto esta estiver aberta
    janela.transient(root)
    janela.grab_set()

    # Container principal
    container = fabricas.criar_frame(
        janela, 
        bg=estilo.Cor.Fundo.PRINCIPAL, 
        padx=estilo.Padding.GRANDE, 
        pady=estilo.Padding.GRANDE
    )
    container.pack(fill="both", expand=True)

    # Título da Janela
    fabricas.criar_label(
        container, 
        "Pedido Nº", 
        estilo.Fonte.Tamanho.TITULO, 
        bg=estilo.Cor.Fundo.PRINCIPAL, 
        bold=True
    ).pack(anchor="w", pady=(0, estilo.Padding.PEQUENO))

    # Subtítulo com o ID do pedido em destaque
    fabricas.criar_label(
        container, 
        f"{pedido.numero}", 
        estilo.Fonte.Tamanho.Informacoes.PEDIDO, 
        bg=estilo.Cor.Fundo.PRINCIPAL, 
        cor=estilo.Cor.Acao.PRIMARIA,
        bold=True
    ).pack(anchor="w", pady=(0, estilo.Padding.GRANDE))

    # Função auxiliar para criar os blocos de informação
    def bloco_info(
            titulo, 
            valor, 
            tamanho_valor=estilo.Fonte.Tamanho.NORMAL, 
            bold_valor=False, 
            cor_valor=estilo.Cor.Texto.PADRAO
        ):
        # Um cartão sutil para separar cada bloco de informação
        bloco = fabricas.criar_frame(container, bg=estilo.Cor.Fundo.PAINEL)
        bloco.config(padx=estilo.Padding.PADRAO, pady=estilo.Padding.PADRAO)
        bloco.pack(fill="x", pady=estilo.Padding.PEQUENO)
        
        # Rótulo (ex: CLIENTE)
        fabricas.criar_label(
            bloco, 
            titulo.upper(), 
            estilo.Fonte.Tamanho.PEQUENO, 
            cor=estilo.Cor.Texto.MUTED, 
            bg=estilo.Cor.Fundo.PAINEL, 
            bold=True
        ).pack(anchor="w")
        
        # Valor (ex: Maria Silva)
        fabricas.criar_label(
            bloco, 
            str(valor) if valor else "—", 
            tamanho_valor, 
            cor=cor_valor, 
            bg=estilo.Cor.Fundo.PAINEL,
            bold=bold_valor
        ).pack(anchor="w", pady=(estilo.Padding.PEQUENO, 0))


    # --- DADOS DO PEDIDO ---    
    # Cliente em destaque
    bloco_info(
        "Cliente", 
        pedido.cliente, 
        tamanho_valor=estilo.Fonte.Tamanho.SUBTITULO, 
        bold_valor=True
    )
    
    # Linha com Registro e Arte
    linha_dupla = fabricas.criar_frame(container, bg=estilo.Cor.Fundo.PRINCIPAL)
    linha_dupla.pack(fill="x", pady=estilo.Padding.PEQUENO)
    
    # Coluna Esquerda: Registro
    col_registro = fabricas.criar_frame(linha_dupla, bg=estilo.Cor.Fundo.PAINEL)
    col_registro.config(padx=estilo.Padding.PADRAO, pady=estilo.Padding.PADRAO)
    col_registro.pack(side="left", fill="both", expand=True, padx=(0, estilo.Padding.PEQUENO))
    
    fabricas.criar_label(
        col_registro, 
        "REGISTRO", 
        estilo.Fonte.Tamanho.PEQUENO, 
        cor=estilo.Cor.Texto.MUTED, 
        bg=estilo.Cor.Fundo.PAINEL, 
        bold=True
    ).pack(anchor="w")
    
    if pedido.data_pedido:
        try:
            # Usa a classe datetime importada no topo, sem sobrescrevê-la
            dt_obj = datetime.strptime(pedido.data_pedido, "%Y-%m-%d %H:%M:%S")
            data_formatada = dt_obj.strftime("%d/%m/%Y às %H:%M")
        except ValueError:
            data_formatada = pedido.data_pedido
    else:
        data_formatada = "—"
        
    fabricas.criar_label(
        col_registro, 
        data_formatada, 
        estilo.Fonte.Tamanho.NORMAL, 
        bg=estilo.Cor.Fundo.PAINEL
    ).pack(anchor="w", pady=(estilo.Padding.PEQUENO, 0))

    # Coluna Direita: Arte
    col_arte = fabricas.criar_frame(linha_dupla, bg=estilo.Cor.Fundo.PAINEL)
    col_arte.config(padx=estilo.Padding.PADRAO, pady=estilo.Padding.PADRAO)
    col_arte.pack(side="left", fill="both", expand=True)
    
    fabricas.criar_label(
        col_arte, 
        "ARTE", 
        estilo.Fonte.Tamanho.PEQUENO, 
        cor=estilo.Cor.Texto.MUTED, 
        bg=estilo.Cor.Fundo.PAINEL, 
        bold=True
    ).pack(anchor="w")
    
    cor_arte = estilo.Cor.Texto.PADRAO if pedido.caminho_arte else estilo.Cor.Status.RETIDO
    fabricas.criar_label(
        col_arte, 
        pedido.caminho_arte if pedido.caminho_arte else "Não anexada", 
        estilo.Fonte.Tamanho.NORMAL, 
        cor=cor_arte, 
        bg=estilo.Cor.Fundo.PAINEL
    ).pack(anchor="w", pady=(estilo.Padding.PEQUENO, 0))

    # Botão de Fechar
    def fechar_com_fade():
        animacao.fade_out_janela(janela, janela.destroy)

    btn_fechar = fabricas.criar_botao(
        container, 
        "Fechar", 
        fechar_com_fade, 
        largura=15
    )
    btn_fechar.pack(side="bottom", pady=estilo.Padding.GRANDE)

    # 3. DISPARA O FADE-IN
    animacao.fade_in_janela(janela)