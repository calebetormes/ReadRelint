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
          <p>Selecione um relatório da lista à esquerda para visualizar o dossiê detalhado.</p>
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
    allRelintsCache = data;
    renderRelintsMasterList(data);
  } catch (err) {
    listContainer.innerHTML = `<div class="error-state">Erro ao carregar RELINTs: ${err.message}</div>`;
  }
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
      <div class="relint-item-header">
        <span class="badge badge-blue">${escapeHtml(r.relint_type || 'RELINT')}</span>
        <span class="relint-date">${escapeHtml(r.date_of_fact || 'Data N/I')}</span>
      </div>
      
      <div class="relint-item-subject">${escapeHtml(r.subject || 'Sem Assunto')}</div>
      <div class="relint-item-summary">${escapeHtml(r.summary || r.source_file)}</div>

      <div class="relint-item-footer">
        <span class="relint-muni"><i data-lucide="map-pin"></i> ${escapeHtml(r.municipality || 'N/I')}</span>
        <div class="relint-meta">
          <span><i data-lucide="users"></i> ${r.participants_count}</span>
          ${r.user_edited ? '<span class="edited-tag" title="Editado pelo usuário">✓ Editado</span>' : ''}
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

  detailPane.innerHTML = `<div class="loading-state">Carregando dossiê do relatório...</div>`;

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

  detailPane.innerHTML = `
    <div class="detail-header">
      <div>
        <div class="detail-source-file"><i data-lucide="file"></i> ${escapeHtml(relint.source_file)}</div>
        <h2 class="detail-title">${escapeHtml(relint.subject || 'Sem Assunto Definido')}</h2>
      </div>
      <div class="detail-actions">
        <button class="btn btn-secondary" onclick="toggleEditModal('${relint.id}')">
          <i data-lucide="edit-3"></i> Editar
        </button>
      </div>
    </div>

    <!-- Fact Details Grid -->
    <div class="fact-grid">
      <div class="fact-card">
        <span class="fact-label">Data e Hora do Fato</span>
        <span class="fact-value">${escapeHtml(relint.date_of_fact || 'N/I')} ${relint.time_of_fact ? 'às ' + escapeHtml(relint.time_of_fact) : ''}</span>
      </div>
      <div class="fact-card">
        <span class="fact-label">Grupo BM / Tipo</span>
        <span class="fact-value">${escapeHtml(relint.bm_group || 'Outros')} (${escapeHtml(relint.relint_type || 'Outros')})</span>
      </div>
    </div>

    <!-- Geolocation & Address Section -->
    <div class="dossier-section card-geo">
      <div class="geo-header">
        <h3 class="section-title" style="margin-bottom: 0;"><i data-lucide="map-pin"></i> Localização da Ocorrência</h3>
        <span class="badge ${getPrecisionBadgeClass(relint.precision_level)}">${escapeHtml(relint.precision_label || 'Sem Localização')}</span>
      </div>

      <div class="geo-body">
        <div class="geo-address">
          <strong>Endereço Extraído:</strong> ${escapeHtml(relint.address || 'Não informado')}
        </div>
        ${relint.coordinates ? `<div class="geo-coords"><strong>Coordenadas GPS:</strong> <code>${escapeHtml(relint.coordinates)}</code></div>` : ''}

        ${relint.map_url ? `
          <div class="geo-map-action">
            <a href="${escapeHtml(relint.map_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-map">
              <i data-lucide="external-link"></i> Abrir no Google Maps
            </a>
          </div>
        ` : ''}
      </div>
    </div>

    <!-- Summary -->
    <div class="dossier-section">
      <h3 class="section-title"><i data-lucide="align-left"></i> Resumo Analítico</h3>
      <div class="summary-box">${escapeHtml(relint.summary || 'Nenhum resumo gerado.')}</div>
    </div>

    <!-- Photos & Media Section -->
    <div class="dossier-section">
      <h3 class="section-title"><i data-lucide="image"></i> Fotos & Anexos do Fato (${relint.images ? relint.images.length : 0})</h3>
      ${!relint.images || relint.images.length === 0 ? '<p class="text-muted" style="font-size: 0.9rem;">Nenhuma foto extraída deste RELINT.</p>' : `
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

    <!-- Participants Section -->
    <div class="dossier-section">
      <h3 class="section-title"><i data-lucide="users"></i> Participantes Citados (${relint.participants.length})</h3>
      ${relint.participants.length === 0 ? '<p class="text-muted">Nenhum participante registrado.</p>' : `
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

    <!-- Full Content Accordion -->
    <div class="dossier-section">
      <details class="content-details">
        <summary class="section-title" style="cursor: pointer;"><i data-lucide="file-text"></i> Transcrição Literal Completa (PDF)</summary>
        <pre class="raw-content-pre">${escapeHtml(relint.content || 'Texto não disponível.')}</pre>
      </details>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function getPrecisionBadgeClass(level) {
  switch (level) {
    case 'exact_coords':
      return 'badge-emerald';
    case 'direct_link':
      return 'badge-blue';
    case 'address_inferred':
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
