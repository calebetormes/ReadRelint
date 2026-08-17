/**
 * View para Gerenciamento do Motor de Monitoramento de Pastas & IA.
 * Organizada em 2 Sub-Abas principais:
 *   - Sub-Aba 1: Painel de Controle + Console de Logs em Tempo Real (no lado direito)
 *   - Sub-Aba 2: Relatório de Leitura dos RELINTs dividido em 2 Colunas (20% Gráficos Circulares / 80% Lista com Scroll)
 */

let monitoringEventSource = null;
let _lastProcessedCount = -1;
let _allWebReports = [];

function renderMonitoringView(container) {
  container.innerHTML = `
    <!-- Header com Seletor de Sub-Abas -->
    <div class="view-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px;">
      <div>
        <h1 class="view-title">Motor de Monitoramento & IA</h1>
        <p class="view-subtitle">Painel de controle de leitura em tempo real e visualização de relatórios.</p>
      </div>

      <!-- Seletor de Sub-Abas -->
      <div style="display: flex; gap: 8px; background: #121212; padding: 4px; border-radius: 8px; border: 1px solid var(--hairline-strong);">
        <button id="subtab-btn-panel" class="btn-resend" onclick="switchMonitoringSubTab('panel')" style="background: var(--surface-elevated); color: #ffffff; border-color: rgba(255,255,255,0.14);">
          <i data-lucide="cpu"></i> Painel & Console Logs
        </button>
        <button id="subtab-btn-reports" class="btn-resend" onclick="switchMonitoringSubTab('reports')" style="background: transparent; color: var(--ash); border-color: transparent;">
          <i data-lucide="file-text"></i> Relatório de Leitura
          <span id="web-subtab-badge" style="background: rgba(16,185,129,0.15); color: #10b981; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-left: 4px;">0</span>
        </button>
      </div>
    </div>

    <!-- Style local para animações e barras de rolagem customizadas -->
    <style>
      @keyframes progressGlow {
        0% { opacity: 0.75; filter: brightness(0.9); }
        50% { opacity: 1; filter: brightness(1.25); }
        100% { opacity: 0.75; filter: brightness(0.9); }
      }
      .bar-active { animation: progressGlow 1.2s infinite ease-in-out; }

      @keyframes spinSmooth {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      .spin-icon {
        display: inline-block;
        animation: spinSmooth 1.2s linear infinite;
      }

      @keyframes pulseGlowDot {
        0% { transform: scale(0.9); opacity: 0.5; box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
        70% { transform: scale(1.15); opacity: 1; box-shadow: 0 0 0 7px rgba(52, 211, 153, 0); }
        100% { transform: scale(0.9); opacity: 0.5; box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
      }
      .pulse-dot-reading {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #34d399;
        display: inline-block;
        animation: pulseGlowDot 1.4s infinite ease-in-out;
      }
      .pulse-dot-idle {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #64748b;
        display: inline-block;
      }

      pre#web-log-console::-webkit-scrollbar {
        width: 6px;
      }
      pre#web-log-console::-webkit-scrollbar-track {
        background: #09090b;
        border-radius: 4px;
      }
      pre#web-log-console::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
      }
      pre#web-log-console::-webkit-scrollbar-thumb:hover {
        background: rgba(56, 189, 248, 0.5);
      }

      #web-reports-list::-webkit-scrollbar {
        width: 6px;
      }
      #web-reports-list::-webkit-scrollbar-track {
        background: #121212;
        border-radius: 4px;
      }
      #web-reports-list::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
      }
      #web-reports-list::-webkit-scrollbar-thumb:hover {
        background: rgba(16, 185, 129, 0.5);
      }
    </style>

    <!-- ===================================================================== -->
    <!-- SUB-ABA 1: PAINEL DE CONTROLE + CONSOLE DE LOGS (Lado a Lado)        -->
    <!-- ===================================================================== -->
    <div id="subtab-panel-container" style="display: flex; gap: 20px; align-items: stretch; flex-wrap: wrap;">
      
      <!-- COLUNA 1: CONTROLES E MÉTRICAS (52% de largura) -->
      <div style="flex: 1 1 50%; min-width: 320px;">
        
        <!-- 1. Card: Diretório de Monitoramento -->
        <div class="card" style="margin-bottom: 16px;">
          <div style="font-size: 13px; font-weight: 600; color: var(--ash); margin-bottom: 10px;">
            📁 Diretório de Monitoramento dos RELINTs (Servidor Local)
          </div>
          <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
            <input type="text" id="web-dir-input" class="form-control" placeholder="Selecione ou cole o caminho da pasta local no servidor (ex: D:\\RELINTs)..." style="flex: 1; min-width: 200px;" />
            <button class="btn-resend btn-resend-emerald" onclick="browseWebFolder()">
              <i data-lucide="folder-search"></i> Procurar Pasta no PC
            </button>
            <button class="btn-resend" onclick="setWebMonitoringPath()">
              <i data-lucide="search"></i> Definir & Inspecionar
            </button>
          </div>
        </div>

        <!-- 2. Card: Status do Monitoramento com Linha Dedicada e Loading Dinâmico -->
        <div class="card" style="margin-bottom: 16px; display: flex; flex-direction: column; gap: 10px; padding: 16px 20px;">
          <div id="web-status-badge" style="font-size: 14px; font-weight: 700; color: #f59e0b; display: flex; align-items: center; gap: 8px;">
            Status: ⏸️ Monitoramento Pausado
          </div>
          
          <div id="web-current-reading-container" style="display: flex; align-items: center; gap: 10px; font-size: 12.5px; font-weight: 600; padding-top: 8px; border-top: 1px solid rgba(255, 255, 255, 0.07); color: #94a3b8;">
            <div id="web-reading-icon-wrapper" style="display: flex; align-items: center; justify-content: center; width: 18px; height: 18px;">
              <span class="pulse-dot-idle"></span>
            </div>
            <span id="web-current-reading-text" style="word-break: break-all;">Aguardando início do monitoramento...</span>
          </div>
        </div>

        <!-- Grid de 2 Cards Individuais para os Medidores Circulares Ampliados -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 16px;">
          
          <!-- CARD 1: Arquivos Lidos na Pasta (Banco / Histórico) -->
          <div class="card" style="display: flex; flex-direction: column; align-items: center; text-align: center; padding: 20px 16px;">
            <div style="font-size: 13px; font-weight: 700; color: #10b981; margin-bottom: 14px; display: flex; align-items: center; gap: 6px;">
              <i data-lucide="database"></i> Arquivos Lidos na Pasta
            </div>
            
            <div style="position: relative; width: 130px; height: 130px;">
              <svg width="130" height="130" viewBox="0 0 140 140" style="transform: rotate(-90deg);">
                <circle cx="70" cy="70" r="55" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="10" />
                <circle id="web-circle1-ring" cx="70" cy="70" r="55" fill="none" stroke="url(#emerald-grad)" stroke-width="10" stroke-dasharray="345.57" stroke-dashoffset="345.57" stroke-linecap="round" style="transition: stroke-dashoffset 0.5s ease;" />
                <defs>
                  <linearGradient id="emerald-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#059669" />
                    <stop offset="100%" stop-color="#10b981" />
                  </linearGradient>
                </defs>
              </svg>
              <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <span id="web-prog1-val" style="font-size: 20px; font-weight: 800; color: #10b981;">0.0%</span>
                <span style="font-size: 10px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.5px;">PASTA</span>
              </div>
            </div>

            <div id="web-prog1-sub" style="font-size: 12px; color: #94a3b8; margin-top: 12px; font-weight: 600;">
              0 / 0 arquivos lidos
            </div>
          </div>

          <!-- CARD 2: Progresso da Leitura Atual da Sessão -->
          <div class="card" style="display: flex; flex-direction: column; align-items: center; text-align: center; padding: 20px 16px;">
            <div style="font-size: 13px; font-weight: 700; color: #c084fc; margin-bottom: 14px; display: flex; align-items: center; gap: 6px;">
              <i data-lucide="zap"></i> Leitura Atual da Sessão
            </div>

            <div style="position: relative; width: 130px; height: 130px;">
              <svg width="130" height="130" viewBox="0 0 140 140" style="transform: rotate(-90deg);">
                <circle cx="70" cy="70" r="55" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="10" />
                <circle id="web-circle2-ring" cx="70" cy="70" r="55" fill="none" stroke="url(#purple-grad)" stroke-width="10" stroke-dasharray="345.57" stroke-dashoffset="345.57" stroke-linecap="round" style="transition: stroke-dashoffset 0.5s ease;" />
                <defs>
                  <linearGradient id="purple-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#7c3aed" />
                    <stop offset="100%" stop-color="#c084fc" />
                  </linearGradient>
                </defs>
              </svg>
              <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <span id="web-prog2-val" style="font-size: 20px; font-weight: 800; color: #c084fc;">0.0%</span>
                <span style="font-size: 10px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.5px;">SESSÃO</span>
              </div>
            </div>

            <div id="web-prog2-sub" style="font-size: 12px; color: #94a3b8; margin-top: 12px; font-weight: 600;">
              0 / 0 novos lidos
            </div>
          </div>

        </div>

        <!-- 3. Card: Painel de Ações (Botões Principais) -->
        <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
          <button id="web-btn-toggle-monitor" class="btn-resend btn-resend-emerald" onclick="toggleWebMonitoring()">
            <i data-lucide="play"></i> Iniciar Monitoramento
          </button>

          <button id="web-btn-reset-all" class="btn-resend btn-resend-amber" onclick="confirmWebResetAll()">
            <i data-lucide="rotate-ccw"></i> Resetar & Re-ler Todos os RELINTs
          </button>
        </div>

        <!-- 4. Card em Destaque: Inteligência Artificial (Ollama Local) -->
        <div class="card" style="border: 1px solid rgba(16, 185, 129, 0.4); background: #18181b; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="font-size: 14px; font-weight: 700; color: #34d399;">⚡ INTELIGÊNCIA ARTIFICIAL (Ollama Local)</div>
            <div id="web-ai-status-lbl" style="font-size: 12px; color: #10b981; margin-top: 4px;">
              Modo Ativo: 🟢 IA Local (Ollama) Habilitado
            </div>
          </div>
          <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; cursor: pointer;">
            <input type="checkbox" id="web-switch-llm" onchange="toggleWebLLM(this.checked)" checked style="width: 18px; height: 18px; accent-color: #10b981;" />
            Usar Processamento por IA
          </label>
        </div>

      </div>

      <!-- COLUNA 2: CONSOLE DE LOGS DO SISTEMA EM TEMPO REAL (48% de largura / Puxado para o lado direito) -->
      <div style="flex: 1 1 45%; min-width: 320px; display: flex; flex-direction: column;">
        <div class="card" style="display: flex; flex-direction: column; max-height: calc(100vh - 180px); overflow: hidden;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-shrink: 0;">
            <span style="font-size: 14px; font-weight: 700; color: var(--head); display: flex; align-items: center; gap: 8px;">
              <i data-lucide="terminal" style="color: #38bdf8;"></i> Console de Logs do Sistema em Tempo Real
            </span>
            <button class="btn-resend btn-resend-sm" onclick="clearWebLogs()">
              <i data-lucide="trash-2"></i> Limpar Console
            </button>
          </div>
          <pre id="web-log-console" style="background: #09090b; color: #38bdf8; font-family: 'Consolas', 'JetBrains Mono', monospace; font-size: 12px; padding: 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); overflow-y: auto; white-space: pre-wrap; margin: 0; height: 380px; max-height: calc(100vh - 240px); line-height: 1.5;"></pre>
        </div>
      </div>

    </div>

    <!-- ===================================================================== -->
    <!-- SUB-ABA 2: RELATÓRIO DE LEITURA DOS RELINTs (2 Colunas 20% / 80%)      -->
    <!-- ===================================================================== -->
    <div id="subtab-reports-container" style="display: none;">
      <div style="display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap;">
        
        <!-- COLUNA 1: 3 GRÁFICOS CIRCULARES SVG (20% da largura) -->
        <div style="flex: 1 1 18%; min-width: 200px; display: flex; flex-direction: column; gap: 14px;">
          
          <!-- Círculo 1: Total na Pasta -->
          <div class="card" style="display: flex; flex-direction: column; align-items: center; text-align: center; padding: 16px 12px;">
            <div style="font-size: 12px; font-weight: 700; color: #c084fc; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
              <i data-lucide="folder"></i> Total na Pasta
            </div>
            <div style="position: relative; width: 110px; height: 110px;">
              <svg width="110" height="110" viewBox="0 0 140 140" style="transform: rotate(-90deg);">
                <circle cx="70" cy="70" r="55" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="10" />
                <circle id="rep-circle-total-ring" cx="70" cy="70" r="55" fill="none" stroke="url(#purple-grad)" stroke-width="10" stroke-dasharray="345.57" stroke-dashoffset="0" stroke-linecap="round" />
              </svg>
              <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <span id="web-card-total" style="font-size: 24px; font-weight: 800; color: #c084fc;">0</span>
                <span style="font-size: 9px; text-transform: uppercase; color: #64748b; font-weight: 700;">ARQUIVOS</span>
              </div>
            </div>
          </div>

          <!-- Círculo 2: Lidos com IA (Ollama) -->
          <div class="card" style="display: flex; flex-direction: column; align-items: center; text-align: center; padding: 16px 12px;">
            <div style="font-size: 12px; font-weight: 700; color: #10b981; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
              <i data-lucide="bot"></i> Lidos com IA
            </div>
            <div style="position: relative; width: 110px; height: 110px;">
              <svg width="110" height="110" viewBox="0 0 140 140" style="transform: rotate(-90deg);">
                <circle cx="70" cy="70" r="55" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="10" />
                <circle id="rep-circle-llm-ring" cx="70" cy="70" r="55" fill="none" stroke="url(#emerald-grad)" stroke-width="10" stroke-dasharray="345.57" stroke-dashoffset="345.57" stroke-linecap="round" style="transition: stroke-dashoffset 0.5s ease;" />
              </svg>
              <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <span id="web-card-llm" style="font-size: 24px; font-weight: 800; color: #10b981;">0</span>
                <span id="web-card-llm-pct" style="font-size: 9px; text-transform: uppercase; color: #64748b; font-weight: 700;">0%</span>
              </div>
            </div>
          </div>

          <!-- Círculo 3: Lidos com Regex (Sem IA) -->
          <div class="card" style="display: flex; flex-direction: column; align-items: center; text-align: center; padding: 16px 12px;">
            <div style="font-size: 12px; font-weight: 700; color: #f59e0b; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
              <i data-lucide="file-code"></i> Lidos com Regex
            </div>
            <div style="position: relative; width: 110px; height: 110px;">
              <svg width="110" height="110" viewBox="0 0 140 140" style="transform: rotate(-90deg);">
                <circle cx="70" cy="70" r="55" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="10" />
                <circle id="rep-circle-regex-ring" cx="70" cy="70" r="55" fill="none" stroke="#f59e0b" stroke-width="10" stroke-dasharray="345.57" stroke-dashoffset="345.57" stroke-linecap="round" style="transition: stroke-dashoffset 0.5s ease;" />
              </svg>
              <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <span id="web-card-regex" style="font-size: 24px; font-weight: 800; color: #f59e0b;">0</span>
                <span id="web-card-regex-pct" style="font-size: 9px; text-transform: uppercase; color: #64748b; font-weight: 700;">0%</span>
              </div>
            </div>
          </div>

        </div>

        <!-- COLUNA 2: LISTA DE RELINTs COM ALTURA DA TELA E SCROLLBAR (80% da largura) -->
        <div style="flex: 4 1 78%; min-width: 320px;">
          <div class="card" style="display: flex; flex-direction: column; height: calc(100vh - 200px); max-height: calc(100vh - 200px);">
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 12px; flex-shrink: 0;">
              <div style="font-size: 16px; font-weight: 700; color: var(--head); display: flex; align-items: center; gap: 8px;">
                <i data-lucide="file-text" style="color: #10b981;"></i> Relatório Geral de Leitura dos RELINTs
              </div>
              <button class="btn-resend btn-resend-sm" onclick="fetchReportsList()">
                <i data-lucide="refresh-cw"></i> Atualizar Lista
              </button>
            </div>

            <!-- Filtro e Busca em Tempo Real (Fixo no topo da coluna) -->
            <div style="display: flex; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; flex-shrink: 0;">
              <div style="flex: 1; min-width: 240px; position: relative;">
                <input type="text" id="web-report-search" class="form-control" placeholder="Pesquisar por nome do PDF, assunto, resumo ou pessoa..." oninput="filterWebReports()" style="width: 100%; padding-left: 36px;" />
                <i data-lucide="search" style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: var(--ash);"></i>
              </div>

              <select id="web-report-filter-method" class="form-control" onchange="filterWebReports()" style="width: 200px;">
                <option value="all">Todos os Métodos</option>
                <option value="llm">🟢 Apenas IA Local (Ollama)</option>
                <option value="regex">⚡ Apenas Regex (Sem IA)</option>
              </select>
            </div>

            <!-- Lista de Cards dos RELINTs com Barra de Rolagem em Altura da Tela -->
            <div id="web-reports-list" style="flex: 1; overflow-y: auto; padding-right: 6px;">
              <div style="text-align: center; color: var(--ash); font-style: italic; padding: 20px;">
                Carregando relatórios de leitura...
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  `;

  // Carrega status inicial e inicia SSE real-time
  fetchMonitoringStatus();
  initMonitoringSSE();
  if (window.lucide) window.lucide.createIcons();
}

