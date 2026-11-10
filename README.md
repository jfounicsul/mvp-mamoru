# MVP Mamoru — Sistema de Gestão e Conferência de Pedidos

MVP de software desktop para Windows 11 focado na conferência de pedidos e controle de estoque. Desenvolvido com foco em resiliência, zero dependências externas (stdlib Python) e arquitetura limpa.

## Stack Técnica
- **Linguagem:** Python 3.12+
- **Interface:** Tkinter (nativo)
- **Persistência:** SQLite3 (nativo)
- **Parser de Dados:** `zipfile` + `xml.etree.ElementTree` (leitura nativa de `.xlsx`)
- **Segurança:** `hashlib` (PBKDF2 com salt para senhas)

## Como Executar

1. Clone o repositório.
2. Navegue até a raiz do projeto.
3. Execute a aplicação:
```bash
python main.py
```

**Atalho de Desenvolvimento:**
Para pular a tela de login e popular o banco com dados fictícios automaticamente:
```bash
# Windows (CMD)
set tela=dashboard && python main.py
```

## Arquitetura

O projeto adota uma arquitetura monolítica em camadas com separação estrita de responsabilidades (SoC). O fluxo de dependência é unidirecional.

```text
mvp-mamoru/
├── main.py                     # Ponto de entrada (wiring e atalho de dev)
├── constantes/
│   └── estilo.py               # Tokens visuais, fontes, cores, paddings e dimensões
├── controladores/
│   ├── aplicacao.py            # Estado compartilhado e orquestração de telas
│   ├── bootstrap.py            # Inicialização ordenada (estado → banco → UI)
│   ├── db_construtor.py        # Escrita e criação de tabelas no SQLite
│   ├── db_leitor.py            # Consultas/leitura do SQLite
│   ├── db_usuarios.py          # Autenticação e gestão de usuários
│   ├── entidades.py            # Dataclasses do domínio (Pedido, ItemEstoque, ResultadoValidacao)
│   ├── leitor_planilha.py      # Parser nativo de arquivos .xlsx
│   ├── seguranca.py            # Criptografia (PBKDF2) e anti-brute force
│   └── validador_pedidos.py    # Regras de negócio puras (RF01)
├── dados/
│   └── mamoru.db               # Banco de dados SQLite local (gerado on-the-fly)
└── interface/
    ├── animacao.py             # Motor de animações (hover, fade, pulso)
    ├── fabricas.py             # Fábrica de widgets padronizados
    ├── janela_informacoes.py   # Janela modal com detalhes do pedido
    ├── tela_login.py           # Tela 1 — Login / Primeiro acesso
    ├── tela_importacao.py      # Tela 2 — Importação do arquivo
    └── tela_dashboard.py       # Tela 3 — Resultados e validação
```

### Princípios Adotados
- **Zero Dependências:** Nenhuma biblioteca externa, sem necessidade de `pip install` algum.
- **Separação de Camadas (SoC):** Uma camada não conhece a implementação da outra, apenas invoca suas abstrações.
- **Persistência Isolada:** Leitura e escrita no banco de dados são feitas por módulos dedicados.

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange.svg" alt="Status">
</div>