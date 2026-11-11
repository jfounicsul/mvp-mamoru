/* ——— ESTADO GLOBAL ——— */
let pedidoSelecionado = null;
let dadosGlobais = [];

/* ——— MOTOR DE PULSO (FUNÇÃO GLOBAL) ——— */
function iniciarPulso() {
    const corBase = "#F4F6F8";
    const forcaMaxima = 0.3;

    const hexParaRgb = (hex) => {
        hex = hex.replace('#', '');
        return [
            parseInt(hex.substring(0, 2), 16),
            parseInt(hex.substring(2, 4), 16),
            parseInt(hex.substring(4, 6), 16)
        ];
    };

    const rgbParaHex = (rgb) => {
        return '#' + rgb.map(valor => valor.toString(16).padStart(2, '0')).join('');
    };

    const rgbBase = hexParaRgb(corBase);
    let estadoAnimacao = { passo: 0, subindo: true, pausa: 0 };
    const delayPulsoMs = 30;
    const passosPulso = 120;
    const pausaPulso = 15;

    const loopAnimacao = () => {
        const temAvisoHoje = document.getElementById('aviso-hoje');
        const temAvisoProximo = document.querySelector('.aviso-pulso.atencao');

        if (!temAvisoHoje && !temAvisoProximo) return;

        if (estadoAnimacao.pausa > 0) {
            estadoAnimacao.pausa--;
            setTimeout(loopAnimacao, delayPulsoMs);
            return;
        }

        let proporcao = estadoAnimacao.passo / passosPulso;
        proporcao = 0.5 - 0.5 * Math.cos(Math.PI * proporcao);
        const intensidade = proporcao * forcaMaxima;

        if (temAvisoHoje) {
            const rgbPulso = hexParaRgb("#FFB2B2");
            const corAtualRgb = [
                Math.floor(rgbBase[0] + (rgbPulso[0] - rgbBase[0]) * intensidade),
                Math.floor(rgbBase[1] + (rgbPulso[1] - rgbBase[1]) * intensidade),
                Math.floor(rgbBase[2] + (rgbPulso[2] - rgbBase[2]) * intensidade)
            ];
            temAvisoHoje.style.backgroundColor = rgbParaHex(corAtualRgb);
        }

        if (temAvisoProximo) {
            const rgbPulso = hexParaRgb("#FFD3A5");
            const corAtualRgb = [
                Math.floor(rgbBase[0] + (rgbPulso[0] - rgbBase[0]) * intensidade),
                Math.floor(rgbBase[1] + (rgbPulso[1] - rgbBase[1]) * intensidade),
                Math.floor(rgbBase[2] + (rgbPulso[2] - rgbBase[2]) * intensidade)
            ];
            temAvisoProximo.style.backgroundColor = rgbParaHex(corAtualRgb);
        }

        if (estadoAnimacao.subindo) {
            estadoAnimacao.passo++;
            if (estadoAnimacao.passo >= passosPulso) {
                estadoAnimacao.passo = passosPulso;
                estadoAnimacao.subindo = false;
                estadoAnimacao.pausa = pausaPulso;
            }
        } else {
            estadoAnimacao.passo--;
            if (estadoAnimacao.passo <= 0) {
                estadoAnimacao.passo = 0;
                estadoAnimacao.subindo = true;
                estadoAnimacao.pausa = pausaPulso;
            }
        }

        setTimeout(loopAnimacao, delayPulsoMs);
    };

/* ——— ROTEADOR DA SPA ——— */
function navegarPara(tela) {
    const app = document.getElementById('app');
    app.innerHTML = "";

    if (tela === 'login') renderizarLogin(app);
    else if (tela === 'cadastro') renderizarCadastro(app);
    else if (tela === 'importacao') renderizarImportacao(app);
    else if (tela === 'dashboard') carregarDashboard(app);
}

/* ——— TELA DE CADASTRO ——— */
function renderizarCadastro(app) {
    app.innerHTML = `
        <div class="tela-centralizada">
            <div class="container-form">
                <h1>Mamoru</h1>
                <p>Por favor, crie sua conta para realizar o primeiro acesso.</p>
                <label>Usuário</label><input type="text" id="cad-usuario">
                <label>Senha</label><input type="password" id="cad-senha">
                <label>Confirme a senha</label><input type="password" id="cad-senha-confirma">
                <button class="btn btn-primario" onclick="fazerCadastro()" style="width: 100%; margin-top: 12px; padding: 8px;">Cadastrar</button>
            </div>
        </div>
    `;
}

async function fazerCadastro() {
    const usuarioDigitado = document.getElementById('cad-usuario').value;
    const senhaDigitada = document.getElementById('cad-senha').value;
    const confirmacaoSenha = document.getElementById('cad-senha-confirma').value;

    if (!usuarioDigitado || !senhaDigitada) return alert("Preencha os campos.");
    if (senhaDigitada !== confirmacaoSenha) return alert("Senhas não coincidem.");

    const resposta = await fetch('/api/cadastrar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usuarioDigitado, senha: senhaDigitada })
    });

    if (resposta.ok) {
        alert("Conta criada!");
        navegarPara('login');
    } else {
        alert("Erro ao criar conta.");
    }
}