function switchMonitoringSubTab(tabName) {
  const panelContainer = document.getElementById('subtab-panel-container');
  const reportsContainer = document.getElementById('subtab-reports-container');
  const btnPanel = document.getElementById('subtab-btn-panel');
  const btnReports = document.getElementById('subtab-btn-reports');

  if (tabName === 'panel') {
    if (panelContainer) panelContainer.style.display = 'flex';
    if (reportsContainer) reportsContainer.style.display = 'none';
    if (btnPanel) {
      btnPanel.style.background = 'var(--surface-elevated)';
      btnPanel.style.borderColor = 'rgba(255,255,255,0.14)';
      btnPanel.style.color = '#ffffff';
    }
    if (btnReports) {
      btnReports.style.background = 'transparent';
      btnReports.style.borderColor = 'transparent';
      btnReports.style.color = 'var(--ash)';
    }
  } else {
    if (panelContainer) panelContainer.style.display = 'none';
    if (reportsContainer) reportsContainer.style.display = 'block';
    if (btnPanel) {
      btnPanel.style.background = 'transparent';
      btnPanel.style.borderColor = 'transparent';
      btnPanel.style.color = 'var(--ash)';
    }
    if (btnReports) {
      btnReports.style.background = 'var(--surface-elevated)';
      btnReports.style.borderColor = 'rgba(255,255,255,0.14)';
      btnReports.style.color = '#ffffff';
    }
    fetchReportsList();
  }
  if (window.lucide) window.lucide.createIcons();
}

