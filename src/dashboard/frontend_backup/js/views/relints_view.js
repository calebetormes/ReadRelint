/**
 * RELINTs Master-Detail Controller & View Renderer
 */

let currentRelintId = null;
let allRelintsCache = [];

document.addEventListener('DOMContentLoaded', () => {
  initRelintsView();
});

function initRelintsView() {
  const container = document.getElementById('tab-relints');
  if (!container) return;

  // Render Master-Detail HTML Shell inside tab-relints
  container.innerHTML = `
    <div class="relints-layout">
      <!-- Left Pane: Master List & Filters -->
      <div class="master-pane card">
        <div class="filter-bar">
          <div class="search-box">
            <i data-lucide="search" class="search-icon"></i>
            <input type="text" id="relint-search-input" placeholder="Buscar por assunto, fato, envolvido..." />
          </div>
          
          <div class="filter-selectors">
            <select id="filter-bm-group">
              <option value="todos">Todos os Grupos BM</option>
              <option value="Roubo a Estabelecimento">Roubo a Estabelecimento</option>
              <option value="Roubo a Residência">Roubo a Residência</option>
              <option value="Roubo de Veículo">Roubo de Veículo</option>
              <option value="Roubo a Pedestre">Roubo a Pedestre</option>
              <option value="Furto Qualificado">Furto Qualificado</option>
              <option value="Furto de Veículo">Furto de Veículo</option>
              <option value="Prisão por Tráfico">Prisão por Tráfico</option>
              <option value="Outros">Outros</option>
            </select>

            <select id="filter-relint-type">
              <option value="todos">Todos os Tipos</option>
              <option value="Ocorrência">Ocorrência</option>
              <option value="Disk Denúncia">Disk Denúncia</option>
              <option value="Resposta a PB">Resposta a PB</option>
              <option value="Outros">Outros</option>
            </select>
          </div>
        </div>

        <div class="relint-list-container" id="relint-list-container">
          <div class="loading-state">Carregando relatórios...</div>
        </div>
      </div>

      <!-- Right Pane: Detail Dossier View -->
      <div class="detail-pane card" id="detail-pane">
        <div class="empty-detail-state">
          <i data-lucide="file-search" style="width: 48px; height: 48px; color: var(--text-muted);"></i>
          <h3>Nenhum RELINT selecionado</h3>
          <p>Selecione um relatório da lista à esquerda para visualizar os detalhes do RELINT.</p>
        </div>
      </div>
    </div>
  `;

  // Initialize icons inside newly injected HTML
  if (window.lucide) window.lucide.createIcons();

  // Attach Event Listeners for Filters
  document.getElementById('relint-search-input')?.addEventListener('input', debounce(fetchRelintsList, 300));
  document.getElementById('filter-bm-group')?.addEventListener('change', fetchRelintsList);
  document.getElementById('filter-relint-type')?.addEventListener('change', fetchRelintsList);

  // Initial Fetch
  fetchRelintsList();
}

async function fetchRelintsList() {
  const listContainer = document.getElementById('relint-list-container');
  if (!listContainer) return;

  const search = document.getElementById('relint-search-input')?.value || '';
  const bmGroup = document.getElementById('filter-bm-group')?.value || 'todos';
  const relintType = document.getElementById('filter-relint-type')?.value || 'todos';

  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (bmGroup !== 'todos') params.append('bm_group', bmGroup);
  if (relintType !== 'todos') params.append('relint_type', relintType);

  try {
    const res = await fetch(`/api/v1/relints?${params.toString()}`);
    if (!res.ok) throw new Error('Falha ao buscar relatórios');
    const data = await res.json();
    // Sort descending by numeric ID to guarantee newest added document is first
    data.sort((a, b) => (Number(b.id) || 0) - (Number(a.id) || 0));
    allRelintsCache = data;
    renderRelintsMasterList(data);
    if (!currentRelintId && data.length > 0) {
      selectRelint(data[0].id);
    }
  } catch (err) {
    listContainer.innerHTML = `<div class="error-state">Erro ao carregar RELINTs: ${err.message}</div>`;
  }
}

