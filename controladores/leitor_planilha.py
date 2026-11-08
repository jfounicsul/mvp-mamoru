"""
Leitura nativa de planilhas Excel (.xlsx) e OpenDocument (.ods) e dados de teste.
"""

import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from modelos.pedido import Pedido


# CONFIGURAÇÃO DE COLUNAS (Mapeamento do arquivo xlsx)
# Valores configuráveis para facilitar ajustes no mapeamento das colunas.
class IndiceColuna:
    PEDIDO     = 0  # Coluna A
    CLIENTE    = 1  # Coluna B
    PRODUTO    = 2  # Coluna C
    QUANTIDADE = 3  # Coluna D
    PRAZO      = 4  # Coluna E
    ARTE       = 5  # Coluna F


# FUNÇÃO AUXILIAR: CONVERSÃO DE DATA
def converter_prazo(prazo_raw: str):
    """Converte o prazo em formatos comuns de planilha para YYYY-MM-DD HH:MM:SS."""
    if not prazo_raw:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(prazo_raw.strip(), fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return None


# FUNÇÃO AUXILIAR: EXTRAÇÃO DE VALOR
def obter_valor(valores: list, indice, default: str = "") -> str:
    """Extrai um valor da lista de células já normalizada por índice de coluna."""
    if indice is None or indice >= len(valores):
        return default
    return str(valores[indice]).strip()


# FUNÇÃO AUXILIAR: FORMATAÇÃO DE DATETIME → STRING DO BANCO
def formatar_data_hora(date_time: datetime) -> str:
    """Formata um datetime no padrão YYYY-MM-DD HH:MM:SS usado em todo o domínio."""
    return date_time.strftime("%Y-%m-%d %H:%M:%S")


# DISPATCHER: ESCOLHE O PARSER CORRETO
def ler_planilha(caminho_arquivo: str) -> list[Pedido]:
    """
    Função única que decide qual parser usar com base na extensão do arquivo.
    """
    if caminho_arquivo.lower().endswith('.ods'):
        return ler_planilha_ods(caminho_arquivo)
    return ler_planilha_xlsx(caminho_arquivo)


# PARSER 1: .XLSX (Excel)
def ler_planilha_xlsx(caminho_arquivo: str) -> list[Pedido]:
    """
    Lê um arquivo .xlsx usando apenas zipfile e ElementTree (nativos).
    """
    pedidos = []
    namespace = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    max_col_index = max(filter(None, [
        IndiceColuna.PEDIDO, IndiceColuna.CLIENTE, IndiceColuna.PRODUTO,
        IndiceColuna.QUANTIDADE, IndiceColuna.PRAZO, IndiceColuna.ARTE
    ]))

    try:
        with zipfile.ZipFile(caminho_arquivo, 'r') as arquivo_zip:
            # 1. Lê os textos compartilhados (sharedStrings)
            textos = []
            try:
                xml_strings = arquivo_zip.read('xl/sharedStrings.xml')
                raiz_strings = ET.fromstring(xml_strings)
                for si in raiz_strings.findall('ns:si', namespace):
                    texto_completo = "".join(t.text or "" for t in si.findall('ns:t', namespace))
                    textos.append(texto_completo)
            except KeyError:
                pass

            # 2. Lê a primeira planilha
            xml_sheet = arquivo_zip.read('xl/worksheets/sheet1.xml')
            raiz_sheet = ET.fromstring(xml_sheet)
            rows = raiz_sheet.findall('ns:sheetData/ns:row', namespace)

            # 3. Itera sobre as linhas (pula o cabeçalho)
            for row in rows[1:]:
                valores = [""] * (max_col_index + 1)

                for coluna in row.findall('ns:c', namespace):
                    ref = coluna.get('r', '')
                    col_letra = ''.join(filter(str.isalpha, ref))
                    if not col_letra:
                        continue

                    # Converte letra da coluna para índice (A=0, B=1, ...)
                    col_index = 0
                    for char in col_letra:
                        col_index = col_index * 26 + (ord(char) - ord('A') + 1)
                    col_index -= 1

                    if col_index > max_col_index:
                        continue

                    valor_elem = coluna.find('ns:v', namespace)
                    if valor_elem is not None and valor_elem.text is not None:
                        valor_texto = valor_elem.text
                        if coluna.get('t') == 's':
                            valor_texto = textos[int(valor_texto)]
                        valores[col_index] = valor_texto

                # Monta o objeto Pedido
                try:
                    numero = obter_valor(valores, IndiceColuna.PEDIDO)
                    if numero:
                        pedidos.append(Pedido(
                            numero=numero,
                            cliente=obter_valor(valores, IndiceColuna.CLIENTE),
                            produto=obter_valor(valores, IndiceColuna.PRODUTO),
                            quantidade=int(float(obter_valor(valores, IndiceColuna.QUANTIDADE, "0"))),
                            prazo=converter_prazo(obter_valor(valores, IndiceColuna.PRAZO)),
                            caminho_arte=obter_valor(valores, IndiceColuna.ARTE) or None
                        ))
                except Exception as erro:
                    print(f"Erro ao processar linha XLSX: {erro}")
                    continue

    except zipfile.BadZipFile:
        print("Erro: O arquivo selecionado não é um .xlsx válido.")
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")

    return pedidos


# PARSER 2: .ODS (OpenDocument Spreadsheet)
def ler_planilha_ods(caminho_arquivo: str) -> list[Pedido]:
    """
    Lê um arquivo .ods usando apenas zipfile e ElementTree (nativos).
    """
    pedidos = []
    namespaces = {
        'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
    }

    try:
        with zipfile.ZipFile(caminho_arquivo, 'r') as arquivo_zip:
            # O .ods tem os dados no content.xml
            xml_content = arquivo_zip.read('content.xml')
            raiz = ET.fromstring(xml_content)

            # Acha a primeira tabela
            tabela = raiz.find('.//table:table', namespaces)
            if tabela is None:
                return pedidos

            linhas = tabela.findall('table:table-row', namespaces)

            # Pula o cabeçalho
            for linha in linhas[1:]:
                valores = [""] * 6
                colunas = linha.findall('table:table-cell', namespaces)
                
                col_index = 0
                for celula in colunas:
                    repeticao = int(celula.get(f"{{{namespaces['table']}}}number-columns-repeated", 1))
                    texto = "".join(celula.itertext()).strip()
                    
                    for _ in range(repeticao):
                        if col_index < len(valores):
                            valores[col_index] = texto
                        col_index += 1

                try:
                    numero = valores[IndiceColuna.PEDIDO].strip()
                    if numero:
                        pedidos.append(Pedido(
                            numero=numero,
                            cliente=valores[IndiceColuna.CLIENTE].strip(),
                            produto=valores[IndiceColuna.PRODUTO].strip(),
                            quantidade=int(float(valores[IndiceColuna.QUANTIDADE].strip() or "0")),
                            prazo=converter_prazo(valores[IndiceColuna.PRAZO]),
                            caminho_arte=valores[IndiceColuna.ARTE].strip() or None
                        ))
                except Exception as erro:
                    print(f"Erro ao processar linha ODS: {erro}")
                    continue

    except zipfile.BadZipFile:
        print("Erro: O arquivo selecionado não é um .ods válido.")
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")

    return pedidos


# DADOS FICTÍCIOS (FALLBACK PARA TESTES RÁPIDOS)
def importar_pedidos_ficticios() -> list[Pedido]:
    """Mantido para testes sem arquivo (fallback)."""
    hoje = datetime(2026, 11, 8, 10, 0, 0)

    return [
        Pedido(
            "001",
            "Maria Silva",
            "Camiseta M",
            1,
            formatar_data_hora(hoje),
            formatar_data_hora(hoje + timedelta(days=7)),
            "arte_maria.png"
        ),
        Pedido(
            "002",
            "João Souza",
            "Caneca",
            2,
            formatar_data_hora(hoje),
            formatar_data_hora(hoje + timedelta(days=5)),
            None
        ),
        Pedido(
            "003",
            "Ana Aparecida",
            "Camiseta P",
            1,
            formatar_data_hora(hoje),
            formatar_data_hora(hoje.replace(hour=18)),
            "arte_ana.png"
        ),
        Pedido(
            "004",
            "Claudio Conceição",
            "Camiseta M",
            2,
            formatar_data_hora(hoje),
            formatar_data_hora(hoje + timedelta(days=2)),
            "arte_claudio.png"
        ),
        Pedido(
            "005",
            "Pedro Perez",
            "Copo",
            5,
            formatar_data_hora(hoje),
            formatar_data_hora(hoje + timedelta(days=10)),
            "arte_pedro.png"
        ),
    ]