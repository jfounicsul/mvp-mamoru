# ——————————————————————————————————————————————————————————————————————————
# IMPORTAÇÕES NATIVAS E CONFIGURAÇÃO DE CAMINHO
# ——————————————————————————————————————————————————————————————————————————
import http.server
import socketserver
import sys
import os
import json
import tempfile
import email.parser
import email.policy

# Garante que o Python encontre a pasta 'controladores' na raiz do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controladores import (
    db_leitor, 
    db_construtor,
    db_usuarios,
    validador_pedidos, 
    leitor_planilha, 
    seguranca
)

# ——————————————————————————————————————————————————————————————————————————
# INICIALIZAÇÃO DO BANCO E DO ESTADO GLOBAL
# ——————————————————————————————————————————————————————————————————————————
db_construtor.inicializar_banco()
db_usuarios.inicializar_tabela()

ESTADO_VALIDACAO = {}

def atualizar_estado_global():
    global ESTADO_VALIDACAO
    pedidos = db_leitor.carregar_pedidos()
    estoque = db_leitor.carregar_estoque()
    ESTADO_VALIDACAO = {}
    for pedido in pedidos:
        resultado = validador_pedidos.validar_pedido(pedido, estoque)
        ESTADO_VALIDACAO[pedido.numero] = resultado

atualizar_estado_global()

PORT = 8080