function extractRelintNumber(r) {
  const sourceFile = r.arquivo_origem || r.source_file || '';
  const subject = r.assunto || r.subject || '';
  const relintType = r.tipo_relint || r.relint_type || 'RELINT';
  const text = `${sourceFile} ${subject}`;
  const match = text.match(/\b(?:RELINT|RELAT[OÓ]RIO\s+DE\s+INTELIG[ÊE]NCIA)\s*(?:N[ºo°]?\s*)?(\d+(?:\/\d+)?)/i);
  if (match && match[1]) return `RELINT ${match[1]}`;
  
  const matchNo = text.match(/\bN[ºo°]\s*(\d+(?:\/\d+)?)/i);
  if (matchNo && matchNo[1]) return `RELINT ${matchNo[1]}`;

  const matchSimple = text.match(/RELINT[-_\s]*(\d+)/i);
  if (matchSimple && matchSimple[1]) return `RELINT ${matchSimple[1]}`;

  return relintType;
}

function renderRelintsMasterList(relints) {
  const listContainer = document.getElementById('relint-list-container');
  if (!listContainer) return;

  if (relints.length === 0) {
    listContainer.innerHTML = `
      <div class="empty-state">
        <p>Nenhum RELINT encontrado com os filtros aplicados.</p>
      </div>
    `;
    return;
  }

  listContainer.innerHTML = relints.map(r => {
    const isEdited = r.editado_usuario || r.user_edited;
    const titleText = r.assunto || r.subject || r.arquivo_origem || r.source_file || 'Sem Assunto';
    return `
    <div class="relint-item-card ${r.id === currentRelintId ? 'active' : ''}" onclick="selectRelint('${r.id}')">
      <div class="relint-item-content">
        <div class="relint-item-header-row" style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
          <span class="relint-number-badge">${escapeHtml(extractRelintNumber(r))}</span>
          ${isEdited ? `<span class="badge badge-emerald" style="font-size:10px;padding:2px 6px;"><i data-lucide="check-check" style="width:11px;height:11px;margin-right:2px;display:inline;"></i> REVISADO</span>` : ''}
        </div>
        <div class="relint-item-title-small" style="font-size:12.5px; font-weight:500; color:var(--ink); line-height:1.35; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;" title="${escapeHtml(titleText)}">
          ${escapeHtml(titleText)}
        </div>
      </div>
    </div>
  `}).join('');

  if (window.lucide) window.lucide.createIcons();
}

async function selectRelint(reportId) {
  currentRelintId = reportId;
  renderRelintsMasterList(allRelintsCache);

  const detailPane = document.getElementById('detail-pane');
  if (!detailPane) return;

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
    if (!res.ok) throw new Error('Não foi possível carregar os detalhes do RELINT.');
    const relint = await res.json();
    renderRelintDetail(relint);
  } catch (err) {
    detailPane.innerHTML = `<div class="error-state">${err.message}</div>`;
  }
}