/* ——— TELA DE LOGIN ——— */
function renderizarLogin(app) {
    app.innerHTML = `
        <div class="tela-centralizada">
            <div class="container-form">
                <h1>Mamoru</h1>
                <p>Insira seu usuário e senha para acessar.</p>
                <label>Usuário</label><input type="text" id="login-usuario">
                <label>Senha</label><input type="password" id="login-senha">
                <button class="btn btn-primario" onclick="fazerLogin()" style="width: 100%; margin-top: 12px; padding: 8px;">Entrar</button>
            </div>
        </div>
    `;
}

async function fazerLogin() {
    const usuarioDigitado = document.getElementById('login-usuario').value;
    const senhaDigitada = document.getElementById('login-senha').value;

    if (!usuarioDigitado || !senhaDigitada) return alert("Preencha os campos.");

    const resposta = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usuarioDigitado, senha: senhaDigitada })
    });

    const dados = await resposta.json();

    if (dados.sucesso) {
        const verificacaoPedidos = await fetch('/api/pedidos');
        const pedidos = await verificacaoPedidos.json();

        if (pedidos.resumo.total > 0) navegarPara('dashboard');
        else navegarPara('importacao');
    } else {
        alert(dados.erro || "Credenciais inválidas.");
    }
}

/* ——— TELA DE IMPORTAÇÃO ——— */
function renderizarImportacao(app) {
    app.innerHTML = `
        <div class="tela-centralizada">
            <div class="container-form">
                <h1>Bem-vindo ao Mamoru</h1>
                <p>Importe o arquivo Excel exportado pelo AJXCommerce.</p>
                <div style="margin-bottom: 20px; text-align: left;">
                    <label>Planilha de Pedidos (.xlsx)</label>
                    <input type="file" id="file-pedidos" accept=".xlsx">
                    <button class="btn" onclick="upload('pedidos')" style="width: 100%;">Enviar Pedidos</button>
                </div>
                <div style="margin-bottom: 20px; text-align: left;">
                    <label>Planilha de Estoque (.xlsx)</label>
                    <input type="file" id="file-estoque" accept=".xlsx">
                    <button class="btn" onclick="upload('estoque')" style="width: 100%;">Enviar Estoque</button>
                </div>
                <button class="btn btn-primario" onclick="injetarDadosFicticios()" style="width: 100%; padding: 12px; font-size: 14px;">
                    Começar sem planilha
                    <span style="display: block; font-size: 11px; opacity: 0.8; font-weight: normal;">(teste com dados fictícios)</span>
                </button>
            </div>
        </div>
    `;
}