# ——————————————————————————————————————————————————————————————————————————
# HANDLER HTTP DO MAMORU
# ——————————————————————————————————————————————————————————————————————————
class MamoruWebHandler(http.server.SimpleHTTPRequestHandler):

    # ----------------------------------------------------------------------
    # ROTAS GET
    # ----------------------------------------------------------------------
    def do_GET(self):

        if self.path in ["/", "/index.html"]:
            self.servir_arquivo("index.html", "text/html; charset=utf-8")

        elif self.path == "/style.css":
            self.servir_arquivo("style.css", "text/css; charset=utf-8")

        elif self.path == "/script.js":
            self.servir_arquivo("script.js", "application/javascript; charset=utf-8")

        elif self.path == "/bg.png":
            caminho_bg = os.path.join(os.path.dirname(__file__), 'app_web', 'bg.png')

            if not os.path.exists(caminho_bg):
                caminho_bg = os.path.join(os.path.dirname(__file__), 'bg.png')

            try:
                with open(caminho_bg, 'rb') as arquivo:
                    self.send_response(200)
                    self.send_header("Content-type", "image/png")
                    self.end_headers()
                    self.wfile.write(arquivo.read())
            except FileNotFoundError:
                self.send_error(404)

        elif self.path == "/api/pedidos":
            self.enviar_json_pedidos()

        elif self.path == "/api/tem-usuario":
            self.responder_json({"tem_usuario": db_usuarios.tem_usuarios()})

        elif self.path == "/api/popular-dados-ficticios":
            if not db_leitor.carregar_pedidos():
                db_construtor.salvar_pedidos(db_construtor.importar_pedidos_ficticios())
                db_construtor.salvar_estoque(db_construtor.importar_estoque_ficticio())
                atualizar_estado_global()
            self.responder_json({"sucesso": True})

        else:
            self.send_error(404, "Rota GET não encontrada")

    # ----------------------------------------------------------------------
    # ROTAS POST
    # ----------------------------------------------------------------------
    def do_POST(self):

        if self.path == "/api/cadastrar":
            self.handle_cadastro()

        elif self.path == "/api/login":
            self.handle_login()

        elif self.path == "/api/popular-dados-ficticios":
            self.handle_popular_ficticios()

        elif self.path == "/api/importar-pedidos":
            self.handle_upload("pedidos")

        elif self.path == "/api/importar-estoque":
            self.handle_upload("estoque")

        elif self.path == "/api/marcar-concluido":
            self.handle_status("CONCLUÍDO")

        elif self.path == "/api/reverter":
            self.handle_status("VÁLIDO")

        else:
            self.send_error(404, "Rota POST não encontrada")

    # ----------------------------------------------------------------------
    # HANDLERS DE AÇÃO
    # ----------------------------------------------------------------------
    def handle_cadastro(self):
        tamanho = int(self.headers.get('Content-Length', 0))
        dados = json.loads(self.rfile.read(tamanho).decode('utf-8'))
        sucesso = db_usuarios.cadastrar_usuario(dados['username'], dados['senha'])
        self.responder_json({"sucesso": sucesso}, 200 if sucesso else 400)

    def handle_login(self):
        tamanho = int(self.headers.get('Content-Length', 0))
        dados = json.loads(self.rfile.read(tamanho).decode('utf-8'))

        bloqueado, segundos = seguranca.esta_bloqueado(dados['username'])
        if bloqueado:
            return self.responder_json({"sucesso": False, "erro": f"Bloqueado por {segundos}s"}, 403)

        sucesso = db_usuarios.verificar_credenciais(dados['username'], dados['senha'])
        seguranca.registrar_tentativa(dados['username'], sucesso)

        if sucesso:
            atualizar_estado_global()
        self.responder_json({"sucesso": sucesso}, 200 if sucesso else 401)

    def handle_popular_ficticios(self):
        try:
            if not db_leitor.carregar_pedidos():
                db_construtor.salvar_pedidos(db_construtor.importar_pedidos_ficticios())
                db_construtor.salvar_estoque(db_construtor.importar_estoque_ficticio())
                atualizar_estado_global()
            self.responder_json({"sucesso": True})
        except Exception as erro:
            self.responder_json({"sucesso": False, "erro": str(erro)}, 500)

    def handle_upload(self, tipo):
        content_type = self.headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            return self.responder_json({"sucesso": False, "erro": "Formato inválido"}, 400)

        boundary = content_type.split("boundary=")[1].encode("utf-8")
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)

        parser = email.parser.BytesParser(policy=email.policy.default)
        msg = parser.parsebytes(b"Content-Type: " + content_type.encode('utf-8') + b"\r\n\r\n" + body)

        arquivo_dados = None
        for parte in msg.iter_parts():
            if parte.get_param('name', header='content-disposition') == 'arquivo':
                arquivo_dados = parte.get_payload(decode=True)
                break

        if arquivo_dados:
            fd, temp_path = tempfile.mkstemp(suffix=".xlsx")
            with os.fdopen(fd, 'wb') as arquivo:
                arquivo.write(arquivo_dados)

            try:
                if tipo == "pedidos":
                    dados_lidos = leitor_planilha.ler_planilha_pedidos(temp_path)

                    if not dados_lidos:
                        raise Exception("Nenhum pedido válido encontrado.")
                    db_construtor.salvar_pedidos(dados_lidos)

                else:
                    dados_lidos = leitor_planilha.ler_planilha_estoque(temp_path)

                    if not dados_lidos:
                        raise Exception("Nenhum item válido encontrado.")
                    db_construtor.salvar_estoque(dados_lidos)

                atualizar_estado_global()
                self.responder_json({"sucesso": True})
            except Exception as erro:
                self.responder_json({"sucesso": False, "erro": str(erro)}, 500)
            finally:
                os.remove(temp_path)
        else:
            self.responder_json({"sucesso": False, "erro": "Arquivo não encontrado no formulário"}, 400)

    def handle_status(self, novo_status):
        tamanho = int(self.headers.get('Content-Length', 0))
        dados = json.loads(self.rfile.read(tamanho).decode('utf-8'))
        numero_pedido = dados.get('numero')

        if numero_pedido in ESTADO_VALIDACAO:
            status_atual = ESTADO_VALIDACAO[numero_pedido].status

            if novo_status == "CONCLUÍDO" and status_atual != "CONCLUÍDO":
                ESTADO_VALIDACAO[numero_pedido].status = "CONCLUÍDO"
                ESTADO_VALIDACAO[numero_pedido].motivo = "Finalizado"
                db_construtor.executar_no_banco(
                    ["UPDATE pedidos SET status = ? WHERE numero = ?"],
                    [[("CONCLUÍDO", numero_pedido)]]
                )
            elif novo_status == "VÁLIDO" and status_atual == "CONCLUÍDO":
                ESTADO_VALIDACAO[numero_pedido].status = "VÁLIDO"
                ESTADO_VALIDACAO[numero_pedido].motivo = ""
                db_construtor.executar_no_banco(
                    ["UPDATE pedidos SET status = ? WHERE numero = ?"],
                    [[("PENDENTE", numero_pedido)]]
                )

            self.responder_json({"sucesso": True})
        else:
            self.responder_json({"sucesso": False, "erro": "Pedido não encontrado"}, 404)

    # ----------------------------------------------------------------------
    # RESPOSTAS JSON E ARQUIVOS
    # ----------------------------------------------------------------------
    def enviar_json_pedidos(self):
        pedidos = db_leitor.carregar_pedidos()
        estoque = db_leitor.carregar_estoque()

        resposta = {
            "pedidos": [],
            "resumo": {"total": 0, "em_producao": 0, "retidos": 0, "concluidos": 0}
        }

        for pedido in pedidos:
            resultado = validador_pedidos.validar_pedido(pedido, estoque)

            if pedido.numero in ESTADO_VALIDACAO and ESTADO_VALIDACAO[pedido.numero].status == "CONCLUÍDO":
                resultado = ESTADO_VALIDACAO[pedido.numero]

            resposta["pedidos"].append({
                "numero": pedido.numero,
                "cliente": pedido.cliente,
                "produto": pedido.produto,
                "caminho_arte": pedido.caminho_arte,
                "data_pedido": pedido.data_pedido,
                "prazo": pedido.prazo if pedido.prazo else "—",
                "status": resultado.status,
                "motivo": resultado.motivo
            })

            resposta["resumo"]["total"] += 1

            if resultado.status == "RETIDO":
                resposta["resumo"]["retidos"] += 1

            elif resultado.status == "CONCLUÍDO":
                resposta["resumo"]["concluidos"] += 1

            else:
                resposta["resumo"]["em_producao"] += 1

        self.responder_json(resposta)

    def responder_json(self, dados, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(dados).encode("utf-8"))

    def servir_arquivo(self, nome, content_type):
        caminho = os.path.join(os.path.dirname(__file__), nome)
        if not os.path.exists(caminho):
            caminho = os.path.join(os.path.dirname(__file__), 'app_web', nome)

        try:
            with open(caminho, 'rb') as arquivo:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(arquivo.read())
        except FileNotFoundError:
            self.send_error(404)


# ——————————————————————————————————————————————————————————————————————————
# INICIALIZAÇÃO DO SERVIDOR
# ——————————————————————————————————————————————————————————————————————————
def iniciar_servidor():
    with socketserver.TCPServer(("", PORT), MamoruWebHandler) as httpd:
        print(f"Servidor rodando em http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    iniciar_servidor()