function renderRelintDetail(relint) {
  const detailPane = document.getElementById('detail-pane');
  if (!detailPane) return;

  const partCount = (relint.participants || []).length;
  const imgCount = (relint.images || []).length;

  detailPane.innerHTML = `
    <div class="detail-header">
      <div class="detail-header-left">
        <div class="detail-source-file">
          <i data-lucide="file"></i> ${escapeHtml(relint.source_file)}
        </div>
        <h2 class="detail-title">${escapeHtml(relint.subject || 'Sem Assunto Definido')}</h2>
      </div>
      <div class="header-actions">
        ${relint.user_edited ? '<span class="badge badge-emerald" style="font-size:11px;"><i data-lucide="check-circle-2" style="width:12px;height:12px;margin-right:4px;display:inline;"></i> REVISADO</span>' : ''}
        <button type="button" class="btn btn-secondary btn-sm" onclick="openEditRelintModal('${escapeHtml(relint.id)}')">
          <i data-lucide="edit-3" style="width:13px;height:13px;display:inline;"></i> Editar RELINT
        </button>
      </div>
    </div>

    <!-- Navigation Tabs for Detail Pane -->
    <div class="detail-tab-nav">
      <button class="detail-tab-item active" onclick="switchDetailTab(this, 'relint-detail-tab-synthesis')">
        <i data-lucide="sparkles" style="width:14px;height:14px;"></i> Síntese
      </button>
      ${relint.bm_group && relint.bm_group !== 'Outros' ? `
        <button class="detail-tab-item" onclick="switchDetailTab(this, 'relint-detail-tab-specialties')" style="color: var(--accent-orange); font-weight: 600;">
          <i data-lucide="target" style="width:14px;height:14px;"></i> Especialidades
        </button>
      ` : ''}
      <button class="detail-tab-item" onclick="switchDetailTab(this, 'relint-detail-tab-participants')">
        <i data-lucide="users" style="width:14px;height:14px;"></i> Participantes <span class="tab-badge">${partCount}</span>
      </button>
      <button class="detail-tab-item" onclick="switchDetailTab(this, 'relint-detail-tab-photos')">
        <i data-lucide="image" style="width:14px;height:14px;"></i> Fotos <span class="tab-badge">${imgCount}</span>
      </button>
      <button class="detail-tab-item" onclick="switchDetailTab(this, 'relint-detail-tab-geo')">
        <i data-lucide="map-pin" style="width:14px;height:14px;"></i> Localização
      </button>
      <button class="detail-tab-item" onclick="switchDetailTab(this, 'relint-detail-tab-transcript')">
        <i data-lucide="file-text" style="width:14px;height:14px;"></i> Transcrição Integral
      </button>
    </div>

    <!-- Tab 1: Synthesis -->
    <div class="detail-tab-pane active" id="relint-detail-tab-synthesis">
      ${RelintTabsComponents.renderSynthesisTab(relint)}
    </div>

    <!-- Tab 1.5: Especialidades (Condicional) -->
    <div class="detail-tab-pane" id="relint-detail-tab-specialties">
      ${RelintTabsComponents.renderSpecialtiesTab(relint)}
    </div>

    <!-- Tab 2: Participants -->
    <div class="detail-tab-pane" id="relint-detail-tab-participants">
      <!-- Container populated via ParticipantsTabComponent -->
    </div>

    <!-- Tab 3: Photos & Media -->
    <div class="detail-tab-pane" id="relint-detail-tab-photos">
      ${RelintTabsComponents.renderPhotosTab(relint)}
    </div>

    <!-- Tab 4: Geolocation -->
    <div class="detail-tab-pane" id="relint-detail-tab-geo">
      ${RelintTabsComponents.renderLocationTab(relint)}
    </div>

    <!-- Tab 5: Full Transcript -->
    <div class="detail-tab-pane" id="relint-detail-tab-transcript">
      ${RelintTabsComponents.renderTranscriptTab(relint)}
    </div>
  `;

    // Render Participants Tab via unified component
    if (window.ParticipantsTabComponent) {
      ParticipantsTabComponent.render('relint-detail-tab-participants', relint.participants || [], relint.images || [], relint.id);
    }

  if (window.lucide) window.lucide.createIcons();
}

function copyTranscriptText() {
  const el = document.getElementById('transcript-raw-text');
  if (!el) return;
  const text = el.innerText || el.textContent;
  navigator.clipboard.writeText(text).then(() => {
    alert('Transcrição literal copiada para a área de transferência!');
  }).catch(err => {
    console.error('Falha ao copiar:', err);
  });
}

function switchDetailTab(btnElement, paneId) {
  const container = btnElement.closest('.detail-pane');
  if (!container) return;

  container.querySelectorAll('.detail-tab-item').forEach(b => b.classList.remove('active'));
  container.querySelectorAll('.detail-tab-pane').forEach(p => p.classList.remove('active'));

  btnElement.classList.add('active');
  const targetPane = container.querySelector('#' + paneId);
  if (targetPane) targetPane.classList.add('active');
}

function getPrecisionBadgeClass(level) {
  switch (level) {
    case 'exact_coords':
      return 'badge-emerald';
    case 'direct_link':
      return 'badge-blue';
    case 'address_inferred':
    case 'low_precision':
      return 'badge-amber';
    default:
      return 'badge-muted';
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}



function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    setTimeout(later, wait);
  };
}


/* ─────────────────────────────────────────────────────────────────────────────
   Modal De Edição De RELINTs & Especialidades
   ───────────────────────────────────────────────────────────────────────────── */