async function fetchMonitoringStatus() {
  try {
    const res = await fetch('/api/v1/monitoring/status');
    if (!res.ok) return;
    const data = await res.json();

    const input = document.getElementById('web-dir-input');
    if (input && data.monitoring_path) {
      input.value = data.monitoring_path;
    }

    updateMonitoringUIState(data);
    fetchReportsList();
  } catch (err) {
    console.error('Erro ao buscar status de monitoramento:', err);
  }
}

let _isWebMonitoringActive = false;

function updateMonitoringUIState(data) {
  _isWebMonitoringActive = !!data.is_monitoring;

  const input = document.getElementById('web-dir-input');
  if (input && data.monitoring_path && input.value !== data.monitoring_path) {
    input.value = data.monitoring_path;
  }

  const statusBadge = document.getElementById('web-status-badge');
  const btnToggle = document.getElementById('web-btn-toggle-monitor');
  const readingIconWrapper = document.getElementById('web-reading-icon-wrapper');
  const currentReadingText = document.getElementById('web-current-reading-text');
  const switchLLM = document.getElementById('web-switch-llm');
  const aiStatusLbl = document.getElementById('web-ai-status-lbl');

  if (statusBadge && btnToggle) {
    if (data.is_monitoring) {
      statusBadge.innerHTML = 'Status: 🟢 Monitoramento Ativo';
      statusBadge.style.color = '#4ade80';
      btnToggle.className = 'btn-resend btn-resend-danger';
      btnToggle.innerHTML = '<i data-lucide="pause"></i> Pausar Monitoramento';
    } else {
      statusBadge.innerHTML = data.monitoring_path ? 'Status: ⏸️ Monitoramento Pausado' : 'Status: Parado - Aguardando seleção de diretório';
      statusBadge.style.color = '#f59e0b';
      btnToggle.className = 'btn-resend btn-resend-emerald';
      btnToggle.innerHTML = '<i data-lucide="play"></i> Iniciar Monitoramento';
    }
    if (window.lucide) window.lucide.createIcons();
  }

  if (currentReadingText && readingIconWrapper) {
    if (data.is_monitoring) {
      if (data.current_filename) {
        // Ativamente processando um arquivo PDF (Spinner animado ativo)
        readingIconWrapper.innerHTML = `<i data-lucide="loader-2" class="spin-icon" style="color: #34d399; width: 16px; height: 16px;"></i>`;
        currentReadingText.innerHTML = `<span style="color: #64748b; font-weight: 600;">Lendo agora:</span> <span style="color: #34d399; font-weight: 700;">${data.current_filename}</span>`;
      } else {
        // Monitoramento ativo, aguardando novos PDFs na pasta
        readingIconWrapper.innerHTML = `<span class="pulse-dot-reading"></span>`;
        currentReadingText.innerHTML = `<span style="color: #94a3b8;">Vigilância de pasta ativa — Aguardando novos arquivos PDF...</span>`;
      }
    } else {
      // Monitoramento pausado / parado
      readingIconWrapper.innerHTML = `<span class="pulse-dot-idle"></span>`;
      currentReadingText.innerHTML = `<span style="color: #64748b;">Nenhum arquivo em leitura (Monitoramento Pausado)</span>`;
    }
    if (window.lucide) window.lucide.createIcons();
  }

  // Atualiza switch de IA
  if (switchLLM && aiStatusLbl) {
    switchLLM.checked = data.use_llm;
    if (data.use_llm && data.ollama_online) {
      aiStatusLbl.innerText = 'Modo Ativo: 🟢 IA Local (Ollama) Habilitado';
      aiStatusLbl.style.color = '#10b981';
    } else {
      aiStatusLbl.innerText = 'Modo Ativo: ⚡ Processamento Ultra-Rápido (Regex / Sem IA)';
      aiStatusLbl.style.color = '#f59e0b';
    }
  }

  // Círculo 1: Lidos na pasta (Painel 1)
  const total = data.total_files_in_folder || 0;
  const readCnt = data.read_files_in_folder || 0;
  const prog1 = total > 0 ? Math.min(100, Math.max(0, (readCnt / total) * 100)) : 0;
  
  const circle1Ring = document.getElementById('web-circle1-ring');
  const prog1Val = document.getElementById('web-prog1-val');
  const prog1Sub = document.getElementById('web-prog1-sub');

  if (circle1Ring && prog1Val) {
    const C = 345.57;
    const offset = C - (prog1 / 100) * C;
    circle1Ring.style.strokeDashoffset = `${offset}`;
    prog1Val.innerText = `${prog1.toFixed(1)}%`;
    if (prog1Sub) prog1Sub.innerText = `${readCnt} / ${total} arquivos lidos`;
    
    if (data.is_monitoring && data.current_filename) {
      circle1Ring.classList.add('bar-active');
    } else {
      circle1Ring.classList.remove('bar-active');
    }
  }

  // Círculo 2: Leitura atual da sessão (Painel 1)
  const discovered = data.total_discovered || 0;
  const processed = data.processed_count || 0;
  const prog2 = discovered > 0 ? Math.min(100, Math.max(0, (processed / discovered) * 100)) : 0;

  const circle2Ring = document.getElementById('web-circle2-ring');
  const prog2Val = document.getElementById('web-prog2-val');
  const prog2Sub = document.getElementById('web-prog2-sub');

  if (circle2Ring && prog2Val) {
    const C = 345.57;
    const offset = C - (prog2 / 100) * C;
    circle2Ring.style.strokeDashoffset = `${offset}`;
    prog2Val.innerText = `${prog2.toFixed(1)}%`;
    if (prog2Sub) prog2Sub.innerText = `${processed} / ${discovered} novos lidos`;

    if (data.is_monitoring && data.current_filename) {
      circle2Ring.classList.add('bar-active');
    } else {
      circle2Ring.classList.remove('bar-active');
    }
  }

  // Atualiza o console de logs em tempo real do sistema
  if (data.logs && Array.isArray(data.logs)) {
    const consoleElem = document.getElementById('web-log-console');
    if (consoleElem && data.logs.length > 0) {
      consoleElem.innerText = data.logs.join('\n');
      consoleElem.scrollTop = consoleElem.scrollHeight;
    }
  }

  // Se o número de arquivos processados mudar, atualiza a lista de relatórios da Web
  if (_lastProcessedCount !== processed) {
    _lastProcessedCount = processed;
    fetchReportsList();
  }
}

