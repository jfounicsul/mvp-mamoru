"""
Constantes visuais do Mamoru.
Unifica os valores de estilo usados pelo software.
"""

# —— Fonte ——
class Fonte:
    FAMILIA = "Segoe UI"

    class Tamanho:
        TITULO    = 18
        SUBTITULO = 14
        NORMAL    = 12
        PEQUENO   = 8

        class Dashboard:
            PEDIDO = 16

            class Coluna:
                TITULO   = 14
                CONTEUDO = 14

        class Informacoes:
            PEDIDO = 25

# —— Cor ——
class Cor:
    class Texto:
        PADRAO = "#1F2933"
        MUTED  = "#6B7280"

    class Fundo:
        PRINCIPAL = "#F4F6F8"
        PAINEL    = "#FFFFFF"
        ZEBRA     = "#EFEFEF"

    class Botao:
        FUNDO = "#E2E2E2"
        ATIVO = "#CCCCCC"

    class Borda:
        PADRAO = "#D1D5DB"

    class Acao:
        PRIMARIA    = "#2563EB"
        HOVER_ZEBRA = "#E5EEFF"
        ATIVO_ZEBRA = "#E5EEFF"

    class Status:
        CONCLUIDO = "#16A34A"
        RETIDO    = "#DC2626"
        PRODUCAO  = "#D97706"
        ALERTA    = "#DC2626"
        ATENCAO   = "#D97706"

    class Animacao:
        class Dashboard:
            class Pulso:
                PRAZO_PROXIMO = "#FFD3A5"
                PRAZO_HOJE    = "#FFB2B2"
                 


# —— Geometria ——
class Padding:
    PADRAO  = 12
    PEQUENO = 6
    GRANDE  = 24

    class Dashboard:
        BOTAO_X  = 5
        BOTAO_Y  = 1
        HEADER_Y = 5

        class Cartao:
            class Interno:
                X = 10
                Y = 10

            class Externo:
                X = 5

    class Frame:
        LOGIN = 25


class Dimensao:
    class Botao:
        LARGURA = 14
        ALTURA  = 1

        class Dashboard:
            class Concluido:
                LARGURA = 18

            class Reverter:
                LARGURA = 12

            class Estoque:
                LARGURA = 25

        class Importacao:
            LARGURA = 28

    class Janela:
        LARGURA = 1200
        ALTURA  = 800

    
    class Coluna:
        STATUS = 80
        PEDIDO = 120
        PRAZO  = 250
        OBSERVACAO = 250