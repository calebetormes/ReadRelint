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
    <div class="relints-layout">
      <!-- Left Pane: Master List & Filters -->
      <div class="master-pane card" style="border-top: 4px solid #ef4444;">
        <div class="filter-bar">
          <div class="search-box">
            <i data-lucide="search" class="search-icon"></i>
            <input type="text" id="homicide-search-input" placeholder="Buscar homicídios, envolvidos..." />
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
          <p>Selecione um homicídio da lista à esquerda para visualizar o dossiê detalhado da especialidade.</p>
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
    
    // We only fetch where bm_group is "Homicídio"
    const params = new URLSearchParams();
    params.append('bm_group', 'Homicídio');
    if (search.trim()) params.append('search', search);

    const res = await fetch(`/api/v1/relints?${params.toString()}`);
    if (!res.ok) throw new Error('Falha ao buscar homicídios');
    
    const relints = await res.json();
    renderHomicidesMasterList(relints);
  } catch (err) {
    console.error(err);
    listContainer.innerHTML = `<div class="error-state">Erro ao carregar homicídios: ${err.message}</div>`;
  }
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
    <div class="relint-list-item" data-id="${r.id}" onclick="loadHomicideDetail('${r.id}')">
      <div class="item-header">
        <span class="badge" style="background-color: #ef4444; color: white;">Homicídio</span>
        <span class="item-date">${r.date_of_fact || 'Data Indefinida'}</span>
      </div>
      <div class="item-title">${r.subject || r.source_file}</div>
      <div class="item-meta">
        <span><i data-lucide="map-pin" style="width:12px;height:12px;"></i> ${r.municipality || 'Local Indefinido'}</span>
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

  detailPane.innerHTML = '<div class="loading-state">Carregando dossiê da especialidade...</div>';

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

  // Extract specialty fields (they will be present due to Extra Allow and Polymorphism)
  const regNumber = report.registry_number || "Não Informado";
  const regAgency = report.registry_agency || "Não Informado";
  const regYear = report.registry_year || "Não Informado";
  const factType = report.fact_type || "Não Informado";
  const unit = report.police_unit || "Não Informada";
  const motivation = report.motivation || "Desconhecida";

  let html = `
    <div class="detail-header">
      <h2>Dossiê de Homicídio: ${report.subject || report.source_file}</h2>
      <div class="header-actions">
        <span class="badge badge-rose">
          <i data-lucide="crosshair" style="width:14px;height:14px;margin-right:4px;"></i> ${factType.toUpperCase()}
        </span>
      </div>
    </div>

    <!-- Especialidade: Dados do Homicídio -->
    <div class="detail-section card glow-red" style="padding: 18px; margin-bottom: 24px;">
      <h3 style="color: var(--accent-red); margin-top: 0; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; font-weight: 500;">
        <i data-lucide="file-text" style="width: 18px; height: 18px;"></i>
        Dados da Especialidade Policial
      </h3>
      <div class="meta-grid">
        <div class="meta-item">
          <span class="meta-label">Motivação:</span>
          <span class="meta-value" style="font-weight: 600; color: var(--accent-red);">${motivation}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Registro Policial:</span>
          <span class="meta-value">${regNumber} / ${regYear} (${regAgency})</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Unidade (BPM):</span>
          <span class="meta-value">${unit}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Data/Hora:</span>
          <span class="meta-value">${report.date_of_fact || '?'} às ${report.time_of_fact || '?'}</span>
        </div>
      </div>
    </div>

    <div class="detail-section">
      <h3><i data-lucide="map"></i> Localização</h3>
      <p style="color: var(--body); margin-bottom: 12px;"><strong>Endereço:</strong> ${report.address || report.municipality || 'Não extraído'}</p>
      ${report.map_url ? `<a href="${report.map_url}" target="_blank" class="btn-map">Abrir no Google Maps</a>` : ''}
    </div>

    <div class="detail-section">
      <h3><i data-lucide="align-left"></i> Resumo do Fato</h3>
      <div class="summary-box">${report.summary || 'Resumo não gerado.'}</div>
    </div>
  `;

  // Victims & Accused
  if (report.participants && report.participants.length > 0) {
    const victims = report.participants.filter(p => (p.participation_type || '').toLowerCase() === 'vítima' || (p.participation_type || '').toLowerCase() === 'vitima');
    const accused = report.participants.filter(p => (p.participation_type || '').toLowerCase() === 'acusado' || (p.participation_type || '').toLowerCase() === 'suspeito');
    
    html += `<div class="detail-section">
      <h3><i data-lucide="users"></i> Envolvidos no Homicídio</h3>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div class="participant-card">
          <h4 style="margin-top:0; color: var(--ink); border-bottom: 1px solid var(--hairline); padding-bottom: 8px; font-weight: 500; font-size: 14px;">Vítimas (${victims.length})</h4>
          ${victims.length ? victims.map(v => `<div style="margin-top: 10px; margin-bottom: 8px;"><strong style="color: var(--ink);">${v.name}</strong> <br><small style="color: var(--ash);">${v.document || ''} ${v.nickname ? `(Vulgo: ${v.nickname})` : ''}</small></div>`).join('') : '<p style="color: var(--stone); font-size: 13px; margin-top: 10px;">Nenhuma vítima identificada formalmente</p>'}
        </div>
        <div class="participant-card">
          <h4 style="margin-top:0; color: var(--ink); border-bottom: 1px solid var(--hairline); padding-bottom: 8px; font-weight: 500; font-size: 14px;">Autores/Suspeitos (${accused.length})</h4>
          ${accused.length ? accused.map(a => `<div style="margin-top: 10px; margin-bottom: 8px;"><strong style="color: var(--ink);">${a.name}</strong> <br><small style="color: var(--ash);">${a.document || ''} ${a.nickname ? `(Vulgo: ${a.nickname})` : ''}</small></div>`).join('') : '<p style="color: var(--stone); font-size: 13px; margin-top: 10px;">Nenhum autor/suspeito identificado</p>'}
        </div>
      </div>
    </div>`;
  }

  // Galeria
  if (report.images && report.images.length > 0) {
    html += `
      <div class="detail-section">
        <h3><i data-lucide="image"></i> Fotos do Fato (${report.images.length})</h3>
        <div class="images-gallery-grid">
          ${report.images.map(img => `
            <div class="image-card" onclick="openLightbox('${img.path}', '${img.caption || 'Foto do Fato'}')">
              <div class="image-card-thumb-wrapper">
                <img src="${img.path}" alt="${img.caption || 'Foto'}" class="image-card-thumb" onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'150\' viewBox=\'0 0 200 150\' fill=\'%23101012\'><rect width=\'200\' height=\'150\' fill=\'%2306060a\'/><text x=\'50%25\' y=\'50%25\' dominant-baseline=\'middle\' text-anchor=\'middle\' fill=\'%23464a4d\' font-size=\'14\'>Sem Imagem</text></svg>';" />
              </div>
              <div class="image-card-caption" title="${img.caption || 'Anexo'}">
                ${img.caption || 'Foto anexada'}
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  detailPane.innerHTML = html;
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}