function isLlmExtraction(methodStr) {
  if (!methodStr) return false;
  const str = String(methodStr);
  if (str.includes('Sem IA') || str.includes('Regex') || str.toLowerCase().includes('erro')) {
    return false;
  }
  return str.includes('Ollama') || str.includes('LLM');
}

async function fetchReportsList() {
  try {
    const res = await fetch('/api/v1/relints?page_size=200');
    if (!res.ok) return;
    const data = await res.json();

    _allWebReports = Array.isArray(data) ? data : (data.items || []);
    const totalCount = _allWebReports.length;

    const cardTotal = document.getElementById('web-card-total');
    const cardLLM = document.getElementById('web-card-llm');
    const cardLLMPct = document.getElementById('web-card-llm-pct');
    const cardRegex = document.getElementById('web-card-regex');
    const cardRegexPct = document.getElementById('web-card-regex-pct');
    const subtabBadge = document.getElementById('web-subtab-badge');

    const circleTotalRing = document.getElementById('rep-circle-total-ring');
    const circleLLMRing = document.getElementById('rep-circle-llm-ring');
    const circleRegexRing = document.getElementById('rep-circle-regex-ring');

    let llmCount = 0;
    let regexCount = 0;

    _allWebReports.forEach(r => {
      if (isLlmExtraction(r.extraction_method)) {
        llmCount++;
      } else {
        regexCount++;
      }
    });

    if (cardTotal) cardTotal.innerText = totalCount;
    if (cardLLM) cardLLM.innerText = llmCount;
    if (cardRegex) cardRegex.innerText = regexCount;
    if (subtabBadge) subtabBadge.innerText = totalCount;

    const C = 345.57;

    if (circleTotalRing) {
      circleTotalRing.style.strokeDashoffset = totalCount > 0 ? '0' : `${C}`;
    }

    if (circleLLMRing) {
      const llmPct = totalCount > 0 ? (llmCount / totalCount) : 0;
      circleLLMRing.style.strokeDashoffset = `${C - (llmPct * C)}`;
      if (cardLLMPct) cardLLMPct.innerText = `${(llmPct * 100).toFixed(0)}%`;
    }

    if (circleRegexRing) {
      const regexPct = totalCount > 0 ? (regexCount / totalCount) : 0;
      circleRegexRing.style.strokeDashoffset = `${C - (regexPct * C)}`;
      if (cardRegexPct) cardRegexPct.innerText = `${(regexPct * 100).toFixed(0)}%`;
    }

    renderWebReportsList(_allWebReports);
  } catch (err) {
    console.error('Erro ao listar relatórios:', err);
  }
}

