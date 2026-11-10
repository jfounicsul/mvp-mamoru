"""
Módulo unificado de animações do Mamoru.
Isola a matemática de interpolação de cores e os loops de tempo.
"""

import math


def _hex_para_rgb(hex_color: str) -> tuple:
    """Converte '#RRGGBB' para uma tupla (R, G, B)."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _rgb_para_hex(rgb: tuple) -> str:
    """Converte uma tupla (R, G, B) para '#RRGGBB'."""
    return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'


def pulsar_cor_frame(frame, widgets, cor_base, cor_pulso, forca_maxima=0.3):
    """
    Faz a cor de fundo pulsar, usando a cor de pulso como um overlay
    com opacidade variável. Assim a cor nunca
    "estoura" além do tom do pulso.
    """
    base_rgb = _hex_para_rgb(cor_base)
    pulse_rgb = _hex_para_rgb(cor_pulso)

    # Dicionário de estado para controle do loop
    estado = {
        "passo": 0,
        "subindo": True,
        "pausa": 0
    }

    def loop_animacao():
        pulse_delay_ms = 30
        pulse_steps = 120
        pulse_pause = 15

        # Se o frame for destruído (ex: troca de tela), para a animação
        if not frame.winfo_exists():
            return

        # Lógica de pausa entre as ondas
        if estado["pausa"] > 0:
            estado["pausa"] -= 1
            frame.after(pulse_delay_ms, loop_animacao)
            return

        # Calcula a "força" do pulso (0.0 a 1.0) com suavização
        ratio = estado["passo"] / pulse_steps
        ratio = 0.5 - 0.5 * math.cos(math.pi * ratio)  # Ease-in-out

        # Aplica a intensidade máxima desejada (ex: 0.3 = 30% da cor de pulso)
        intensidade = ratio * forca_maxima

        # Blend: base + (pulso - base) * intensidade
        # Isso garante que a cor final nunca ultrapasse a cor de pulso.
        cor_atual_rgb = (
            int(base_rgb[0] + (pulse_rgb[0] - base_rgb[0]) * intensidade),
            int(base_rgb[1] + (pulse_rgb[1] - base_rgb[1]) * intensidade),
            int(base_rgb[2] + (pulse_rgb[2] - base_rgb[2]) * intensidade)
        )
        cor_atual = _rgb_para_hex(cor_atual_rgb)

        # Pinta o frame e todos os widgets passados
        try:
            frame.configure(bg=cor_atual)
            for widget in widgets:
                if widget.winfo_exists():
                    widget.configure(bg=cor_atual)
        except Exception:
            return

        # Atualiza o estado
        if estado["subindo"]:
            estado["passo"] += 1
            if estado["passo"] >= pulse_steps:
                estado["passo"] = pulse_steps
                estado["subindo"] = False
                estado["pausa"] = pulse_pause
        else:
            estado["passo"] -= 1
            if estado["passo"] <= 0:
                estado["passo"] = 0
                estado["subindo"] = True
                estado["pausa"] = pulse_pause

        # Reagenda o próximo frame
        frame.after(pulse_delay_ms, loop_animacao)

    # Inicia o loop
    loop_animacao()

def fade_in_janela(janela, passos=15, delay=15):
    """Faz a janela aparecer suavemente."""
    # 1. Garante que ela está invisível e escondida
    janela.attributes("-alpha", 0.0)
    janela.withdraw()
    
    # 2. Processa o layout e o geometry sem desenhar na tela ainda
    janela.update_idletasks()
    
    # 3. Mostra a janela (ainda invisível, mas já no lugar certo)
    janela.deiconify()
    
    alpha_atual = 0.0

    def passo():
        nonlocal alpha_atual
        if not janela.winfo_exists():
            return
        
        # Incrementa o alpha
        alpha_atual += 1.0 / passos
        if alpha_atual >= 1.0:
            janela.attributes("-alpha", 1.0)
            return
        
        janela.attributes("-alpha", alpha_atual)
        janela.after(delay, passo)

    # 4. Inicia o loop de fade
    janela.after(delay, passo)


def fade_out_janela(janela, ao_terminar, passos=15, delay=15):
    """Faz a janela desaparecer suavemente e depois executa a função de fechar."""
    alpha_atual = 1.0
    
    def passo():
        nonlocal alpha_atual
        if not janela.winfo_exists():
            return
        
        alpha_atual -= 1.0 / passos
        if alpha_atual <= 0.0:
            janela.attributes("-alpha", 0.0)

            # Espera 50ms para o Windows processar o alpha 0.0 antes de destruir
            janela.after(50, ao_terminar)
            return
        
        janela.attributes("-alpha", alpha_atual)
        janela.after(delay, passo)

    passo()



def animar_cor_texto(label, cor_inicio, cor_fim):
    """Faz o texto de um label transicionar suavemente entre duas cores."""

    hover_passos = 12
    hover_delay_ms = 15

    inicio_rgb = _hex_para_rgb(cor_inicio)
    fim_rgb = _hex_para_rgb(cor_fim)
    
    estado = {"passo": 0}

    def loop():
        if not label.winfo_exists():
            return

        ratio = estado["passo"] / hover_passos

        # Curva de suavização
        ratio = 0.5 - 0.5 * math.cos(math.pi * ratio)

        cor_atual_rgb = (
            int(inicio_rgb[0] + (fim_rgb[0] - inicio_rgb[0]) * ratio),
            int(inicio_rgb[1] + (fim_rgb[1] - inicio_rgb[1]) * ratio),
            int(inicio_rgb[2] + (fim_rgb[2] - inicio_rgb[2]) * ratio)
        )
        
        label.config(fg=_rgb_para_hex(cor_atual_rgb))

        if estado["passo"] < hover_passos:
            estado["passo"] += 1
            label.after(hover_delay_ms, loop)

    loop()

def animar_fundo_linha(linha, widgets, cor_inicio, cor_fim):
    """Faz o fundo da linha inteira transicionar suavemente."""
    hover_passos = 12
    hover_delay_ms = 15

    inicio_rgb = _hex_para_rgb(cor_inicio)
    fim_rgb = _hex_para_rgb(cor_fim)
    
    # Cancela animação anterior se existir
    if hasattr(linha, "_anim_fundo_id") and linha._anim_fundo_id:
        try:
            linha.after_cancel(linha._anim_fundo_id)
        except Exception:
            pass

    estado = {"passo": 0}

    def loop():
        if not linha.winfo_exists():
            return

        ratio = estado["passo"] / hover_passos
        ratio = 0.5 - 0.5 * math.cos(math.pi * ratio)

        cor_atual_rgb = (
            int(inicio_rgb[0] + (fim_rgb[0] - inicio_rgb[0]) * ratio),
            int(inicio_rgb[1] + (fim_rgb[1] - inicio_rgb[1]) * ratio),
            int(inicio_rgb[2] + (fim_rgb[2] - inicio_rgb[2]) * ratio)
        )
        cor_atual = _rgb_para_hex(cor_atual_rgb)

        try:
            linha.config(bg=cor_atual)
            for widget in widgets:
                if widget.winfo_exists():
                    widget.config(bg=cor_atual)
        except Exception:
            return

        if estado["passo"] < hover_passos:
            estado["passo"] += 1
            linha._anim_fundo_id = linha.after(hover_delay_ms, loop)
        else:
            linha._anim_fundo_id = None

    loop()


def hover_linha_zebra(linha, cor_zebra, cor_hover, clique_1, clique_2):
    """Aplica o fade no fundo da linha e os cliques em todos os filhos."""
    
    # Coleta todos os widgets da linha para pintar juntos
    widgets = []
    def coletar(widget):
        widgets.append(widget)
        for child in widget.winfo_children():
            coletar(child)
    coletar(linha)

    # Remove a própria linha da lista (ela é pintada separadamente na função)
    widgets.remove(linha)

    def entrar(event):
        animar_fundo_linha(linha, widgets, cor_zebra, cor_hover)

    def sair(event):
        if getattr(linha, "_selecionada", False):
            return
        animar_fundo_linha(linha, widgets, cor_hover, cor_zebra)

    def aplicar_binds(widget):
        widget.bind("<Enter>", entrar, add="+")
        widget.bind("<Leave>", sair, add="+")
        widget.bind("<Button-1>", clique_1, add="+")
        widget.bind("<Double-Button-1>", clique_2, add="+")
        for child in widget.winfo_children():
            aplicar_binds(child)

    aplicar_binds(linha)


def pulsar_cor_emoji(label, cor_base):
    """
    Faz o emoji pulsar continuamente entre a cor_base e uma versão mais clara dela.
    """
    # 1. Variáveis de controle (ajuste aqui a velocidade e a intensidade)
    passos = 20         
    delay = 40            
    clareamento = 0.2   

    base_rgb = _hex_para_rgb(cor_base)
    
    # 2. Calcula a cor intensa (mais clara que a base)
    intensa_rgb = (
        min(255, int(base_rgb[0] + (255 - base_rgb[0]) * clareamento)),
        min(255, int(base_rgb[1] + (255 - base_rgb[1]) * clareamento)),
        min(255, int(base_rgb[2] + (255 - base_rgb[2]) * clareamento))
    )
    
    estado = {"passo": 0, "subindo": True}

    def loop():
        if not label.winfo_exists():
            return

        ratio = estado["passo"] / passos
        ratio = 0.5 - 0.5 * math.cos(math.pi * ratio)

        cor_atual_rgb = (
            int(base_rgb[0] + (intensa_rgb[0] - base_rgb[0]) * ratio),
            int(base_rgb[1] + (intensa_rgb[1] - base_rgb[1]) * ratio),
            int(base_rgb[2] + (intensa_rgb[2] - base_rgb[2]) * ratio)
        )
        
        try:
            label.config(fg=_rgb_para_hex(cor_atual_rgb))
        except Exception:
            return

        if estado["subindo"]:
            estado["passo"] += 1
            if estado["passo"] >= passos:
                estado["passo"] = passos
                estado["subindo"] = False
        else:
            estado["passo"] -= 1
            if estado["passo"] <= 0:
                estado["passo"] = 0
                estado["subindo"] = True

        label._anim_emoji = label.after(delay, loop)

    if hasattr(label, "_anim_emoji"):
        try:
            label.after_cancel(label._anim_emoji)
        except Exception:
            pass

    loop()