async function injetarDadosFicticios() {
    try {
        const resposta = await fetch('/api/popular-dados-ficticios', { method: 'POST' });
        const dados = await resposta.json();

        if (dados.sucesso) {
            alert("Dados fictícios injetados com sucesso!");
            navegarPara('dashboard');
        } else {
            alert("Erro ao injetar dados.");
        }
    } catch (erro) {
        alert("Erro de conexão ao injetar dados.");
    }
}

async function upload(tipo) {
    const inputArquivo = document.getElementById(tipo === 'pedidos' ? 'file-pedidos' : 'file-estoque');

    if (!inputArquivo.files.length) return alert("Selecione um arquivo.");

    const formulario = new FormData();
    formulario.append('arquivo', inputArquivo.files[0]);

    const resposta = await fetch(`/api/importar-${tipo}`, { method: 'POST', body: formulario });
    const dados = await resposta.json();

    if (dados.sucesso) alert("Importado com sucesso!");
    else alert("Erro: " + dados.erro);
}

/* ——— TELA DE DASHBOARD ——— */
async function carregarDashboard(app) {
    app.innerHTML = `<div class="tela-centralizada"><h2>Carregando dados...</h2></div>`;

    try {
        const resposta = await fetch('/api/pedidos');
        const dados = await resposta.json();
        dadosGlobais = dados.pedidos;

        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);

        let avisosHtml = '';

        dados.pedidos.forEach(pedido => {
            if (pedido.status !== 'CONCLUÍDO' && pedido.status !== 'RETIDO' && pedido.prazo && pedido.prazo !== '—') {
                try {
                    const dataAlvo = new Date(pedido.prazo.replace(' ', 'T'));
                    dataAlvo.setHours(0, 0, 0, 0);
                    const diferencaDias = Math.ceil((dataAlvo - hoje) / (1000 * 60 * 60 * 24));

                    if (diferencaDias < 0) {
                        avisosHtml += `<div class="aviso aviso-pulso" style="border-color:#DC2626; background-color:#EFEFEF;">
                            <div class="aviso-titulo" style="color:#DC2626;">● ATRASADOS:</div>
                            <div class="aviso-linha" style="color:#DC2626;">• Pedido ${pedido.numero} (${pedido.cliente}) — Atrasado há ${Math.abs(diferencaDias)} dias</div>
                        </div>`;
                    } else if (diferencaDias === 0) {
                        avisosHtml += `<div class="aviso aviso-pulso" id="aviso-hoje" style="border-color:#DC2626;">
                            <div class="aviso-titulo" style="color:#DC2626;">⚠️ VENCE HOJE:</div>
                            <div class="aviso-linha" style="color:#DC2626;">• Pedido ${pedido.numero} (${pedido.cliente}) — Entrega hoje (${pedido.prazo})</div>
                        </div>`;
                    } else if (diferencaDias <= 2) {
                        avisosHtml += `<div class="aviso aviso-pulso atencao">
                            <div class="aviso-titulo">⚠️ Prazos Próximos:</div>
                            <div class="aviso-linha">• Pedido ${pedido.numero} (${pedido.cliente}) — Vence em ${diferencaDias} dias (${pedido.prazo})</div>
                        </div>`;
                    }
                } catch (erro) {}
            }
        });

        if (avisosHtml === '') {
            avisosHtml = `<div class="aviso" style="border-color:#D1D5DB;"><div class="aviso-linha" style="color:#6B7280;">Não há pedidos com prazo urgente.</div></div>`;
        }

        app.innerHTML = `
            <div class="janela">
                <div class="titulo">Gestão de Pedidos</div>
                
                <div class="avisos" id="avisos-area">${avisosHtml}</div>
                
                <div class="cartoes">
                    <div class="cartao"><div class="cartao-titulo">📦 Total</div><div class="cartao-valor">${dados.resumo.total}</div></div>
                    <div class="cartao"><div class="cartao-titulo">⌛ Em Produção</div><div class="cartao-valor status-producao">${dados.resumo.em_producao}</div></div>
                    <div class="cartao"><div class="cartao-titulo">❌ Retidos</div><div class="cartao-valor status-retido">${dados.resumo.retidos}</div></div>
                    <div class="cartao"><div class="cartao-titulo">✔️ Concluídos</div><div class="cartao-valor status-concluido">${dados.resumo.concluidos}</div></div>
                </div>

                <div class="lista-area">
                    <div class="lista-cabecalho">
                        <h2>Visão Geral dos Pedidos:</h2>
                        <div class="botoes">
                            <button class="btn" onclick="navegarPara('importacao')">🔄 Importar</button>
                            <button class="btn" onclick="reverter()">↩ Reverter</button>
                            <button class="btn btn-primario" onclick="marcarConcluido()">✓ Marcar Concluído</button>
                        </div>
                    </div>
                    <div class="tabela-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th style="width:80px;">Status</th>
                                    <th style="width:120px;">Pedido</th>
                                    <th style="width:250px;">Prazo</th>
                                    <th>Observação</th>
                                </tr>
                            </thead>
                            <tbody>
                            ${dados.pedidos.map(pedido => {
                                const icone = pedido.status === 'CONCLUÍDO' ? '✔️' : pedido.status === 'RETIDO' ? '❌' : '⌛';
                                const classeStatus = pedido.status === 'CONCLUÍDO' ? 'status-concluido' : pedido.status === 'RETIDO' ? 'status-retido' : 'status-producao';
                                const observacao = pedido.status === 'CONCLUÍDO' ? 'Concluído' : pedido.status === 'RETIDO' ? pedido.motivo : 'Em produção';
                                
                                return `<tr data-numero="${pedido.numero}" onclick="selecionarLinha('${pedido.numero}', this)" ondblclick="abrirDetalhes('${pedido.numero}')">
                                    <td class="${classeStatus}" style="font-size:16px;">${icone}</td>
                                    <td style="font-weight:bold;">${pedido.numero}</td>
                                    <td class="${classeStatus}">${pedido.prazo}</td>
                                    <td class="${classeStatus}">${observacao}</td>
                                </tr>`;
                            }).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <div id="modal-detalhes" class="modal-overlay" style="display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center;">
                <div class="modal-conteudo" style="background: white; padding: 24px; border-radius: 4px; width: 500px; position: relative; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                    <button onclick="fecharDetalhes()" style="position: absolute; top: 10px; right: 10px; border: none; background: none; font-size: 20px; cursor: pointer;">&times;</button>
                    <h2 style="margin-bottom: 16px;">Detalhes do Pedido</h2>
                    <div id="detalhes-conteudo"></div>
                </div>
            </div>
        `;



    } catch (erro) {
        app.innerHTML = `<div class="tela-centralizada"><p style="color:red;">Erro ao carregar dashboard.</p></div>`;
    }
}