async function openEditRelintModal(reportId) {
  const modal = document.getElementById('edit-relint-modal');
  if (!modal) return;

  try {
    const res = await fetch(`/api/v1/relints/${reportId}`);
    if (!res.ok) throw new Error('Falha ao obter detalhes para edição.');
    const relint = await res.json();

    document.getElementById('edit-report-id').value = relint.id || reportId;
    document.getElementById('edit-modal-title').innerText = `Editar RELINT — ${relint.source_file || ''}`;

    // 1. Tab Geral
    document.getElementById('edit-subject').value = relint.subject || '';
    document.getElementById('edit-police-unit').value = relint.police_unit || '';
    document.getElementById('edit-main-fact').value = relint.main_fact || '';
    document.getElementById('edit-date-of-fact').value = relint.date_of_fact || '';
    document.getElementById('edit-time-of-fact').value = relint.time_of_fact || '';
    document.getElementById('edit-relint-type').value = relint.relint_type || 'Ocorrência';
    document.getElementById('edit-bm-group').value = relint.bm_group || 'Outros';
    document.getElementById('edit-summary').value = relint.summary || '';

    // 2. Tab Geo
    document.getElementById('edit-municipality').value = relint.municipality || '';
    document.getElementById('edit-neighborhood').value = relint.neighborhood || '';
    document.getElementById('edit-address').value = relint.address || '';
    document.getElementById('edit-coordinates').value = relint.coordinates || '';
    document.getElementById('edit-map-url').value = relint.map_url || '';

    // 1. Tab Geral & Registro Policial
    let regNum = relint.numero_registro || relint.registry_number || '';
    let regAgency = relint.orgao_registro || relint.registry_agency || '';
    let regYear = relint.ano_registro || relint.registry_year || '';

    if (regNum.includes('/') && (!regAgency || !regYear)) {
      const parts = regNum.split('/');
      if (parts.length >= 3) {
        regNum = parts[0].trim();
        regAgency = parts[1].trim();
        regYear = parts[2].trim();
      }
    }

    const regNumInput = document.getElementById('edit-reg-number');
    const regAgencyInput = document.getElementById('edit-reg-agency');
    const regYearInput = document.getElementById('edit-reg-year');
    if (regNumInput) regNumInput.value = regNum;
    if (regAgencyInput) regAgencyInput.value = regAgency;
    if (regYearInput) regYearInput.value = regYear;

    // 2. Tab Geo
    document.getElementById('edit-municipality').value = relint.municipality || '';
    document.getElementById('edit-neighborhood').value = relint.neighborhood || '';
    document.getElementById('edit-address').value = relint.address || '';
    document.getElementById('edit-coordinates').value = relint.coordinates || '';
    document.getElementById('edit-map-url').value = relint.map_url || '';

    // 3. Tab Especialidades
    document.getElementById('edit-bm-group').addEventListener('change', toggleSpecialtyFormTab);
    
    // Homicídio
    let factTypeVal = relint.fact_type || '';
    if (!factTypeVal || factTypeVal === 'Não Informado') {
      const subj = (relint.subject || '').toLowerCase();
      factTypeVal = (subj.includes('tentativa') || subj.includes('tentado')) ? 'Tentado' : 'Consumado';
    }
    const factTypeInput = document.getElementById('edit-hom-fact-type');
    const motivationInput = document.getElementById('edit-hom-motivation');
    if (factTypeInput) factTypeInput.value = factTypeVal;
    if (motivationInput) motivationInput.value = relint.motivation || 'Desconhecido';

    // Prisão por Tráfico
    if (relint.drug_trafficking_details) {
      document.getElementById('edit-drug-quantity').value = relint.drug_trafficking_details.drug_quantity || '';
      document.getElementById('edit-drug-types').value = relint.drug_trafficking_details.drug_types || '';
    }

    // Roubo a Estabelecimento
    if (relint.establishment_robbery_details) {
      document.getElementById('edit-estab-type').value = relint.establishment_robbery_details.establishment_type || '';
      document.getElementById('edit-estab-loc-type').value = relint.establishment_robbery_details.location_type || 'Urbano';
      document.getElementById('edit-estab-injured').value = relint.establishment_robbery_details.injured_victims || 0;
      document.getElementById('edit-estab-hostage').value = relint.establishment_robbery_details.hostage_victim || 0;
    }

    // Roubo a Residência
    if (relint.residence_robbery_details) {
      document.getElementById('edit-res-loc-type').value = relint.residence_robbery_details.location_type || 'Urbano';
      document.getElementById('edit-res-injured').value = relint.residence_robbery_details.injured_victims || 0;
      document.getElementById('edit-res-hostage').value = relint.residence_robbery_details.hostage_victim || 0;
    }

    // Roubo de Veículo
    if (relint.vehicle_robbery_details) {
      document.getElementById('edit-vrob-model').value = relint.vehicle_robbery_details.vehicle_model || '';
      document.getElementById('edit-vrob-plate').value = relint.vehicle_robbery_details.license_plate || '';
      document.getElementById('edit-vrob-recovered').value = relint.vehicle_robbery_details.recovered || 0;
      document.getElementById('edit-vrob-rec-loc').value = relint.vehicle_robbery_details.recovery_location || '';
    }

    // Roubo a Pedestre
    if (relint.pedestrian_robbery_details) {
      document.getElementById('edit-ped-injured').value = relint.pedestrian_robbery_details.injured_victims || 0;
      document.getElementById('edit-ped-weapon').value = relint.pedestrian_robbery_details.weapon_used || '';
      document.getElementById('edit-ped-object').value = relint.pedestrian_robbery_details.stolen_object || '';
    }

    // Furto de Veículo
    if (relint.vehicle_theft_details) {
      document.getElementById('edit-vtheft-model').value = relint.vehicle_theft_details.vehicle_model || '';
      document.getElementById('edit-vtheft-plate').value = relint.vehicle_theft_details.license_plate || '';
      document.getElementById('edit-vtheft-recovered').value = relint.vehicle_theft_details.recovered || 0;
      document.getElementById('edit-vtheft-rec-loc').value = relint.vehicle_theft_details.recovery_location || '';
    }

    toggleSpecialtyFormTab();


    // 4. Tab Participantes
    window.currentEditRelintImages = relint.images || [];
    const container = document.getElementById('edit-participants-container');
    container.innerHTML = '';
    const parts = relint.participants || [];
    if (parts.length === 0) {
      addParticipantEditRow({}, window.currentEditRelintImages);
    } else {
      parts.forEach(p => addParticipantEditRow(p, window.currentEditRelintImages));
    }

    // 5. Tab Transcrição
    document.getElementById('edit-content').value = relint.content || '';

    modal.classList.add('active');
    if (window.lucide) window.lucide.createIcons();
  } catch (err) {
    alert('Erro ao abrir formulário de edição: ' + err.message);
  }
}

