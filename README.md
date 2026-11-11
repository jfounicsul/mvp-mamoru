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

## Versão Web (Deploy)

A versão web do Mamoru foi construída para viabilizar o acesso remoto ao sistema sem depender do ambiente desktop. Ela mantém **toda a lógica de negócio** da versão original (importação, validação, regras de status) e substitui o Tkinter por uma interface SPA (Single Page Application) em HTML, CSS e JavaScript puro.

### Stack Técnica (Web)
- **Backend:** Python 3.12+ com `http.server` nativo (zero dependências).
- **Frontend:** HTML5, CSS3 e JavaScript puro (sem frameworks).
- **Persistência:** SQLite3 (nativo), compartilhando o mesmo banco `mamoru.db`.

### Como Executar (Web)
Dentro da pasta `web_deploy/`, execute:
```bash
python app_web.py
```
O servidor sobe em `http://localhost:8080`. Acesse pelo navegador.

### Funcionalidades implementadas na versão web
- **SPA com roteamento**: Login, Cadastro, Importação e Dashboard em uma única página.
- **Importação real de planilhas `.xlsx`**: upload processado nativamente pelo Python.
- **Dashboard dinâmico**: cartões de resumo, tabela com status, seleção de linha, modal de detalhes (duplo clique).
- **Atualização de status**: concluir/reverter pedidos com fade suave na linha, sem recarregar a tela.
- **Alertas proativos**: avisos de "Vence Hoje" e "Prazos Próximos" com pulso visual (replicando a animação do `animacao.py` via JavaScript).
- **Background com logo**: imagem centralizada com opacidade controlada.
- **Fade-in/out**: transições suaves entre telas e modal.

### Estrutura da Versão Web
```text
web_deploy/
├── app_web.py   # Servidor HTTP nativo e rotas da API
├── index.html   # Documento base da SPA
├── style.css    # Estilos e animações da interface web
├── script.js    # Lógica da SPA (roteamento, fetch, animações)
└── bg.png       # Imagem de fundo das telas de login/cadastro/importação
```

### Atalho de Desenvolvimento (Web)
Na tela de importação, o botão **"Começar sem planilha"** popula o banco com os dados fictícios definidos em `db_construtor.importar_pedidos_ficticios()` e redireciona para o Dashboard.

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange.svg" alt="Status">
</div>