/* ——— SELEÇÃO DE LINHA ——— */
function selecionarLinha(numero, linhaTabela) {
    document.querySelectorAll('tbody tr').forEach(linha => linha.classList.remove('selecionada'));
    linhaTabela.classList.add('selecionada');
    pedidoSelecionado = numero;
}

/* ——— AÇÕES DE STATUS ——— */
async function marcarConcluido() {
    if (!pedidoSelecionado) return alert("Selecione um pedido na tabela.");
    await atualizarStatusPedido(pedidoSelecionado, "CONCLUÍDO");
}

async function reverter() {
    if (!pedidoSelecionado) return alert("Selecione um pedido.");
    await atualizarStatusPedido(pedidoSelecionado, "VÁLIDO");
}

async function atualizarStatusPedido(numero, novoStatus) {
    const endpoint = novoStatus === "CONCLUÍDO" ? '/api/marcar-concluido' : '/api/reverter';

    await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ numero: numero })
    });

    const pedido = dadosGlobais.find(pedido => pedido.numero === numero);

    if (pedido) {
        pedido.status = novoStatus;
        if (novoStatus === "CONCLUÍDO") {
            pedido.motivo = "Finalizado";
        } else {
            pedido.motivo = "";
        }
    }

    const linhaTabela = document.querySelector(`tr[data-numero="${numero}"]`);

    if (linhaTabela) {
        const celulaStatus = linhaTabela.querySelector('td:nth-child(1)');
        const celulaObservacao = linhaTabela.querySelector('td:nth-child(4)');

        const icone = novoStatus === 'CONCLUÍDO' ? '✔️' : novoStatus === 'RETIDO' ? '❌' : '⌛';
        const classeStatus = novoStatus === 'CONCLUÍDO' ? 'status-concluido' : novoStatus === 'RETIDO' ? 'status-retido' : 'status-producao';
        const observacao = novoStatus === 'CONCLUÍDO' ? 'Concluído' : (pedido.motivo || 'Em produção');

        celulaStatus.classList.add('texto-fade-out');
        celulaObservacao.classList.add('texto-fade-out');

        linhaTabela.style.transition = "background-color 0.3s ease-in-out";
        linhaTabela.style.backgroundColor = "#E5EEFF";

        setTimeout(() => {
            celulaStatus.innerHTML = `<span class="${classeStatus}" style="font-size:16px;">${icone}</span>`;
            celulaObservacao.innerHTML = `<span class="${classeStatus}">${observacao}</span>`;

            celulaStatus.classList.remove('texto-fade-out');
            celulaObservacao.classList.remove('texto-fade-out');

            setTimeout(() => { linhaTabela.style.backgroundColor = ""; }, 1000);
        }, 150);
    }

    atualizarResumoCartoes();
    atualizarAvisos();
}