function closeEditRelintModal(event) {
  if (event && event.target && !event.target.classList.contains('modal-backdrop') && !event.target.classList.contains('modal-close-btn')) {
    return;
  }
  const modal = document.getElementById('edit-relint-modal');
  if (modal) modal.classList.remove('active');
}

function switchEditTab(btnElement, paneId) {
  const modal = btnElement.closest('.modal-card');
  if (!modal) return;

  modal.querySelectorAll('.modal-tab-btn').forEach(b => b.classList.remove('active'));
  modal.querySelectorAll('.modal-tab-pane').forEach(p => p.classList.remove('active'));

  btnElement.classList.add('active');
  const target = modal.querySelector('#' + paneId);
  if (target) target.classList.add('active');
}

function toggleSpecialtyFormTab() {
  const bmGroup = document.getElementById('edit-bm-group').value;
  const groups = [
    { id: 'homicide-specialty-fields', condition: bmGroup === 'Homicídio' },
    { id: 'drug-trafficking-specialty-fields', condition: bmGroup === 'Prisão por Tráfico' },
    { id: 'establishment-robbery-specialty-fields', condition: bmGroup === 'Roubo a Estabelecimento' },
    { id: 'residence-robbery-specialty-fields', condition: bmGroup === 'Roubo a Residência' },
    { id: 'vehicle-robbery-specialty-fields', condition: bmGroup === 'Roubo de Veículo' },
    { id: 'pedestrian-robbery-specialty-fields', condition: bmGroup === 'Roubo a Pedestre' },
    { id: 'vehicle-theft-specialty-fields', condition: bmGroup === 'Furto de Veículo' }
  ];

  let anyActive = false;
  groups.forEach(g => {
    const el = document.getElementById(g.id);
    if (el) {
      if (g.condition) {
        el.style.display = 'block';
        anyActive = true;
      } else {
        el.style.display = 'none';
      }
    }
  });

  const otherFields = document.getElementById('other-specialty-fields');
  if (otherFields) {
    otherFields.style.display = anyActive ? 'none' : 'block';
  }
}

