"""Tela 3 — Dashboard de resultados."""

import tkinter as tk
from datetime import datetime

from constantes import estilo
from interface import fabricas, animacao, janela_informacoes


class TelaDashboard:
    def __init__(self, root, aplicacao):
        self.root = root
        self.aplicacao = aplicacao
        self.frame = None
        self.hoje = datetime.now()
        self.linha_selecionada = {"id": None, "frame": None, "tag_original": None}

    def construir(self) -> tk.Frame:
        self.frame = fabricas.criar_frame(self.root, bg=estilo.Cor.Fundo.PRINCIPAL)
        self.frame.config(padx=estilo.Padding.PADRAO, pady=estilo.Padding.PADRAO)

        fabricas.criar_label(
            self.frame, 
            "Gestão de Pedidos", 
            estilo.Fonte.Tamanho.TITULO, 
            bg=estilo.Cor.Fundo.PRINCIPAL, 
            bold=True
            ).pack(anchor="w")

        # —— 1. AVISOS (CONTAINER) ——
        avisos_container = fabricas.criar_frame(self.frame, bg=estilo.Cor.Fundo.PRINCIPAL)
        avisos_container.pack(fill="x", pady=(estilo.Padding.PADRAO, estilo.Padding.PADRAO))

        # —— 2. CARTÕES DE RESUMO ——
        total = len(self.aplicacao.resultados_validacao)
        em_producao = sum(
            1 for resultado in self.aplicacao.resultados_validacao.values() 
            if resultado.status == "VÁLIDO" 
            or resultado.status == "EM_PRODUCAO"
        )
        bloqueados = sum(
            1 for resultado in self.aplicacao.resultados_validacao.values() 
            if resultado.status == "RETIDO"
        )
        concluidos = sum(
            1 for resultado in self.aplicacao.resultados_validacao.values() 
            if resultado.status == "CONCLUÍDO"
        )

        cartoes = fabricas.criar_frame(self.frame, bg=estilo.Cor.Fundo.PRINCIPAL)
        cartoes.pack(fill="x", pady=estilo.Padding.PADRAO)

        self.criar_cartao(cartoes, "Total", total, estilo.Cor.Texto.PADRAO, "📦")
        self.criar_cartao(cartoes, "Em Produção", em_producao, estilo.Cor.Status.PRODUCAO, "⌛")
        self.criar_cartao(cartoes, "Retidos", bloqueados, estilo.Cor.Status.RETIDO, "❌")
        self.criar_cartao(cartoes, "Concluídos", concluidos, estilo.Cor.Status.CONCLUIDO, "✔️")

        # —— 3. LISTA DE PEDIDOS E BOTÕES DE AÇÃO ——
        cabecalho_lista = fabricas.criar_frame(self.frame, bg=estilo.Cor.Fundo.PRINCIPAL)
        cabecalho_lista.pack(fill="x", pady=(estilo.Padding.PADRAO, estilo.Padding.PEQUENO))

        fabricas.criar_label(
            cabecalho_lista, 
            "Visão Geral dos Pedidos:", 
            estilo.Fonte.Tamanho.SUBTITULO, 
            bg=estilo.Cor.Fundo.PRINCIPAL, 
            bold=True
            ).pack(side="left")

        # Botão de Concluir (Empacotado primeiro -> fica na ponta direita)
        btn_concluir = fabricas.criar_botao(
            cabecalho_lista, 
            "✓ Marcar Concluído", 
            self.marcar_concluido, 
            largura=estilo.Dimensao.Botao.Dashboard.Concluido.LARGURA
        )
        btn_concluir.pack(
            side="right", 
            padx=estilo.Padding.Dashboard.BOTAO_X, 
            ipady=estilo.Padding.Dashboard.BOTAO_Y
        )

        # Botão de Reverter (Empacotado depois -> fica à esquerda do Concluir)
        btn_reverter = fabricas.criar_botao(
            cabecalho_lista, 
            "↩ Reverter", 
            self.reverter_producao, 
            largura=estilo.Dimensao.Botao.Dashboard.Reverter.LARGURA
        )
        btn_reverter.pack(
            side="right", 
            padx=estilo.Padding.Dashboard.BOTAO_X, 
            ipady=estilo.Padding.Dashboard.BOTAO_Y
        )

        # Botão de Importar Estoque (Empacotado por último -> fica à esquerda do Reverter)
        btn_estoque = fabricas.criar_botao(
            cabecalho_lista, 
            "📦 Importar arquivo de estoque", 
            self.importar_estoque, 
            largura=estilo.Dimensao.Botao.Dashboard.Estoque.LARGURA
        )
        btn_estoque.pack(
            side="right", 
            padx=estilo.Padding.Dashboard.BOTAO_X, 
            ipady=estilo.Padding.Dashboard.BOTAO_Y
        )

        # Container com scroll
        lista_container = fabricas.criar_frame(self.frame, bg=estilo.Cor.Fundo.PRINCIPAL)
        lista_container.pack(fill="both", expand=True)

        canvas_lista = fabricas.criar_canvas(
            lista_container, bg=estilo.Cor.Fundo.PRINCIPAL
        )
        scrollbar = fabricas.criar_scrollbar(
            lista_container, orient="vertical", command=canvas_lista.yview
        )
        lista_interna = fabricas.criar_frame(
            canvas_lista, bg=estilo.Cor.Fundo.PRINCIPAL
        )

        # Força o Tkinter a calcular a largura do canvas antes de criar a janela
        canvas_lista.update_idletasks()

        lista_interna.bind(
            "<Configure>", 
            lambda e: canvas_lista.configure(scrollregion=canvas_lista.bbox("all"))
        )
        canvas_lista.create_window(
            (0, 0), 
            window=lista_interna, 
            anchor="nw", 
            width=canvas_lista.winfo_width()
        )
        canvas_lista.configure(yscrollcommand=scrollbar.set)
        canvas_lista.bind(
            "<Configure>", 
            lambda e: canvas_lista.itemconfig(canvas_lista.find_all()[0], width=e.width)
        )

        canvas_lista.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Cabeçalho da Tabela
        header = fabricas.criar_frame(lista_interna, bg=estilo.Cor.Fundo.PRINCIPAL)
        header.config(pady=estilo.Padding.Dashboard.HEADER_Y)
        header.pack(fill="x")

        # Colunas (Novo Layout: Status, Pedido, Prazo, Observação)
        coluna_status = self.criar_coluna_fixa(
            header, 
            estilo.Dimensao.Coluna.STATUS, 
            estilo.Cor.Fundo.PRINCIPAL
        )
        coluna_pedido = self.criar_coluna_fixa(
            header, 
            estilo.Dimensao.Coluna.PEDIDO, 
            estilo.Cor.Fundo.PRINCIPAL
        )
        coluna_prazo = self.criar_coluna_fixa(
            header, 
            estilo.Dimensao.Coluna.PRAZO, 
            estilo.Cor.Fundo.PRINCIPAL
        )
        coluna_obs = self.criar_coluna_fixa(
            header, 
            estilo.Dimensao.Coluna.OBSERVACAO, 
            estilo.Cor.Fundo.PRINCIPAL
        )
        
        # Espaçador invisível para empurrar as colunas para a esquerda
        espacador = fabricas.criar_frame(header, bg=estilo.Cor.Fundo.PRINCIPAL)
        espacador.pack(side="left", fill="y", expand=True)

        fabricas.criar_label(
            coluna_status, 
            "Status", 
            estilo.Fonte.Tamanho.Dashboard.Coluna.TITULO, 
            cor=estilo.Cor.Texto.MUTED, 
            bg=estilo.Cor.Fundo.PRINCIPAL
        ).place(relx=0.5, rely=0.5, anchor="center")

        fabricas.criar_label(
            coluna_pedido, 
            "Pedido", 
            estilo.Fonte.Tamanho.Dashboard.Coluna.TITULO, 
            cor=estilo.Cor.Texto.MUTED, 
            bg=estilo.Cor.Fundo.PRINCIPAL
        ).place(relx=0.5, rely=0.5, anchor="center")

        fabricas.criar_label(
            coluna_prazo, 
            "Prazo", 
            estilo.Fonte.Tamanho.Dashboard.Coluna.TITULO, 
            cor=estilo.Cor.Texto.MUTED, 
            bg=estilo.Cor.Fundo.PRINCIPAL
        ).place(relx=0.5, rely=0.5, anchor="center")

        fabricas.criar_label(
            coluna_obs, 
            "Observação", 
            estilo.Fonte.Tamanho.Dashboard.Coluna.TITULO, 
            cor=estilo.Cor.Texto.MUTED, 
            bg=estilo.Cor.Fundo.PRINCIPAL
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Linhas da Tabela
        self.construir_linhas(lista_interna)

        # Avisos
        self.construir_avisos(avisos_container)

        return self.frame
    

    def criar_cartao(self, parent, titulo, valor, cor, icone):
        cartao = fabricas.criar_frame(parent, bg=estilo.Cor.Fundo.PAINEL)
        cartao.config(
            padx=estilo.Padding.Dashboard.Cartao.Interno.X, 
            pady=estilo.Padding.Dashboard.Cartao.Interno.Y, 
            relief="solid", 
            borderwidth=1
        )
        cartao.pack(
            side="left", 
            padx=estilo.Padding.Dashboard.Cartao.Externo.X, 
            expand=True, 
            fill="x"
        )
        
        linha_titulo = fabricas.criar_frame(cartao, bg=estilo.Cor.Fundo.PAINEL)
        linha_titulo.pack(anchor="w")
        
        fabricas.criar_label(
            linha_titulo, 
            icone, 
            estilo.Fonte.Tamanho.PEQUENO, 
            cor=estilo.Cor.Texto.MUTED,
            bg=estilo.Cor.Fundo.PAINEL
        ).pack(side="left")

        fabricas.criar_label(
            linha_titulo, 
            f" {titulo}", 
            estilo.Fonte.Tamanho.PEQUENO, 
            cor=estilo.Cor.Texto.MUTED, 
            bg=estilo.Cor.Fundo.PAINEL
        ).pack(side="left")
        
        fabricas.criar_label(
            cartao, 
            str(valor), 
            estilo.Fonte.Tamanho.TITULO, 
            cor=cor, 
            bg=estilo.Cor.Fundo.PAINEL, 
            bold=True
        ).pack(anchor="w")

    def criar_coluna_fixa(self, parent, largura, bg):
        coluna = fabricas.criar_frame(parent, bg=bg)
        coluna.config(width=largura)
        coluna.pack(side="left", fill="both")
        coluna.pack_propagate(False)
        coluna.config(height=30) 
        return coluna

    def construir_linhas(self, lista_interna):
        for index, pedido in enumerate(self.aplicacao.pedidos_importados):
            resultado = self.aplicacao.resultados_validacao.get(pedido.numero)
            if not resultado:
                continue

            if resultado.status == "CONCLUÍDO":
                icone = "✔️"
                cor_icone = estilo.Cor.Status.CONCLUIDO
                cor_fundo_linha = estilo.Cor.Fundo.PAINEL
                obs_texto = "Concluído"
                cor_obs = estilo.Cor.Status.CONCLUIDO

            elif resultado.status == "RETIDO":
                icone = "❌"
                cor_icone = estilo.Cor.Status.RETIDO
                cor_fundo_linha = estilo.Cor.Fundo.PAINEL if index % 2 == 0 else estilo.Cor.Fundo.ZEBRA
                obs_texto = resultado.motivo
                cor_obs = estilo.Cor.Status.RETIDO

            else:
                icone = "⌛"
                cor_icone = estilo.Cor.Status.PRODUCAO
                cor_fundo_linha = estilo.Cor.Fundo.PAINEL if index % 2 == 0 else estilo.Cor.Fundo.ZEBRA
                obs_texto = "Em produção"
                cor_obs = estilo.Cor.Status.PRODUCAO

            linha = fabricas.criar_frame(lista_interna, bg=cor_fundo_linha)
            linha.config(cursor="hand2", height=35) 
            linha.pack(fill="x", pady=estilo.Padding.PEQUENO)
            linha.pack_propagate(False)
            
            linha._selecionada = False # Controle para o hover

            # Cria as 4 colunas
            coluna_status = self.criar_coluna_fixa(
                linha, 
                estilo.Dimensao.Coluna.STATUS, 
                cor_fundo_linha
            )
            coluna_pedido = self.criar_coluna_fixa(
                linha, 
                estilo.Dimensao.Coluna.PEDIDO, 
                cor_fundo_linha
            )
            coluna_prazo = self.criar_coluna_fixa(
                linha, 
                estilo.Dimensao.Coluna.PRAZO, 
                cor_fundo_linha
            )
            coluna_obs = self.criar_coluna_fixa(
                linha, 
                estilo.Dimensao.Coluna.OBSERVACAO, 
                cor_fundo_linha
            )
            
            # Espaçador invisível
            espacador = fabricas.criar_frame(linha, bg=cor_fundo_linha)
            espacador.pack(side="left", fill="both", expand=True)

            for coluna in [coluna_status, coluna_pedido, coluna_prazo, coluna_obs]:
                coluna.bind(
                    "<Button-1>", 
                    lambda e, 
                    numero=pedido.numero, 
                    frame=linha, 
                    cor=cor_fundo_linha: self.selecionar_linha(numero, frame, cor)
                )

            # --- Status (Apenas o emoji) ---
            lbl_icone = fabricas.criar_label_emoji(
                coluna_status, 
                icone, 
                estilo.Fonte.Tamanho.Dashboard.Coluna.CONTEUDO, 
                cor=cor_icone, 
                bg=cor_fundo_linha
            )
            lbl_icone.place(relx=0.5, rely=0.5, anchor="center")
            lbl_icone.bind(
                "<Button-1>", 
                lambda e, 
                numero=pedido.numero, 
                frame=linha, 
                cor=cor_fundo_linha: self.selecionar_linha(numero, frame, cor)
            )

            # --- Pedido (Link) ---
            lbl_pedido = fabricas.criar_label(
                coluna_pedido, 
                pedido.numero, 
                estilo.Fonte.Tamanho.Dashboard.PEDIDO, 
                cor=estilo.Cor.Texto.PADRAO, 
                bg=cor_fundo_linha,
                bold=True
            )
            lbl_pedido.place(relx=0.5, rely=0.5, anchor="center")
            lbl_pedido.config(cursor="hand2")

            # --- Prazo ---
            cor_data = estilo.Cor.Texto.PADRAO
            if resultado.status != "CONCLUÍDO" and pedido.prazo:
                data_entrega = datetime.strptime(pedido.prazo, "%Y-%m-%d %H:%M:%S")
                texto_prazo = data_entrega.strftime("%d/%m/%Y %H:%M")
                dias_restantes = (data_entrega - self.hoje).days
                if dias_restantes < 0:
                    texto_prazo += f" (Atrasado {abs(dias_restantes)}d)"
                    cor_data = estilo.Cor.Status.RETIDO
                elif dias_restantes == 0:
                    texto_prazo += " (Hoje!)"
                    cor_data = estilo.Cor.Status.PRODUCAO
                else:
                    texto_prazo += f" ({dias_restantes}d)"
            elif resultado.status == "CONCLUÍDO":
                texto_prazo = "Concluído"
                cor_data = estilo.Cor.Status.CONCLUIDO
            else:
                texto_prazo = "—"

            lbl_prazo = fabricas.criar_label(
                coluna_prazo, 
                texto_prazo, 
                estilo.Fonte.Tamanho.Dashboard.Coluna.CONTEUDO, 
                cor=cor_data, 
                bg=cor_fundo_linha
            )
            lbl_prazo.place(relx=0.5, rely=0.5, anchor="center")
            lbl_prazo.bind(
                "<Button-1>", 
                lambda e, 
                numero=pedido.numero, 
                frame=linha, 
                cor=cor_fundo_linha: self.selecionar_linha(numero, frame, cor)
            )

            # --- Observação ---
            lbl_obs = fabricas.criar_label(
                coluna_obs, 
                obs_texto, 
                estilo.Fonte.Tamanho.Dashboard.Coluna.CONTEUDO, 
                cor=cor_obs, 
                bg=cor_fundo_linha
            )
            lbl_obs.place(relx=0.5, rely=0.5, anchor="center")
            lbl_obs.bind(
                "<Button-1>", 
                lambda e, 
                numero=pedido.numero, 
                frame=linha, 
                cor=cor_fundo_linha: self.selecionar_linha(numero, frame, cor)
            )

            # Chama o hover (fade na linha) e os cliques de forma unificada
            animacao.hover_linha_zebra(
                linha=linha,
                cor_zebra=cor_fundo_linha,
                cor_hover=estilo.Cor.Acao.HOVER_ZEBRA,
                clique_1=(
                    lambda e, 
                    num=pedido.numero, 
                    linha=linha, 
                    cor=cor_fundo_linha: self.selecionar_linha(num, linha, cor)
                ),
                clique_2=(
                    lambda e, 
                    pedido=pedido: janela_informacoes.abrir_janela_informacoes(self.root, pedido)
                )
            )

    def construir_avisos(self, avisos_container):
        pedidos_atrasados = []
        pedidos_hoje = []
        pedidos_proximos = []

        for pedido in self.aplicacao.pedidos_importados:
            resultado = self.aplicacao.resultados_validacao.get(pedido.numero)
            if (
                resultado 
                and resultado.status != "CONCLUÍDO" 
                and resultado.status != "RETIDO" 
                and pedido.prazo
            ):
                data_entrega = datetime.strptime(pedido.prazo, "%Y-%m-%d %H:%M:%S")
                delta = (data_entrega - self.hoje).days

                if delta < 0:
                    pedidos_atrasados.append((pedido, delta, "Atrasado"))
                elif delta == 0:
                    pedidos_hoje.append((pedido, delta, "Vence hoje"))
                elif delta <= 2:
                    dia = "dia" if delta == 1 else "dias"
                    pedidos_proximos.append((pedido, delta, f"Vence em {delta} {dia}"))

        if pedidos_atrasados:
            avisos_atrasados_frame = fabricas.criar_frame(
                avisos_container, 
                bg=estilo.Cor.Fundo.ZEBRA,
                highlightbackground=estilo.Cor.Status.ALERTA,
                highlightthickness=1 # 
            )
            avisos_atrasados_frame.config(
                padx=estilo.Padding.PADRAO, 
                pady=estilo.Padding.PADRAO
            )
            avisos_atrasados_frame.pack(fill="x", pady=estilo.Padding.PEQUENO)

            linha_titulo_atrasado = fabricas.criar_frame(avisos_atrasados_frame, bg=estilo.Cor.Fundo.ZEBRA)
            linha_titulo_atrasado.pack(anchor="w", pady=estilo.Padding.PEQUENO)
            
            fabricas.criar_label(
                linha_titulo_atrasado, 
                "●", 
                estilo.Fonte.Tamanho.NORMAL, 
                cor=estilo.Cor.Status.ALERTA, 
                bg=estilo.Cor.Fundo.ZEBRA
            ).pack(side="left")

            fabricas.criar_label(
                linha_titulo_atrasado, 
                "ATRASADOS:", 
                estilo.Fonte.Tamanho.NORMAL, 
                cor=estilo.Cor.Status.ALERTA, 
                bg=estilo.Cor.Fundo.ZEBRA, 
                bold=True
            ).pack(side="left")

            for pedido, delta, status_texto in pedidos_atrasados:
                dia = "dia" if abs(delta) == 1 else "dias"
                self.renderizar_aviso(
                    avisos_atrasados_frame, 
                    "●", 
                    f"Pedido {pedido.numero} ({pedido.cliente}) — Atrasado há {abs(delta)} {dia} ({pedido.prazo})", 
                    estilo.Cor.Fundo.ZEBRA, 
                    estilo.Cor.Status.ALERTA
                )

        if pedidos_hoje:
            avisos_hoje_frame = fabricas.criar_frame(
                avisos_container, 
                bg=estilo.Cor.Fundo.PRINCIPAL,
                highlightbackground=estilo.Cor.Status.ALERTA,
                highlightthickness=1
            )
            avisos_hoje_frame.config(
                padx=estilo.Padding.PADRAO, 
                pady=estilo.Padding.PADRAO
            )
            avisos_hoje_frame.pack(fill="x", pady=estilo.Padding.PEQUENO)

            linha_titulo_hoje = fabricas.criar_frame(avisos_hoje_frame, bg=estilo.Cor.Fundo.PRINCIPAL)
            linha_titulo_hoje.pack(anchor="w", pady=estilo.Padding.PEQUENO)
            
            lbl_icone_hoje = fabricas.criar_label(
                linha_titulo_hoje, 
                "⚠️", 
                estilo.Fonte.Tamanho.NORMAL, 
                cor=estilo.Cor.Status.ALERTA, 
                bg=estilo.Cor.Fundo.PRINCIPAL
            )
            lbl_icone_hoje.pack(side="left")

            lbl_titulo_hoje = fabricas.criar_label(
                linha_titulo_hoje, 
                "VENCE HOJE:", 
                estilo.Fonte.Tamanho.NORMAL, 
                cor=estilo.Cor.Status.ALERTA, 
                bg=estilo.Cor.Fundo.PRINCIPAL, 
                bold=True
            )
            lbl_titulo_hoje.pack(side="left")

            # Coleta os widgets para a animação
            widgets_pulsantes = [linha_titulo_hoje, lbl_icone_hoje, lbl_titulo_hoje]

            for pedido, delta, status_texto in pedidos_hoje:                
                # Cria o aviso e o adiciona na lista que sofrerá o efeito de pulso
                linha_aviso = fabricas.criar_frame(avisos_hoje_frame, bg=estilo.Cor.Fundo.PRINCIPAL)
                linha_aviso.pack(anchor="w")
                
                lbl_bullet = fabricas.criar_label(
                    linha_aviso, 
                    "●", 
                    estilo.Fonte.Tamanho.NORMAL, 
                    cor=estilo.Cor.Status.ALERTA, 
                    bg=estilo.Cor.Fundo.PRINCIPAL
                )
                lbl_bullet.pack(side="left")
                
                lbl_texto = fabricas.criar_label(
                    linha_aviso, 
                    f" Pedido {pedido.numero} ({pedido.cliente}) — Entrega hoje ({pedido.prazo})", 
                    estilo.Fonte.Tamanho.NORMAL, 
                    cor=estilo.Cor.Status.ALERTA, 
                    bg=estilo.Cor.Fundo.PRINCIPAL
                )
                lbl_texto.pack(side="left")

                widgets_pulsantes.extend([linha_aviso, lbl_bullet, lbl_texto])

            # Inicia a animação
            cor_pulso = estilo.Cor.Animacao.Dashboard.Pulso.PRAZO_HOJE
            animacao.pulsar_cor_frame(
                frame=avisos_hoje_frame,
                widgets=widgets_pulsantes,
                cor_base=estilo.Cor.Fundo.PRINCIPAL,
                cor_pulso=cor_pulso
            )

        if pedidos_proximos:
            avisos_proximos_frame = fabricas.criar_frame(
                avisos_container, 
                bg=estilo.Cor.Fundo.PRINCIPAL,
                highlightbackground=estilo.Cor.Status.ATENCAO,
                highlightthickness=1
            )
            avisos_proximos_frame.config(
                padx=estilo.Padding.PADRAO, 
                pady=estilo.Padding.PADRAO
            )
            avisos_proximos_frame.pack(fill="x")

            linha_titulo_proximo = fabricas.criar_frame(
                avisos_proximos_frame, 
                bg=estilo.Cor.Fundo.PRINCIPAL
            )
            linha_titulo_proximo.pack(anchor="w", pady=estilo.Padding.PEQUENO)
            
            lbl_icone_proximo = fabricas.criar_label(
                linha_titulo_proximo, 
                "⚠️", 
                estilo.Fonte.Tamanho.NORMAL, 
                cor=estilo.Cor.Status.ATENCAO, 
                bg=estilo.Cor.Fundo.PRINCIPAL
            )
            lbl_icone_proximo.pack(side="left")

            lbl_titulo_proximo = fabricas.criar_label(
                linha_titulo_proximo, 
                "Prazos Próximos:", 
                estilo.Fonte.Tamanho.NORMAL, 
                cor=estilo.Cor.Status.ATENCAO, 
                bg=estilo.Cor.Fundo.PRINCIPAL, 
                bold=True
            )
            lbl_titulo_proximo.pack(side="left")

            # Coleta os widgets para a animação
            widgets_pulsantes = [linha_titulo_proximo, lbl_icone_proximo, lbl_titulo_proximo]

            for pedido, delta, status_texto in pedidos_proximos:
                # Cria o container do aviso para que seus elementos recebam a animação de pulso
                linha_aviso = fabricas.criar_frame(avisos_proximos_frame, bg=estilo.Cor.Fundo.PRINCIPAL)
                linha_aviso.pack(anchor="w")
                
                lbl_bullet = fabricas.criar_label(
                    linha_aviso, 
                    "●", 
                    estilo.Fonte.Tamanho.NORMAL, 
                    cor=estilo.Cor.Status.ATENCAO, 
                    bg=estilo.Cor.Fundo.PRINCIPAL
                )
                lbl_bullet.pack(side="left")
                
                lbl_texto = fabricas.criar_label(
                    linha_aviso, 
                    f" Pedido {pedido.numero} ({pedido.cliente}) — {status_texto} ({pedido.prazo})", 
                    estilo.Fonte.Tamanho.NORMAL, 
                    cor=estilo.Cor.Status.ATENCAO, 
                    bg=estilo.Cor.Fundo.PRINCIPAL
                )
                lbl_texto.pack(side="left")

                widgets_pulsantes.extend([linha_aviso, lbl_bullet, lbl_texto])

            # Inicia a animação
            cor_pulso = estilo.Cor.Animacao.Dashboard.Pulso.PRAZO_PROXIMO
            animacao.pulsar_cor_frame(
                frame=avisos_proximos_frame,
                widgets=widgets_pulsantes,
                cor_base=estilo.Cor.Fundo.PRINCIPAL,
                cor_pulso=cor_pulso
            )

        if (
            not pedidos_atrasados 
            and not pedidos_hoje 
            and not pedidos_proximos
        ):
            avisos_vazio_frame = fabricas.criar_frame(
                avisos_container, 
                bg=estilo.Cor.Fundo.PRINCIPAL,
                highlightbackground=estilo.Cor.Borda.PADRAO, 
                highlightthickness=1
            )
            avisos_vazio_frame.config(
                padx=estilo.Padding.PADRAO, 
                pady=estilo.Padding.PADRAO
            )
            avisos_vazio_frame.pack(fill="x")
            fabricas.criar_label(
                avisos_vazio_frame, 
                "Não há pedidos com prazo urgente.",
                estilo.Fonte.Tamanho.NORMAL, 
                cor=estilo.Cor.Texto.MUTED, 
                bg=estilo.Cor.Fundo.PRINCIPAL
            ).pack(anchor="w")

    def renderizar_aviso(self, parent, emoji, texto, cor_fundo, cor_texto):
        linha_aviso = fabricas.criar_frame(parent, bg=cor_fundo)
        linha_aviso.pack(anchor="w")

        fabricas.criar_label(
            linha_aviso, 
            emoji, 
            estilo.Fonte.Tamanho.NORMAL, 
            cor=cor_texto, 
            bg=cor_fundo
        ).pack(side="left")

        fabricas.criar_label(
            linha_aviso, 
            f" {texto}", 
            estilo.Fonte.Tamanho.NORMAL, 
            cor=cor_texto, 
            bg=cor_fundo
        ).pack(side="left")

    def selecionar_linha(self, num_pedido, linha_frame, cor_original):
        if self.linha_selecionada["frame"] is not None:
            self.linha_selecionada["frame"]._selecionada = False
            self.mudar_cor_recursivo(
                self.linha_selecionada["frame"], 
                self.linha_selecionada["tag_original"]
            )

        self.linha_selecionada["id"] = num_pedido
        self.linha_selecionada["frame"] = linha_frame
        self.linha_selecionada["tag_original"] = cor_original
        linha_frame._selecionada = True

        self.mudar_cor_recursivo(linha_frame, estilo.Cor.Acao.ATIVO_ZEBRA)

    def mudar_cor_recursivo(self, widget, cor):
        try:
            widget.config(bg=cor)
        except Exception:
            pass 
        for child in widget.winfo_children():
            self.mudar_cor_recursivo(child, cor)

    def marcar_concluido(self):
        if self.linha_selecionada["id"] is None:
            return
        
        num_pedido = self.linha_selecionada["id"]
        status_atual = self.aplicacao.resultados_validacao[num_pedido].status
        
        # Ajuste implementado após feedback da validação prática:
        # O gestor agora pode concluir pedidos "RETIDOS" caso o problema
        # tenha sido resolvido externamente (ex: arte enviada depois).
        if status_atual != "CONCLUÍDO":
            self.aplicacao.resultados_validacao[num_pedido].status = "CONCLUÍDO"
            self.aplicacao.resultados_validacao[num_pedido].motivo = "Finalizado pelo gestor (ajuste pós-validação)"
            self.atualizar_tela()

    def reverter_producao(self):
        if self.linha_selecionada["id"] is None:
            return
        num_pedido = self.linha_selecionada["id"]
        if self.aplicacao.resultados_validacao[num_pedido].status == "CONCLUÍDO":
            self.aplicacao.resultados_validacao[num_pedido].status = "VÁLIDO"
            self.aplicacao.resultados_validacao[num_pedido].motivo = ""
            self.atualizar_tela()

    def atualizar_tela(self):
        self.frame.destroy()
        nova_tela = TelaDashboard(self.root, self.aplicacao)
        nova_tela.construir().pack(fill="both", expand=True)
        self.aplicacao.tela_dashboard = nova_tela.frame

    def importar_estoque(self):
        from tkinter import filedialog, messagebox
        from controladores import (
            leitor_planilha, 
            db_construtor, 
            db_leitor, 
            validador_pedidos
        )

        caminho = filedialog.askopenfilename(
            title="Mamoru — Selecione a planilha de estoque exportada pelo AJXCommerce",
            filetypes=[("Planilhas", "*.xlsx *.ods"), ("Todos os arquivos", "*.*")]
        )

        if not caminho:
            return

        try:
            estoque_lido = leitor_planilha.ler_planilha_estoque(caminho)
            if not estoque_lido:
                messagebox.showwarning(
                    "Mamoru — Erro", 
                    "Nenhum produto válido encontrado na planilha."
                )
                return

            db_construtor.inicializar_banco()
            db_construtor.salvar_estoque(estoque_lido)

            self.aplicacao.estoque_atual = db_leitor.carregar_estoque()
            
            self.aplicacao.resultados_validacao = {}
            for pedido in self.aplicacao.pedidos_importados:
                resultado = validador_pedidos.validar_pedido(pedido, self.aplicacao.estoque_atual)
                self.aplicacao.resultados_validacao[pedido.numero] = resultado

            messagebox.showinfo(
                "Mamoru — Sucesso", 
                "Estoque importado e pedidos revalidados."
            )
            self.atualizar_tela()

        except Exception as erro:
            messagebox.showerror(
                "Mamoru — Erro na Importação", 
                f"Ocorreu um erro ao ler a planilha:\n{erro}"
            )