import unittest
import sqlite3
import os
import tempfile
from controladores import entidades
from controladores import validador_pedidos


class TestMamoruMVP(unittest.TestCase):

    # Contador de progresso real: incrementa a cada teste concluído.
    _testes_concluidos = 0
    _total_testes = 8  # 7 unitários + 1 integração

    def setUp(self):
        """Configuração que roda antes de cada teste."""
        print("\n" + "=" * 70)
        print(f"[SETUP] Iniciando: {self._testMethodName}")
        print("=" * 70)

    def tearDown(self):
        # Incrementa o contador e calcula a porcentagem real de progresso.
        TestMamoruMVP._testes_concluidos += 1
        porcentagem = (TestMamoruMVP._testes_concluidos / TestMamoruMVP._total_testes) * 100
        print(f"[TEARDOWN] Finalizando: {self._testMethodName}")
        print(f"[PROGRESSO] {TestMamoruMVP._testes_concluidos}/{TestMamoruMVP._total_testes} testes concluídos ({porcentagem:.1f}%).")
        print("-" * 70)

    # ------------------------------------------------------------------
    # TESTES UNITÁRIOS — REGRAS DE NEGÓCIO (validador_pedidos)
    # ------------------------------------------------------------------

    def test_validador_estoque_suficiente(self):
        """Caso 1: pedido com estoque suficiente deve ser VÁLIDO."""
        print("[ETAPA 1/4] Montando pedido: Camiseta M, qtd 2, arte anexada.")
        pedido = entidades.Pedido(
            "001", "Maria", "Camiseta M", 2,
            prazo="2026-11-15 10:00:00",
            caminho_arte="arte.png"
        )

        print("[ETAPA 2/4] Montando estoque: {'Camiseta M': 10}.")
        estoque = {"Camiseta M": 10}

        print("[ETAPA 3/4] Executando validador_pedidos.validar_pedido().")
        resultado = validador_pedidos.validar_pedido(pedido, estoque)

        print(f"[ETAPA 4/4] Resultado obtido: status='{resultado.status}', motivo='{resultado.motivo}'.")
        self.assertEqual(resultado.status, "VÁLIDO", "Status deveria ser VÁLIDO.")
        self.assertEqual(resultado.motivo, "", "Motivo deveria ser vazio para pedido válido.")
        print("[CONFERÊNCIA] OK: pedido com estoque suficiente foi aprovado (VÁLIDO).")

    def test_validador_estoque_insuficiente(self):
        """Caso 2: pedido com quantidade maior que o estoque deve ser RETIDO."""
        print("[ETAPA 1/4] Montando pedido: Caneca, qtd 5, arte anexada.")
        pedido = entidades.Pedido(
            "002", "João", "Caneca", 5,
            prazo="2026-11-15 10:00:00",
            caminho_arte="arte.png"
        )

        print("[ETAPA 2/4] Montando estoque: {'Caneca': 2} (insuficiente).")
        estoque = {"Caneca": 2}

        print("[ETAPA 3/4] Executando validador_pedidos.validar_pedido().")
        resultado = validador_pedidos.validar_pedido(pedido, estoque)

        print(f"[ETAPA 4/4] Resultado obtido: status='{resultado.status}', motivo='{resultado.motivo}'.")
        self.assertEqual(resultado.status, "RETIDO", "Status deveria ser RETIDO.")
        self.assertIn("Estoque insuficiente", resultado.motivo, "Motivo deveria conter 'Estoque insuficiente'.")
        print("[CONFERÊNCIA] OK: pedido com estoque insuficiente foi retido (RETIDO).")

    def test_validador_pedido_sem_arte(self):
        """Caso 3: pedido sem arte anexada deve ser RETIDO."""
        print("[ETAPA 1/4] Montando pedido: Copo, qtd 1, SEM arte.")
        pedido = entidades.Pedido(
            "003", "Ana", "Copo", 1,
            prazo="2026-11-15 10:00:00",
            caminho_arte=None
        )

        print("[ETAPA 2/4] Montando estoque: {'Copo': 10} (suficiente).")
        estoque = {"Copo": 10}

        print("[ETAPA 3/4] Executando validador_pedidos.validar_pedido().")
        resultado = validador_pedidos.validar_pedido(pedido, estoque)

        print(f"[ETAPA 4/4] Resultado obtido: status='{resultado.status}', motivo='{resultado.motivo}'.")
        self.assertEqual(resultado.status, "RETIDO", "Status deveria ser RETIDO.")
        self.assertIn("Arte não anexada", resultado.motivo, "Motivo deveria conter 'Arte não anexada'.")
        print("[CONFERÊNCIA] OK: pedido sem arte foi retido (RETIDO).")

    def test_validador_prazo_ausente(self):
        """Caso 4 (borda): pedido sem prazo deve ser RETIDO."""
        print("[ETAPA 1/4] Montando pedido: Camiseta P, qtd 1, SEM prazo, arte anexada.")
        pedido = entidades.Pedido(
            "004", "Carlos", "Camiseta P", 1,
            prazo=None,
            caminho_arte="arte.png"
        )

        print("[ETAPA 2/4] Montando estoque: {'Camiseta P': 10}.")
        estoque = {"Camiseta P": 10}

        print("[ETAPA 3/4] Executando validador_pedidos.validar_pedido().")
        resultado = validador_pedidos.validar_pedido(pedido, estoque)

        print(f"[ETAPA 4/4] Resultado obtido: status='{resultado.status}', motivo='{resultado.motivo}'.")
        self.assertEqual(resultado.status, "RETIDO", "Status deveria ser RETIDO.")
        self.assertIn("Prazo não informado", resultado.motivo, "Motivo deveria conter 'Prazo não informado'.")
        print("[CONFERÊNCIA] OK: pedido sem prazo foi retido (RETIDO).")

    def test_validador_quantidade_invalida(self):
        """Caso 5 (borda): pedido com quantidade <= 0 deve ser RETIDO."""
        print("[ETAPA 1/4] Montando pedido: Caneca, qtd 0 (inválida), arte anexada.")
        pedido = entidades.Pedido(
            "005", "Beatriz", "Caneca", 0,
            prazo="2026-11-15 10:00:00",
            caminho_arte="arte.png"
        )

        print("[ETAPA 2/4] Montando estoque: {'Caneca': 10}.")
        estoque = {"Caneca": 10}

        print("[ETAPA 3/4] Executando validador_pedidos.validar_pedido().")
        resultado = validador_pedidos.validar_pedido(pedido, estoque)

        print(f"[ETAPA 4/4] Resultado obtido: status='{resultado.status}', motivo='{resultado.motivo}'.")
        self.assertEqual(resultado.status, "RETIDO", "Status deveria ser RETIDO.")
        self.assertIn("Quantidade inválida", resultado.motivo, "Motivo deveria conter 'Quantidade inválida'.")
        print("[CONFERÊNCIA] OK: pedido com quantidade inválida foi retido (RETIDO).")

    def test_validador_produto_inexistente_no_estoque(self):
        """Caso 6 (borda): produto não cadastrado no estoque deve ser RETIDO."""
        print("[ETAPA 1/4] Montando pedido: Moletom G, qtd 1, arte anexada.")
        pedido = entidades.Pedido(
            "006", "Daniel", "Moletom G", 1,
            prazo="2026-11-15 10:00:00",
            caminho_arte="arte.png"
        )

        print("[ETAPA 2/4] Montando estoque SEM o produto 'Moletom G'.")
        estoque = {"Camiseta M": 10, "Caneca": 5}

        print("[ETAPA 3/4] Executando validador_pedidos.validar_pedido().")
        resultado = validador_pedidos.validar_pedido(pedido, estoque)

        print(f"[ETAPA 4/4] Resultado obtido: status='{resultado.status}', motivo='{resultado.motivo}'.")
        self.assertEqual(resultado.status, "RETIDO", "Status deveria ser RETIDO.")
        self.assertIn("Estoque insuficiente", resultado.motivo, "Produto inexistente deve ser tratado como estoque 0.")
        print("[CONFERÊNCIA] OK: pedido com produto inexistente no estoque foi retido (RETIDO).")

    def test_validador_multiplos_motivos(self):
        """Caso 7 (borda): pedido com múltiplas inconsistências deve acumular motivos."""
        print("[ETAPA 1/4] Montando pedido: Copo, qtd 10, SEM arte, SEM prazo.")
        pedido = entidades.Pedido(
            "007", "Eduarda", "Copo", 10,
            prazo=None,
            caminho_arte=None
        )

        print("[ETAPA 2/4] Montando estoque: {'Copo': 2} (insuficiente).")
        estoque = {"Copo": 2}

        print("[ETAPA 3/4] Executando validador_pedidos.validar_pedido().")
        resultado = validador_pedidos.validar_pedido(pedido, estoque)

        print(f"[ETAPA 4/4] Resultado obtido: status='{resultado.status}', motivo='{resultado.motivo}'.")
        self.assertEqual(resultado.status, "RETIDO", "Status deveria ser RETIDO.")
        self.assertIn("Prazo não informado", resultado.motivo, "Motivo deveria conter 'Prazo não informado'.")
        self.assertIn("Arte não anexada", resultado.motivo, "Motivo deveria conter 'Arte não anexada'.")
        self.assertIn("Estoque insuficiente", resultado.motivo, "Motivo deveria conter 'Estoque insuficiente'.")
        print("[CONFERÊNCIA] OK: pedido com múltiplos motivos foi retido e motivos foram acumulados.")

    # ------------------------------------------------------------------
    # TESTE DE INTEGRAÇÃO — PERSISTÊNCIA REAL COM SQLITE EM ARQUIVO
    # ------------------------------------------------------------------

    def test_integracao_persistencia_arquivo(self):
        """Testa gravação e leitura em um banco SQLite em arquivo temporário."""
        print("[ETAPA 1/5] Criando arquivo temporário para o banco de teste.")
        fd, caminho_temp = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        print("[ETAPA 1/5] Arquivo temporário criado.")

        try:
            print("[ETAPA 2/5] Abrindo conexão com o banco temporário.")
            conexao = sqlite3.connect(caminho_temp)
            conexao.execute(
                "CREATE TABLE estoque (produto TEXT PRIMARY KEY, quantidade_disponivel INTEGER NOT NULL)"
            )
            print("[ETAPA 2/5] Tabela 'estoque' criada.")

            print("[ETAPA 3/5] Inserindo registros: ('Camiseta P', 20), ('Caneca', 5).")
            conexao.executemany(
                "INSERT INTO estoque (produto, quantidade_disponivel) VALUES (?, ?)",
                [("Camiseta P", 20), ("Caneca", 5)]
            )
            conexao.commit()
            print("[ETAPA 3/5] Registros inseridos e commit realizado.")

            print("[ETAPA 4/5] Fechando conexão e reabrindo para testar persistência real.")
            conexao.close()
            conexao = sqlite3.connect(caminho_temp)
            cursor = conexao.execute(
                "SELECT quantidade_disponivel FROM estoque WHERE produto = ?",
                ("Camiseta P",)
            )
            valor = cursor.fetchone()[0]
            print(f"[ETAPA 4/5] Valor lido após reabertura: {valor}")

            print("[ETAPA 5/5] Validando persistência.")
            self.assertEqual(valor, 20, "O valor persistido deveria ser 20.")
            self.assertEqual(
                conexao.execute("SELECT COUNT(*) FROM estoque").fetchone()[0], 2,
                "Deveria haver 2 registros na tabela."
            )
            print("[CONFERÊNCIA] OK: persistência em arquivo funcionou (dados sobreviveram à reabertura).")

            conexao.close()
            print("[CONFERÊNCIA] OK: conexão com o banco fechada.")
        finally:
            print("[LIMPEZA] Removendo arquivo temporário.")
            if os.path.exists(caminho_temp):
                os.remove(caminho_temp)
                print("[LIMPEZA] Arquivo temporário removido com sucesso.")


if __name__ == '__main__':
    unittest.main()