function addParticipantEditRow(data = {}, relintImages = []) {
  const container = document.getElementById('edit-participants-container');
  if (!container) return;

  const images = relintImages.length ? relintImages : (window.currentEditRelintImages || []);
  const selectedPhoto = data.photo_path || data.caminho_foto || '';

  let photoOptions = `<option value="">Sem foto vinculada</option>`;
  images.forEach((imgUrl, idx) => {
    const filename = imgUrl.split('/').pop();
    const isSel = (imgUrl === selectedPhoto) ? 'selected' : '';
    photoOptions += `<option value="${escapeHtml(imgUrl)}" ${isSel}>Foto ${idx + 1} (${escapeHtml(filename)})</option>`;
  });

  const row = document.createElement('div');
  row.className = 'edit-participant-row';
  row.innerHTML = `
    <input type="text" class="form-control part-name" placeholder="Nome Completo *" value="${escapeHtml(data.name || data.nome || '')}" required />
    <input type="text" class="form-control part-nickname" placeholder="Alcunha / Vulgo" value="${escapeHtml(data.nickname || data.alcunha || '')}" />
    <input type="text" class="form-control part-document" placeholder="CPF / RG" value="${escapeHtml(data.document || data.documento || '')}" />
    <input type="text" class="form-control part-background" placeholder="Antecedentes" value="${escapeHtml(data.background || data.antecedentes || '')}" />
    <select class="form-control part-type">
      <option value="Autor/Suspeito" ${(data.participation_type === 'Autor/Suspeito' || data.participation_type === 'Acusado' || data.participation_type === 'Suspeito' || !data.participation_type) ? 'selected' : ''}>Autor/Suspeito</option>
      <option value="Vítima" ${data.participation_type === 'Vítima' ? 'selected' : ''}>Vítima</option>
      <option value="Testemunha" ${data.participation_type === 'Testemunha' ? 'selected' : ''}>Testemunha</option>
    </select>
    <select class="form-control part-photo" title="Selecione a foto principal deste participante">
      ${photoOptions}
    </select>
    <button type="button" class="btn-remove-part" onclick="removeParticipantEditRow(this)" title="Remover Participante">&times;</button>
  `;
  container.appendChild(row);
}

function removeParticipantEditRow(btn) {
  const row = btn.closest('.edit-participant-row');
  if (row) row.remove();
}