function filterWebReports() {
  const searchInput = document.getElementById('web-report-search');
  const methodSelect = document.getElementById('web-report-filter-method');
  
  const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const methodFilter = methodSelect ? methodSelect.value : 'all';

  const filtered = _allWebReports.filter(r => {
    // Filtro por Método
    const isLLM = isLlmExtraction(r.extraction_method);
    if (methodFilter === 'llm' && !isLLM) return false;
    if (methodFilter === 'regex' && isLLM) return false;

    // Filtro por Texto
    if (!query) return true;

    const subjectMatch = (r.subject || '').toLowerCase().includes(query);
    const fileMatch = (r.source_file || '').toLowerCase().includes(query);
    const summaryMatch = (r.summary || '').toLowerCase().includes(query);
    const cityMatch = (r.municipality || '').toLowerCase().includes(query);
    const partMatch = (r.participants || []).some(p => 
      (p.name || '').toLowerCase().includes(query) || 
      (p.nickname || '').toLowerCase().includes(query) || 
      (p.document || '').toLowerCase().includes(query)
    );

    return subjectMatch || fileMatch || summaryMatch || cityMatch || partMatch;
  });

  renderWebReportsList(filtered);
}

function renderWebReportsList(reports) {
  const listContainer = document.getElementById('web-reports-list');
  if (!listContainer) return;
  listContainer.innerHTML = '';

  if (!reports || reports.length === 0) {
    listContainer.innerHTML = `
      <div style="text-align: center; color: var(--ash); font-style: italic; padding: 20px; background: #121212; border-radius: 8px; border: 1px dashed var(--hairline);">
        Nenhum RELINT encontrado.
      </div>
    `;
    return;
  }

  reports.forEach(r => {
    const isLLM = isLlmExtraction(r.extraction_method);
    const hasError = (r.extraction_method || '').toLowerCase().includes('erro') || !!r.error_message;

    let badgeText = isLLM ? '🟢 Lido com LLM (Ollama)' : '⚡ Lido sem LLM (Regex)';
    let badgeColor = isLLM ? '#10b981' : '#f59e0b';
    let badgeBg = isLLM ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)';
    let badgeBorder = isLLM ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)';

    if (hasError) {
      badgeText = '🔴 Erro na Leitura';
      badgeColor = '#ef4444';
      badgeBg = 'rgba(239,68,68,0.15)';
      badgeBorder = 'rgba(239,68,68,0.3)';
    }

    const card = document.createElement('div');
    card.style.cssText = 'background: #18181b; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 8px;';

    const errorDetailsHTML = hasError ? `
      <div style="font-size: 11px; color: #f87171; margin-top: 2px; font-weight: 600;">
        ⚠️ Erro: ${r.error_message || 'Falha ao extrair dados do arquivo'}
      </div>
    ` : '';

    card.innerHTML = `
      <div style="display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0;">
        <span style="font-size: 18px;">📄</span>
        <div style="flex: 1; min-width: 0;">
          <div style="font-size: 14px; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${r.source_file}">
            ${r.source_file}
          </div>
          ${errorDetailsHTML}
        </div>
      </div>

      <div style="display: flex; align-items: center; gap: 12px; flex-shrink: 0;">
        <span style="background: ${badgeBg}; color: ${badgeColor}; font-weight: 700; font-size: 11px; padding: 4px 10px; border-radius: 4px; border: 1px solid ${badgeBorder}; white-space: nowrap;">
          ${badgeText}
        </span>
        <button class="btn-resend btn-resend-sm" onclick="reprocessWebFile('${r.source_file}')">
          <i data-lucide="refresh-cw"></i> Refazer Leitura
        </button>
      </div>
    `;

    listContainer.appendChild(card);
  });

  if (window.lucide) window.lucide.createIcons();
}

