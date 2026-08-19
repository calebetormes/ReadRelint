/**
 * Homicides Specialty View Renderer
 */

document.addEventListener('DOMContentLoaded', () => {
  initHomicidesView();
});

function initHomicidesView() {
  const container = document.getElementById('tab-homicides');
  if (!container) return;

  // Render Master-Detail HTML Shell inside tab-homicides
  container.innerHTML = `
    <!-- Tabs de Especialidade no Topo -->
    <div class="detail-tab-nav" style="margin-bottom: 16px; flex-wrap: nowrap; overflow-x: auto; overflow-y: hidden;" id="specialty-tabs-container">
      <button class="detail-tab-item active" data-val="Homicídio">Homicídio</button>
      <button class="detail-tab-item" data-val="Prisão por Tráfico">Tráfico</button>
      <button class="detail-tab-item" data-val="Roubo a Estabelecimento">Roubo Estab.</button>
      <button class="detail-tab-item" data-val="Roubo a Residência">Roubo Resid.</button>
      <button class="detail-tab-item" data-val="Roubo de Veículo">Roubo Veíc.</button>
      <button class="detail-tab-item" data-val="Roubo a Pedestre">Roubo Ped.</button>
      <button class="detail-tab-item" data-val="Furto de Veículo">Furto Veíc.</button>
    </div>

    <div class="relints-layout">
      <!-- Left Pane: Master List & Filters -->
      <div class="master-pane card" style="border-top: 4px solid #ef4444;">
        <div class="filter-bar" style="display:flex; flex-direction:column; gap:8px;">

          <div class="search-box">
            <i data-lucide="search" class="search-icon"></i>
            <input type="text" id="homicide-search-input" placeholder="Buscar registros, envolvidos..." />
          </div>
        </div>

        <div class="relint-list-container" id="homicide-list-container">
          <div class="loading-state">Carregando homicídios...</div>
        </div>
      </div>

      <!-- Right Pane: Detail Dossier View -->
      <div class="detail-pane card" id="homicide-detail-pane">
        <div class="empty-detail-state">
          <i data-lucide="crosshair" style="width: 48px; height: 48px; color: var(--text-muted);"></i>
          <h3>Nenhum Caso Selecionado</h3>
          <p>Selecione um homicídio da lista à esquerda para visualizar o RELINT detalhado da especialidade.</p>
        </div>
      </div>
    </div>
  `;

  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
  setupHomicidesEvents();
  fetchHomicides();
}

function setupHomicidesEvents() {
  const searchInput = document.getElementById('homicide-search-input');
  
  // Setup tabs
  const tabBtns = document.querySelectorAll('#specialty-tabs-container .detail-tab-item');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      tabBtns.forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      fetchHomicides();
    });
  });

  if (searchInput) {
    let timeout;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => fetchHomicides(), 400);
    });
  }
}

async function fetchHomicides() {
  const listContainer = document.getElementById('homicide-list-container');
  if (!listContainer) return;
  listContainer.innerHTML = '<div class="loading-state">Carregando...</div>';

  try {
    const search = document.getElementById('homicide-search-input')?.value || '';
    
    // Obter o valor da aba ativa
    const activeTab = document.querySelector('#specialty-tabs-container .detail-tab-item.active');
    const group = activeTab ? activeTab.getAttribute('data-val') : 'Homicídio';

    // We only fetch where bm_group matches the select
    const params = new URLSearchParams();
    params.append('bm_group', group);
    if (search.trim()) params.append('search', search);

    const res = await fetch(`/api/v1/relints?${params.toString()}`);
    if (!res.ok) throw new Error('Falha ao buscar homicídios');

    const relints = await res.json();
    // Sort descending by numeric ID to guarantee newest added document is first
    relints.sort((a, b) => (Number(b.id) || 0) - (Number(a.id) || 0));
    renderHomicidesMasterList(relints);
    if (relints.length > 0) {
      loadHomicideDetail(relints[0].id);
    }
  } catch (err) {
    console.error(err);
    listContainer.innerHTML = `<div class="error-state">Erro ao carregar homicídios: ${err.message}</div>`;
  }
}

function extractRelintNumber(r) {
  const text = `${r.source_file || ''} ${r.subject || ''}`;
  const match = text.match(/\b(?:RELINT|RELAT[OÓ]RIO\s+DE\s+INTELIG[ÊE]NCIA)\s*(?:N[ºo°]?\s*)?(\d+(?:\/\d+)?)/i);
  if (match && match[1]) return `RELINT ${match[1]}`;

  const matchNo = text.match(/\bN[ºo°]\s*(\d+(?:\/\d+)?)/i);
  if (matchNo && matchNo[1]) return `RELINT ${matchNo[1]}`;

  const matchSimple = text.match(/RELINT[-_\s]*(\d+)/i);
  if (matchSimple && matchSimple[1]) return `RELINT ${matchSimple[1]}`;

  return r.relint_type || 'RELINT';
}