function atualizarResumoCartoes() {
    const total = dadosGlobais.length;
    const emProducao = dadosGlobais.filter(pedido => pedido.status === 'VÁLIDO' || pedido.status === 'EM_PRODUCAO').length;
    const retidos = dadosGlobais.filter(pedido => pedido.status === 'RETIDO').length;
    const concluidos = dadosGlobais.filter(pedido => pedido.status === 'CONCLUÍDO').length;

    document.querySelectorAll('.cartao-valor')[0].innerText = total;
    document.querySelectorAll('.cartao-valor')[1].innerText = emProducao;
    document.querySelectorAll('.cartao-valor')[2].innerText = retidos;
    document.querySelectorAll('.cartao-valor')[3].innerText = concluidos;
}

function atualizarAvisos() {
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    let avisosHtml = '';

    dadosGlobais.forEach(pedido => {
        if (pedido.status !== 'CONCLUÍDO' && pedido.status !== 'RETIDO' && pedido.prazo && pedido.prazo !== '—') {
            try {
                const dataAlvo = new Date(pedido.prazo.replace(' ', 'T'));
                dataAlvo.setHours(0, 0, 0, 0);
                const diferencaDias = Math.ceil((dataAlvo - hoje) / (1000 * 60 * 60 * 24));

                if (diferencaDias < 0) {
                    avisosHtml += `<div class="aviso aviso-pulso" style="border-color:#DC2626; background-color:#EFEFEF;">
                        <div class="aviso-titulo" style="color:#DC2626;">● ATRASADOS:</div>
                        <div class="aviso-linha" style="color:#DC2626;">• Pedido ${pedido.numero} (${pedido.cliente}) — Atrasado há ${Math.abs(diferencaDias)} dias</div>
                    </div>`;
                } else if (diferencaDias === 0) {
                    avisosHtml += `<div class="aviso aviso-pulso" id="aviso-hoje" style="border-color:#DC2626;">
                        <div class="aviso-titulo" style="color:#DC2626;">⚠️ VENCE HOJE:</div>
                        <div class="aviso-linha" style="color:#DC2626;">• Pedido ${pedido.numero} (${pedido.cliente}) — Entrega hoje (${pedido.prazo})</div>
                    </div>`;
                } else if (diferencaDias <= 2) {
                    avisosHtml += `<div class="aviso aviso-pulso atencao">
                        <div class="aviso-titulo">⚠️ Prazos Próximos:</div>
                        <div class="aviso-linha">• Pedido ${pedido.numero} (${pedido.cliente}) — Vence em ${diferencaDias} dias (${pedido.prazo})</div>
                    </div>`;
                }
            } catch (erro) {}
        }
    });

    if (avisosHtml === '') {
        avisosHtml = `<div class="aviso" style="border-color:#D1D5DB;"><div class="aviso-linha" style="color:#6B7280;">Não há pedidos com prazo urgente.</div></div>`;
    }

    const areaAvisos = document.getElementById('avisos-area');
    if (areaAvisos) {
        areaAvisos.innerHTML = avisosHtml;
    }

    if (document.getElementById('aviso-hoje') || document.querySelector('.aviso-pulso.atencao')) {
        iniciarPulso();
    }
}