async function browseWebFolder() {
  try {
    appendWebLog('🔍 Abrindo seletor nativo de pasta do Windows...');
    const res = await fetch('/api/v1/monitoring/browse', { method: 'POST' });
    if (!res.ok) return;
    const data = await res.json();
    if (data.status === 'success' && data.path) {
      const input = document.getElementById('web-dir-input');
      if (input) input.value = data.path;
      appendWebLog(`Pasta selecionada: ${data.path}`);
      fetchMonitoringStatus();
    } else if (data.status === 'cancelled') {
      appendWebLog('Seleção de pasta cancelada.');
    }
  } catch (err) {
    console.error('Erro ao abrir diálogo de pasta:', err);
  }
}

async function setWebMonitoringPath() {
  const input = document.getElementById('web-dir-input');
  if (!input || !input.value.trim()) {
    alert('Informe o caminho da pasta local no servidor.');
    return;
  }

  try {
    const res = await fetch('/api/v1/monitoring/path', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: input.value.trim() })
    });

    const data = await res.json();
    if (res.ok) {
      appendWebLog(`Pasta de monitoramento definida: ${input.value.trim()}`);
      fetchMonitoringStatus();
    } else {
      alert(data.detail || 'Erro ao definir diretório.');
    }
  } catch (err) {
    alert('Erro de comunicação ao definir diretório.');
  }
}