function renderHomicidesMasterList(relints) {
  const listContainer = document.getElementById('homicide-list-container');
  if (!listContainer) return;

  if (relints.length === 0) {
    listContainer.innerHTML = `
      <div class="empty-detail-state">
        <p>Nenhum homicídio encontrado.</p>
      </div>`;
    return;
  }

  listContainer.innerHTML = relints.map(r => `
    <div class="relint-item-card" data-id="${r.id}" onclick="loadHomicideDetail('${r.id}')">
      <div class="relint-item-content">
        <div class="relint-item-header-row" style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
          <span class="relint-number-badge" style="color: var(--accent-red); border-color: rgba(255,32,71,0.25);">${extractRelintNumber(r)}</span>
          ${r.user_edited ? `<span class="badge badge-emerald" style="font-size:10px;padding:2px 6px;"><i data-lucide="check-check" style="width:11px;height:11px;margin-right:2px;display:inline;"></i> REVISADO</span>` : ''}
        </div>
        <div class="relint-item-title-small" style="font-size:12.5px; font-weight:500; color:var(--ink); line-height:1.35; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;" title="${r.subject || r.source_file}">
          ${r.subject || r.source_file}
        </div>
      </div>
    </div>
  `).join('');

  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

async function loadHomicideDetail(reportId) {
  const detailPane = document.getElementById('homicide-detail-pane');
  if (!detailPane) return;

  // Update active state in list
  document.querySelectorAll('#homicide-list-container .relint-list-item').forEach(el => {
    el.classList.toggle('active', el.dataset.id === reportId);
  });

  detailPane.innerHTML = `
    <div class="loading-state">
      <svg class="spin-fast" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
      </svg>
      <span style="font-weight: 600; font-size: 14px;">Carregando detalhes do RELINT...</span>
    </div>
  `;

  try {
    const res = await fetch(`/api/v1/relints/${reportId}`);
    if (!res.ok) throw new Error('Falha ao carregar detalhes');

    const data = await res.json();
    renderHomicideDetail(data);
  } catch (err) {
    console.error(err);
    detailPane.innerHTML = `<div class="error-state">Erro: ${err.message}</div>`;
  }
}

function renderHomicideDetail(report) {
  const detailPane = document.getElementById('homicide-detail-pane');
  if (!detailPane) return;

  const regNum = report.numero_registro || report.registry_number;
  const regAgency = report.orgao_registro || report.registry_agency;
  const regYear = report.ano_registro || report.registry_year;
  const subjectText = report.assunto || report.subject || report.arquivo_origem || report.source_file || 'Sem Assunto Definido';
  const sourceFile = report.arquivo_origem || report.source_file || '';
  const mainFact = report.fato_principal || report.main_fact || '';
  const isEdited = report.editado_usuario || report.user_edited;

  let regDisplay = "Não Informado";
  if (regNum && regNum !== "Não Informado") {
    if (regNum.includes('/')) {
      regDisplay = regNum;
    } else {
      const parts = [regNum];
      if (regAgency && regAgency !== "Não Informado") parts.push(regAgency);
      if (regYear && regYear !== "Não Informado") parts.push(regYear);
      regDisplay = parts.join(' / ');
    }
  }

  let factType = report.tipo_fato || report.fact_type;
  if (!factType || factType === "Não Informado") {
    const subj = subjectText.toLowerCase();
    const main = mainFact.toLowerCase();
    if (subj.includes('tentativa') || subj.includes('tentado') || main.includes('tentativa') || main.includes('tentado')) {
      factType = "Tentado";
    } else if (subj.includes('consumado') || main.includes('consumado')) {
      factType = "Consumado";
    } else {
      factType = "Não Informado";
    }
  }
  const unit = report.unidade_policial || report.police_unit || "Não Informada";
  const motivation = report.motivacao || report.motivation || "Desconhecida";

  const participantsList = report.participantes || report.participants || [];
  const imagesList = report.imagens || report.images || [];
  const partCount = participantsList.length;
  const imgCount = imagesList.length;

  detailPane.innerHTML = `
    <div class="detail-header">
      <div class="detail-header-left">
        <div class="detail-source-file">
          <i data-lucide="file"></i> ${escapeHtml(sourceFile)}
        </div>
        <h2 class="detail-title">${escapeHtml(subjectText)}</h2>
      </div>
      <div class="header-actions">
        ${isEdited ? '<span class="badge badge-emerald" style="font-size:11px;"><i data-lucide="check-circle-2" style="width:12px;height:12px;margin-right:4px;display:inline;"></i> REVISADO</span>' : ''}
        <span class="badge badge-rose">
          <i data-lucide="crosshair" style="width:14px;height:14px;margin-right:4px;"></i> ${factType.toUpperCase()}
        </span>
        <button type="button" class="btn btn-secondary btn-sm" onclick="openEditRelintModal('${report.id}')">
          <i data-lucide="edit-3" style="width:13px;height:13px;display:inline;"></i> Editar Caso
        </button>
      </div>
    </div>

    <!-- Navigation Tabs for Detail Pane -->
    <div class="detail-tab-nav">
      <button class="detail-tab-item active" onclick="switchDetailTab(this, 'homicide-detail-tab-synthesis')">
        <i data-lucide="sparkles" style="width:14px;height:14px;"></i> Síntese
      </button>
      ${report.bm_group && report.bm_group !== 'Outros' ? `
        <button class="detail-tab-item" onclick="switchDetailTab(this, 'homicide-detail-tab-specialties')" style="color: var(--accent-red); font-weight: 600;">
          <i data-lucide="target" style="width:14px;height:14px;"></i> Especialidades
        </button>
      ` : ''}
      <button class="detail-tab-item" onclick="switchDetailTab(this, 'homicide-detail-tab-participants')">
        <i data-lucide="users" style="width:14px;height:14px;"></i> Participantes <span class="tab-badge">${partCount}</span>
      </button>
      <button class="detail-tab-item" onclick="switchDetailTab(this, 'homicide-detail-tab-photos')">
        <i data-lucide="image" style="width:14px;height:14px;"></i> Fotos <span class="tab-badge">${imgCount}</span>
      </button>
      <button class="detail-tab-item" onclick="switchDetailTab(this, 'homicide-detail-tab-geo')">
        <i data-lucide="map-pin" style="width:14px;height:14px;"></i> Localização
      </button>
      <button class="detail-tab-item" onclick="switchDetailTab(this, 'homicide-detail-tab-transcript')">
        <i data-lucide="file-text" style="width:14px;height:14px;"></i> Transcrição Integral
      </button>
    </div>

    <!-- Tab 1: Synthesis -->
    <div class="detail-tab-pane active" id="homicide-detail-tab-synthesis">
      ${RelintTabsComponents.renderSynthesisTab(report)}
    </div>

    <!-- Tab 1.5: Especialidades (Condicional) -->
    <div class="detail-tab-pane" id="homicide-detail-tab-specialties">
      ${RelintTabsComponents.renderSpecialtiesTab(report)}
    </div>

    <!-- Tab 2: Participants / Envolvidos -->
    <div class="detail-tab-pane" id="homicide-detail-tab-participants">
      <!-- Container populated via ParticipantsTabComponent -->
    </div>

    <!-- Tab 3: Photos -->
    <div class="detail-tab-pane" id="homicide-detail-tab-photos">
      ${RelintTabsComponents.renderPhotosTab(report)}
    </div>

    <!-- Tab 4: Location -->
    <div class="detail-tab-pane" id="homicide-detail-tab-geo">
      ${RelintTabsComponents.renderLocationTab(report)}
    </div>

    <!-- Tab 5: Full Transcript -->
    <div class="detail-tab-pane" id="homicide-detail-tab-transcript">
      ${RelintTabsComponents.renderTranscriptTab(report)}
    </div>
  `;

    // Render Participants Tab via unified component
    if (window.ParticipantsTabComponent) {
      ParticipantsTabComponent.render('homicide-detail-tab-participants', report.participantes || report.participants || [], imagesList || [], report.id);
    }

    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
}

function getPrecisionBadgeClass(level) {
  switch (level) {
    case 'exact_coords': return 'badge-emerald';
    case 'direct_link': return 'badge-blue';
    case 'address_inferred':
    case 'low_precision': return 'badge-amber';
    default: return 'badge-muted';
  }
}

function getPrecisionIconHtml(level) {
  switch (level) {
    case 'exact_coords': return '<i data-lucide="crosshair" style="width:12px;height:12px;display:inline;"></i>';
    case 'direct_link': return '<i data-lucide="link" style="width:12px;height:12px;display:inline;"></i>';
    case 'address_inferred':
    case 'low_precision': return '<i data-lucide="search" style="width:12px;height:12px;display:inline;"></i>';
    default: return '<i data-lucide="map-pin-off" style="width:12px;height:12px;display:inline;"></i>';
  }
}
