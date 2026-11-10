import os
import sys
import tkinter

from constantes import estilo
from controladores import bootstrap
from controladores import db_construtor, db_leitor


def main() -> int:
    root = tkinter.Tk()
    root.title("MVP — Mamoru")
    largura = estilo.Dimensao.Janela.LARGURA
    altura = estilo.Dimensao.Janela.ALTURA
    pos_x = (root.winfo_screenwidth() // 2) - (largura // 2)
    pos_y = (root.winfo_screenheight() // 2) - (altura // 2)
    root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
    root.withdraw()

    # 1. Bootstrap inicializa estado, banco e a classe da aplicação
    aplicacao = bootstrap.inicializar_aplicacao(root)

    # 2. Atalho de desenvolvimento
    tela_alvo = os.environ.get("tela")
    if tela_alvo == "dashboard":
        # Fallback para o dev: só injeta se o banco estiver vazio
        db_construtor.inicializar_banco()
        if not db_leitor.carregar_pedidos():
            db_construtor.salvar_pedidos(db_construtor.importar_pedidos_ficticios())
            db_construtor.salvar_estoque(db_construtor.importar_estoque_ficticio())

        # Usa o orquestrador da aplicação para carregar e ir pro dashboard
        aplicacao.carregar_dashboard()
    else:
        # 3. Fluxo normal: começa no login
        aplicacao.iniciar()

    root.deiconify()
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())