/* ——— MODAL DE DETALHES ——— */
function abrirDetalhes(numero) {
    const pedido = dadosGlobais.find(pedido => pedido.numero === numero);
    if (!pedido) return;

    document.getElementById('modal-detalhes').querySelector('h2').innerText = 'Pedido Nº';

    let dataFormatada = '—';
    if (pedido.prazo && pedido.prazo !== '—') {
        try {
            const dataObjeto = new Date(pedido.prazo.replace(' ', 'T'));
            dataFormatada = dataObjeto.toLocaleDateString('pt-BR') + ' às ' + dataObjeto.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        } catch (erro) {
            dataFormatada = pedido.prazo;
        }
    }

    const corArte = pedido.caminho_arte ? '#1F2933' : '#DC2626';

    document.getElementById('detalhes-conteudo').innerHTML = `
        <h1 style="color: #2563EB; font-size: 25px; font-weight: bold; margin-bottom: 24px;">${pedido.numero}</h1>
        
        <div style="background: white; padding: 12px; border-radius: 4px; margin-bottom: 6px;">
            <div style="font-size: 10px; font-weight: bold; color: #6B7280; margin-bottom: 4px;">CLIENTE</div>
            <div style="font-size: 16px; font-weight: bold; color: #1F2933;">${pedido.cliente}</div>
        </div>
        
        <div style="display: flex; gap: 6px;">
            <div style="flex: 1; background: white; padding: 12px; border-radius: 4px;">
                <div style="font-size: 10px; font-weight: bold; color: #6B7280; margin-bottom: 4px;">REGISTRO</div>
                <div style="font-size: 14px; color: #1F2933;">${dataFormatada}</div>
            </div>
            <div style="flex: 1; background: white; padding: 12px; border-radius: 4px;">
                <div style="font-size: 10px; font-weight: bold; color: #6B7280; margin-bottom: 4px;">ARTE</div>
                <div style="font-size: 14px; color: ${corArte};">${pedido.caminho_arte || 'Não anexada'}</div>
            </div>
        </div>
    `;

    const modal = document.getElementById('modal-detalhes');
    modal.style.display = 'flex';

    setTimeout(() => {
        modal.classList.add('ativo');
    }, 10);
}

function fecharDetalhes() {
    const modal = document.getElementById('modal-detalhes');
    modal.classList.remove('ativo');

    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

/* ——— INICIALIZAÇÃO DA APLICAÇÃO ——— */
window.onload = async () => {
    try {
        const resposta = await fetch('/api/tem-usuario');
        const dados = await resposta.json();

        if (dados.tem_usuario) navegarPara('login');
        else navegarPara('cadastro');
    } catch (erro) {
        navegarPara('login');
    }
};