async function submitEditRelint(event) {
  if (event) event.preventDefault();

  const reportId = document.getElementById('edit-report-id').value;
  if (!reportId) return;

  const btnSave = document.getElementById('btn-save-edit-relint');
  if (btnSave) {
    btnSave.disabled = true;
    btnSave.innerHTML = `<svg class="spin-fast" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg> Salvando...`;
  }

  try {
    const bmGroup = document.getElementById('edit-bm-group').value;
    const isHomicide = (bmGroup === 'Homicídio');

    const partRows = document.querySelectorAll('#edit-participants-container .edit-participant-row');
    const participants = [];
    partRows.forEach(row => {
      const name = row.querySelector('.part-name').value.trim();
      if (name) {
        participants.push({
          name: name,
          nickname: row.querySelector('.part-nickname').value.trim(),
          document: row.querySelector('.part-document').value.trim(),
          background: row.querySelector('.part-background').value.trim(),
          participation_type: row.querySelector('.part-type').value,
          photo_path: row.querySelector('.part-photo')?.value || '',
        });
      }
    });

    const regNumVal = document.getElementById('edit-reg-number') ? document.getElementById('edit-reg-number').value : '';
    const regAgencyVal = document.getElementById('edit-reg-agency') ? document.getElementById('edit-reg-agency').value : '';
    const regYearVal = document.getElementById('edit-reg-year') ? document.getElementById('edit-reg-year').value : '';

    const payload = {
      subject: document.getElementById('edit-subject').value,
      police_unit: document.getElementById('edit-police-unit').value,
      registry_number: regNumVal,
      registry_agency: regAgencyVal,
      registry_year: regYearVal,
      main_fact: document.getElementById('edit-main-fact').value,
      date_of_fact: document.getElementById('edit-date-of-fact').value,
      time_of_fact: document.getElementById('edit-time-of-fact').value,
      relint_type: document.getElementById('edit-relint-type').value,
      bm_group: bmGroup,
      summary: document.getElementById('edit-summary').value,
      municipality: document.getElementById('edit-municipality').value,
      neighborhood: document.getElementById('edit-neighborhood').value,
      address: document.getElementById('edit-address').value,
      coordinates: document.getElementById('edit-coordinates').value,
      map_url: document.getElementById('edit-map-url').value,
      content: document.getElementById('edit-content').value,
      participants: participants,
      user_edited: true,
    };

    if (payload.bm_group === 'Homicídio') {
      payload.homicide_details = {
        registry_number: regNumVal,
        registry_agency: regAgencyVal,
        registry_year: regYearVal,
        fact_type: document.getElementById('edit-hom-fact-type').value,
        motivation: document.getElementById('edit-hom-motivation').value
      };
    } else if (payload.bm_group === 'Prisão por Tráfico') {
      payload.drug_trafficking_details = {
        drug_quantity: document.getElementById('edit-drug-quantity').value,
        drug_types: document.getElementById('edit-drug-types').value
      };
    } else if (payload.bm_group === 'Roubo a Estabelecimento') {
      payload.establishment_robbery_details = {
        establishment_type: document.getElementById('edit-estab-type').value,
        location_type: document.getElementById('edit-estab-loc-type').value,
        injured_victims: parseInt(document.getElementById('edit-estab-injured').value, 10) || 0,
        hostage_victim: parseInt(document.getElementById('edit-estab-hostage').value, 10) || 0
      };
    } else if (payload.bm_group === 'Roubo a Residência') {
      payload.residence_robbery_details = {
        location_type: document.getElementById('edit-res-loc-type').value,
        injured_victims: parseInt(document.getElementById('edit-res-injured').value, 10) || 0,
        hostage_victim: parseInt(document.getElementById('edit-res-hostage').value, 10) || 0
      };
    } else if (payload.bm_group === 'Roubo de Veículo') {
      payload.vehicle_robbery_details = {
        vehicle_model: document.getElementById('edit-vrob-model').value,
        license_plate: document.getElementById('edit-vrob-plate').value,
        recovered: parseInt(document.getElementById('edit-vrob-recovered').value, 10) || 0,
        recovery_location: document.getElementById('edit-vrob-rec-loc').value
      };
    } else if (payload.bm_group === 'Roubo a Pedestre') {
      payload.pedestrian_robbery_details = {
        injured_victims: parseInt(document.getElementById('edit-ped-injured').value, 10) || 0,
        weapon_used: document.getElementById('edit-ped-weapon').value,
        stolen_object: document.getElementById('edit-ped-object').value
      };
    } else if (payload.bm_group === 'Furto de Veículo') {
      payload.vehicle_theft_details = {
        vehicle_model: document.getElementById('edit-vtheft-model').value,
        license_plate: document.getElementById('edit-vtheft-plate').value,
        recovered: parseInt(document.getElementById('edit-vtheft-recovered').value, 10) || 0,
        recovery_location: document.getElementById('edit-vtheft-rec-loc').value
      };
    }

    const res = await fetch(`/api/v1/relints/${reportId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.detail || 'Erro ao salvar alterações do RELINT.');
    }

    const updatedRelint = await res.json();
    closeEditRelintModal();
    renderRelintDetail(updatedRelint);
    initRelintsView();

    if (typeof loadHomicidesData === 'function') {
      loadHomicidesData();
    }
  } catch (err) {
    alert('Erro ao salvar: ' + err.message);
  } finally {
    if (btnSave) {
      btnSave.disabled = false;
      btnSave.innerHTML = `<i data-lucide="check" style="width:14px;height:14px;display:inline;"></i> Salvar Alterações`;
      if (window.lucide) window.lucide.createIcons();
    }
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
