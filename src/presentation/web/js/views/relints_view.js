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
  const text = `${r.source_file || ''} ${r.subject || ''}`;
  const match = text.match(/\b(?:RELINT|RELAT[OÓ]RIO\s+DE\s+INTELIG[ÊE]NCIA)\s*(?:N[ºo°]?\s*)?(\d+(?:\/\d+)?)/i);
  if (match && match[1]) return `RELINT ${match[1]}`;
  
  const matchNo = text.match(/\bN[ºo°]\s*(\d+(?:\/\d+)?)/i);
  if (matchNo && matchNo[1]) return `RELINT ${matchNo[1]}`;

  const matchSimple = text.match(/RELINT[-_\s]*(\d+)/i);
  if (matchSimple && matchSimple[1]) return `RELINT ${matchSimple[1]}`;

  return r.relint_type || 'RELINT';
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

  listContainer.innerHTML = relints.map(r => `
    <div class="relint-item-card ${r.id === currentRelintId ? 'active' : ''}" onclick="selectRelint('${r.id}')">
      <div class="relint-item-content">
        <div class="relint-item-header-row" style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
          <span class="relint-number-badge">${escapeHtml(extractRelintNumber(r))}</span>
          ${r.user_edited ? `<span class="badge badge-emerald" style="font-size:10px;padding:2px 6px;"><i data-lucide="check-check" style="width:11px;height:11px;margin-right:2px;display:inline;"></i> REVISADO</span>` : ''}
        </div>
        <div class="relint-item-title-small" style="font-size:12.5px; font-weight:500; color:var(--ink); line-height:1.35; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;" title="${escapeHtml(r.subject || r.source_file)}">
          ${escapeHtml(r.subject || r.source_file)}
        </div>
      </div>
    </div>
  `).join('');

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
      <div>
        <div class="detail-source-file"><i data-lucide="file"></i> ${escapeHtml(relint.source_file)} ${relint.user_edited ? '<span class="badge badge-emerald" style="margin-left:8px;font-size:11px;"><i data-lucide="check-circle-2" style="width:12px;height:12px;margin-right:4px;display:inline;"></i> REVISADO</span>' : ''}</div>
        <h2 class="detail-title">${escapeHtml(relint.subject || 'Sem Assunto Definido')}</h2>
      </div>
    </div>

    <!-- Navigation Tabs for Detail Pane -->
    <div class="detail-tab-nav">
      <button class="detail-tab-item active" onclick="switchDetailTab(this, 'relint-detail-tab-synthesis')">
        <i data-lucide="sparkles" style="width:14px;height:14px;"></i> Síntese &amp; Fatos
      </button>
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

    <!-- Tab 1: Synthesis & Fatos -->
    <div class="detail-tab-pane active" id="relint-detail-tab-synthesis">
      <!-- Highlighted Synthesis Card (First / Top) -->
      <div class="synthesis-card">
        <h3 class="synthesis-title"><i data-lucide="sparkles"></i> Síntese da Ocorrência</h3>
        <p class="synthesis-text">${escapeHtml(relint.summary || 'Nenhuma síntese gerada.')}</p>
      </div>

      <!-- Expanded Fact Details & Geolocation Card (Below Synthesis) -->
      <div class="dossier-section card" style="padding: 20px; margin-bottom: 20px;">
        <h3 class="section-title" style="margin-top: 0; margin-bottom: 16px;">
          <i data-lucide="info"></i> Detalhes do Fato &amp; Georreferenciamento
        </h3>
        
        <div class="grid-2" style="margin-bottom: 16px; gap: 16px;">
          <div class="fact-card">
            <span class="fact-label"><i data-lucide="calendar" style="width:12px;height:12px;display:inline;"></i> Data e Hora do Fato</span>
            <span class="fact-value">${escapeHtml(relint.date_of_fact || 'N/I')} ${relint.time_of_fact ? 'às ' + escapeHtml(relint.time_of_fact) : ''}</span>
          </div>
          <div class="fact-card">
            <span class="fact-label"><i data-lucide="shield" style="width:12px;height:12px;display:inline;"></i> Grupo BM / Unidade PM</span>
            <span class="fact-value">${escapeHtml(relint.bm_group || 'Outros')} ${relint.police_unit ? '• ' + escapeHtml(relint.police_unit) : ''}</span>
          </div>
        </div>

        ${relint.main_fact ? `
          <div style="margin-bottom: 16px; padding: 12px 14px; background-color: var(--canvas); border: 1px solid var(--hairline); border-radius: var(--r-md);">
            <span class="fact-label" style="font-size:11px;color:var(--ash);text-transform:uppercase;">Evento Principal (Main Fact)</span>
            <div style="font-size:13.5px;font-weight:500;color:var(--ink);margin-top:4px;">${escapeHtml(relint.main_fact)}</div>
          </div>
        ` : ''}

        <!-- Geolocation Details -->
        <div style="padding-top: 14px; border-top: 1px solid var(--hairline);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
            <span class="fact-label" style="font-size:12px;font-weight:600;color:var(--ink);display:flex;align-items:center;gap:6px;">
              <i data-lucide="map-pin" style="color:var(--accent-orange);"></i> Localização e Georreferenciamento
            </span>
            <span class="badge ${getPrecisionBadgeClass(relint.precision_level)}">${escapeHtml(relint.precision_label || 'Sem Localização')}</span>
          </div>

          <div style="font-size:13.5px;color:var(--ink);margin-bottom:8px;line-height:1.5;">
            <strong>Endereço Extraído:</strong> ${escapeHtml(relint.address || 'Endereço não informado')}
          </div>

          ${relint.coordinates ? `
            <div style="margin-bottom:12px;display:flex;align-items:center;gap:8px;">
              <span style="font-size:12px;color:var(--ash);">Coordenadas GPS:</span>
              <code class="geo-code" style="font-size:12px;padding:3px 8px;">${escapeHtml(relint.coordinates)}</code>
            </div>
          ` : ''}

          ${relint.map_url ? `
            <div style="margin-top:12px;">
              <a href="${escapeHtml(relint.map_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" style="display:inline-flex;align-items:center;gap:6px;">
                <i data-lucide="external-link"></i> Abrir no Google Maps
              </a>
            </div>
          ` : ''}
        </div>
      </div>
    </div>

    <!-- Tab 2: Participants -->
    <div class="detail-tab-pane" id="relint-detail-tab-participants">
      <div class="dossier-section">
        <h3 class="section-title"><i data-lucide="users"></i> Participantes Citados (${partCount})</h3>
        ${partCount === 0 ? '<p class="text-muted">Nenhum participante registrado neste RELINT.</p>' : `
          <div class="participants-grid">
            ${relint.participants.map(p => `
              <div class="participant-card">
                <div class="participant-header">
                  <div class="participant-name">${escapeHtml(p.name)}</div>
                  <span class="badge ${p.participation_type === 'Vítima' ? 'badge-emerald' : 'badge-rose'}">${escapeHtml(p.participation_type || 'Acusado')}</span>
                </div>
                ${p.nickname ? `<div class="participant-sub">Alcunha: <strong>${escapeHtml(p.nickname)}</strong></div>` : ''}
                ${p.document ? `<div class="participant-sub">Documento: ${escapeHtml(p.document)}</div>` : ''}
                ${p.background ? `<div class="participant-sub">Antecedentes: ${escapeHtml(p.background)}</div>` : ''}
              </div>
            `).join('')}
          </div>
        `}
      </div>
    </div>

    <!-- Tab 3: Photos & Media -->
    <div class="detail-tab-pane" id="relint-detail-tab-photos">
      <div class="dossier-section">
        <h3 class="section-title"><i data-lucide="image"></i> Fotos &amp; Anexos do Fato (${imgCount})</h3>
        ${imgCount === 0 ? '<p class="text-muted" style="font-size: 0.9rem;">Nenhuma foto extraída deste RELINT.</p>' : `
          <div class="images-gallery-grid">
            ${relint.images.map(img => `
              <div class="image-card" onclick="openLightbox('${escapeHtml(img.path)}', '${escapeHtml(img.caption || relint.subject || 'Foto do Fato')}')">
                <div class="image-card-thumb-wrapper">
                  <img src="${escapeHtml(img.path)}" alt="${escapeHtml(img.caption || 'Foto do Fato')}" class="image-card-thumb" onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'150\' viewBox=\'0 0 200 150\' fill=\'%231e293b\'><rect width=\'200\' height=\'150\' fill=\'%230f172a\'/><text x=\'50%25\' y=\'50%25\' dominant-baseline=\'middle\' text-anchor=\'middle\' fill=\'%2364748b\' font-size=\'14\'>Sem Imagem</text></svg>';" />
                  <span class="image-card-badge">Pág ${img.page || 1}</span>
                </div>
                ${img.caption ? `<div class="image-card-caption">${escapeHtml(img.caption)}</div>` : ''}
              </div>
            `).join('')}
          </div>
        `}
      </div>
    </div>

    <!-- Tab 4: Geolocation -->
    <div class="detail-tab-pane" id="relint-detail-tab-geo">
      <div class="dossier-section card-geo card" style="padding:20px;">
        <div class="geo-header" style="margin-bottom:16px;">
          <h3 class="section-title" style="margin-bottom: 0;"><i data-lucide="map-pin"></i> Localização &amp; Georreferenciamento</h3>
          <span class="badge ${getPrecisionBadgeClass(relint.precision_level)}">${escapeHtml(relint.precision_label || 'Sem Localização')}</span>
        </div>
        <div class="geo-body">
          <div class="geo-address" style="margin-bottom:12px;font-size:14px;">
            <strong>Endereço Formatado:</strong> ${escapeHtml(relint.address || 'Não informado')}
          </div>
          ${relint.municipality ? `<div style="font-size:13px;color:var(--ash);margin-bottom:6px;"><strong>Município:</strong> ${escapeHtml(relint.municipality)}</div>` : ''}
          ${relint.neighborhood ? `<div style="font-size:13px;color:var(--ash);margin-bottom:6px;"><strong>Bairro:</strong> ${escapeHtml(relint.neighborhood)}</div>` : ''}
          ${relint.police_unit ? `<div style="font-size:13px;color:var(--ash);margin-bottom:6px;"><strong>Unidade PM:</strong> ${escapeHtml(relint.police_unit)}</div>` : ''}
          ${relint.coordinates ? `<div class="geo-coords" style="margin-top:12px;"><strong>Coordenadas GPS:</strong> <code class="geo-code" style="font-size:13px;padding:4px 8px;">${escapeHtml(relint.coordinates)}</code></div>` : ''}

          ${relint.map_url ? `
            <div class="geo-map-action" style="margin-top:16px;">
              <a href="${escapeHtml(relint.map_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
                <i data-lucide="external-link"></i> Abrir no Google Maps
              </a>
            </div>
          ` : ''}
        </div>
      </div>
    </div>

    <!-- Tab 5: Full Transcript -->
    <div class="detail-tab-pane" id="relint-detail-tab-transcript">
      <div class="transcript-free-header">
        <div>
          <h3 class="section-title" style="margin-bottom:4px;border-bottom:none;padding-bottom:0;">
            <i data-lucide="file-text"></i> Transcrição Literal Completa (PDF)
          </h3>
          <div style="font-size:12px;color:var(--ash);margin-top:2px;">
            ${(relint.content || '').split('\n').length} linhas • ${(relint.content || '').length.toLocaleString('pt-BR')} caracteres
          </div>
        </div>

        <button type="button" class="btn btn-secondary btn-sm" onclick="copyTranscriptText()">
          <i data-lucide="copy" style="width:13px;height:13px;display:inline;"></i> Copiar Texto Completo
        </button>
      </div>

      <div class="transcript-free-content" id="transcript-raw-text">${escapeHtml(formatTranscriptText(relint.content))}</div>
    </div>
  `;

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
