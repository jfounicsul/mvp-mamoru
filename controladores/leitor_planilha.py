"""
Leitura nativa de planilhas Excel (.xlsx) e OpenDocument (.ods) e dados de teste.
"""

import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from controladores import entidades


# CONFIGURAÇÃO DE COLUNAS (Mapeamento de arquivos de planilha)
# Valores configuráveis para facilitar ajustes no mapeamento das colunas.
class Coluna:
    class Pedidos:
        PEDIDO     = 0  # Coluna A
        CLIENTE    = 1  # Coluna B
        PRODUTO    = 2  # Coluna C
        QUANTIDADE = 3  # Coluna D
        PRAZO      = 4  # Coluna E
        ARTE       = 5  # Coluna F

    class Estoque:
        PRODUTO    = 0  # Coluna A
        QUANTIDADE = 1  # Coluna B


# FUNÇÃO AUXILIAR: CONVERSÃO DE DATA
def converter_prazo(prazo_raw: str):
    """Converte o prazo em formatos comuns de planilha para YYYY-MM-DD HH:MM:SS."""
    if not prazo_raw:
        return None
    for format in ("%d/%m/%Y", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(prazo_raw.strip(), format).strftime("%Y-%m-%d %H:%M:%S")
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


# DISPATCHER: PEDIDOS
def ler_planilha_pedidos(caminho_arquivo: str) -> list[entidades.Pedido]:
    """
    Chama o parser de pedidos (.xlsx).
    """
    return ler_planilha_xlsx(caminho_arquivo)


# DISPATCHER: ESTOQUE
def ler_planilha_estoque(caminho_arquivo: str) -> dict:
    """
    Chama o parser de estoque (.xlsx).
    """
    return ler_estoque_xlsx(caminho_arquivo)


# PARSER 1: .XLSX (Excel)
def ler_planilha_xlsx(caminho_arquivo: str) -> list[entidades.Pedido]:
    """
    Lê um arquivo .xlsx usando apenas zipfile e ElementTree (nativos).
    """
    pedidos = []
    namespace = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    max_col_index = max(filter(None, [
        Coluna.Pedidos.PEDIDO, 
        Coluna.Pedidos.CLIENTE, 
        Coluna.Pedidos.PRODUTO,
        Coluna.Pedidos.QUANTIDADE, 
        Coluna.Pedidos.PRAZO, 
        Coluna.Pedidos.ARTE
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

                # Monta o objeto entidades.Pedido
                try:
                    numero = obter_valor(valores, Coluna.Pedidos.PEDIDO)
                    if numero:
                        pedidos.append(entidades.Pedido(
                            numero=numero,
                            cliente=obter_valor(valores, Coluna.Pedidos.CLIENTE),
                            produto=obter_valor(valores, Coluna.Pedidos.PRODUTO),
                            quantidade=int(float(obter_valor(valores, Coluna.Pedidos.QUANTIDADE, "0"))),
                            prazo=converter_prazo(obter_valor(valores, Coluna.Pedidos.PRAZO)),
                            caminho_arte=obter_valor(valores, Coluna.Pedidos.ARTE) or None
                        ))
                except Exception as erro:
                    print(f"Erro ao processar linha XLSX: {erro}")
                    continue

    except zipfile.BadZipFile:
        print("Erro: O arquivo selecionado não é um arquivo .xlsx válido.")
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")

    return pedidos


# PARSER DE ESTOQUE: .XLSX (Excel)
def ler_estoque_xlsx(caminho_arquivo: str) -> dict:
    """
    Lê uma planilha .xlsx de estoque usando apenas zipfile e ElementTree.
    Retorna {produto: quantidade_disponivel}.
    """
    estoque = {}
    namespace = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    max_col_index = max(filter(None, [
        Coluna.Estoque.PRODUTO, Coluna.Estoque.QUANTIDADE
    ]))

    try:
        with zipfile.ZipFile(caminho_arquivo, 'r') as arquivo_zip:
            # 1. Lê os textos compartilhados
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

                try:
                    produto = obter_valor(valores, Coluna.Estoque.PRODUTO)
                    if produto:
                        quantidade = int(float(obter_valor(valores, Coluna.Estoque.QUANTIDADE, "0")))
                        estoque[produto] = quantidade
                except Exception as erro:
                    print(f"Erro ao processar linha XLSX (estoque): {erro}")
                    continue

    except zipfile.BadZipFile:
        print("Erro: O arquivo de estoque não é um arquivo .xlsx válido.")
    except FileNotFoundError:
        print("Erro: Arquivo de estoque não encontrado.")

    return estoque