async function toggleWebMonitoring() {
  const btnToggle = document.getElementById('web-btn-toggle-monitor');
  const statusBadge = document.getElementById('web-status-badge');
  const readingIconWrapper = document.getElementById('web-reading-icon-wrapper');
  const currentReadingText = document.getElementById('web-current-reading-text');

  const isCurrentlyActive = _isWebMonitoringActive;
  const endpoint = isCurrentlyActive ? '/api/v1/monitoring/stop' : '/api/v1/monitoring/start';

  // Atualização otimista imediata
  if (!isCurrentlyActive) {
    _isWebMonitoringActive = true;
    if (statusBadge) {
      statusBadge.innerHTML = 'Status: 🟢 Monitoramento Ativo';
      statusBadge.style.color = '#4ade80';
    }
    if (readingIconWrapper) {
      readingIconWrapper.innerHTML = `<i data-lucide="loader-2" class="spin-icon" style="color: #f59e0b; width: 16px; height: 16px;"></i>`;
    }
    if (currentReadingText) {
      currentReadingText.innerHTML = `<span style="color: #f59e0b; font-weight: 600;">Inicializando varredura dos PDFs em segundo plano...</span>`;
    }
    if (btnToggle) {
      btnToggle.className = 'btn-resend btn-resend-danger';
      btnToggle.innerHTML = `<i data-lucide="pause"></i> Pausar Monitoramento`;
    }
    appendWebLog('🚀 Comando de início acionado. Inicializando leitor em segundo plano...');
  } else {
    _isWebMonitoringActive = false;
    if (statusBadge) {
      statusBadge.innerHTML = 'Status: ⏸️ Monitoramento Pausado';
      statusBadge.style.color = '#f59e0b';
    }
    if (btnToggle) {
      btnToggle.className = 'btn-resend btn-resend-emerald';
      btnToggle.innerHTML = `<i data-lucide="play"></i> Iniciar Monitoramento`;
    }
    appendWebLog('⏸️ Pausando monitoramento...');
  }
  if (window.lucide) window.lucide.createIcons();

  try {
    const res = await fetch(endpoint, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) {
      _isWebMonitoringActive = isCurrentlyActive;
      alert(data.detail || 'Erro ao alterar estado do monitoramento.');
    }
  } catch (err) {
    _isWebMonitoringActive = isCurrentlyActive;
    alert('Erro de comunicação.');
  } finally {
    fetchMonitoringStatus();
  }
}

async function toggleWebLLM(enable) {
  try {
    const res = await fetch('/api/v1/monitoring/toggle-llm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ use_llm: enable })
    });
    const data = await res.json();
    appendWebLog(data.use_llm ? '🟢 Modo de extração por IA Local (Ollama) ATIVADO.' : '⚡ Modo de extração rápida (Regex / Sem IA) ATIVADO.');
    fetchMonitoringStatus();
  } catch (err) {
    console.error('Erro ao alterar chave da IA:', err);
  }
}

async function confirmWebResetAll() {
  if (!confirm('Atenção!\nEsta ação irá zerar todas as ocorrências salvas no banco de dados, limpar o cadastro de pessoas e apagar as mídias salvas.\n\nDeseja continuar e re-ler todos os RELINTs da pasta do zero?')) {
    return;
  }

  try {
    const res = await fetch('/api/v1/monitoring/reset', { method: 'POST' });
    if (res.ok) {
      appendWebLog('🔄 Reset completo da base de dados e mídias executado com sucesso.');
      fetchMonitoringStatus();
    }
  } catch (err) {
    alert('Erro ao executar o reset completo.');
  }
}

async function reprocessWebFile(filename) {
  try {
    const res = await fetch('/api/v1/monitoring/reprocess-file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename })
    });
    if (res.ok) {
      appendWebLog(`🚀 Re-leitura do arquivo ${filename} disparada.`);
      setTimeout(() => {
        fetchMonitoringStatus();
      }, 1000);
    }
  } catch (err) {
    alert('Erro ao disparar re-leitura.');
  }
}

function appendWebLog(msg) {
  const consoleElem = document.getElementById('web-log-console');
  if (!consoleElem) return;
  const time = new Date().toLocaleTimeString('pt-BR');
  consoleElem.innerText += `[${time}] ${msg}\n`;
  consoleElem.scrollTop = consoleElem.scrollHeight;
}

function clearWebLogs() {
  const consoleElem = document.getElementById('web-log-console');
  if (consoleElem) consoleElem.innerText = '';
}

function initMonitoringSSE() {
  if (monitoringEventSource) {
    monitoringEventSource.close();
  }

  monitoringEventSource = new EventSource('/api/v1/monitoring/events');
  monitoringEventSource.onmessage = function(e) {
    try {
      const data = JSON.parse(e.data);
      updateMonitoringUIState(data);
    } catch (err) {}
  };
}
