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

  detailPane.innerHTML = '<div class="loading-state">Carregando detalhes do RELINT...</div>';

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

  const regNumber = report.registry_number || "Não Informado";
  const regAgency = report.registry_agency || "Não Informado";
  const regYear = report.registry_year || "Não Informado";
  const factType = report.fact_type || "Não Informado";
  const unit = report.police_unit || "Não Informada";
  const motivation = report.motivation || "Desconhecida";

  const partCount = (report.participants || []).length;
  const imgCount = (report.images || []).length;

  detailPane.innerHTML = `
    <div class="detail-header">
      <h2>RELINT de Homicídio: ${report.subject || report.source_file}</h2>
      <div class="header-actions" style="display:flex; gap:10px; align-items:center;">
        ${report.user_edited ? '<span class="badge badge-emerald" style="font-size:11px;"><i data-lucide="check-circle-2" style="width:12px;height:12px;margin-right:4px;display:inline;"></i> REVISADO</span>' : ''}
        <span class="badge badge-rose">
          <i data-lucide="crosshair" style="width:14px;height:14px;margin-right:4px;"></i> ${factType.toUpperCase()}
        </span>
        <button class="btn btn-secondary btn-sm" onclick="openEditRelintModal('${report.id}')">
          <i data-lucide="edit-3" style="width:14px;height:14px;margin-right:4px;display:inline;"></i> Revisar
        </button>
      </div>
    </div>

    <!-- Navigation Tabs for Detail Pane -->
    <div class="detail-tab-nav">
      <button class="detail-tab-item active" onclick="switchDetailTab(this, 'homicide-detail-tab-synthesis')">
        <i data-lucide="sparkles" style="width:14px;height:14px;"></i> Síntese &amp; Fatos
      </button>
      <button class="detail-tab-item" onclick="switchDetailTab(this, 'homicide-detail-tab-participants')">
        <i data-lucide="users" style="width:14px;height:14px;"></i> Envolvidos <span class="tab-badge">${partCount}</span>
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

    <!-- Tab 1: Synthesis & Fatos -->
    <div class="detail-tab-pane active" id="homicide-detail-tab-synthesis">
      <!-- Highlighted Synthesis Card (First / Top) -->
      <div class="synthesis-card" style="border-left-color: var(--accent-red);">
        <h3 class="synthesis-title" style="color: var(--accent-red);"><i data-lucide="sparkles"></i> Síntese da Ocorrência</h3>
        <p class="synthesis-text">${report.summary || 'Nenhuma síntese gerada.'}</p>
      </div>

      <!-- Expanded Fact Details & Geolocation Card (Below Synthesis) -->
      <div class="dossier-section card" style="padding: 20px; margin-bottom: 20px;">
        <h3 class="section-title" style="margin-top: 0; margin-bottom: 16px;">
          <i data-lucide="info"></i> Detalhes do Fato &amp; Georreferenciamento
        </h3>
        
        <div class="grid-2" style="margin-bottom: 16px; gap: 16px;">
          <div class="fact-card">
            <span class="fact-label"><i data-lucide="calendar" style="width:12px;height:12px;display:inline;"></i> Data e Hora do Fato</span>
            <span class="fact-value">${report.date_of_fact || 'N/I'} ${report.time_of_fact ? 'às ' + report.time_of_fact : ''}</span>
          </div>
          <div class="fact-card">
            <span class="fact-label"><i data-lucide="shield" style="width:12px;height:12px;display:inline;"></i> Grupo BM / Tipo de Documento</span>
            <span class="fact-value" style="color: var(--accent-red); font-weight:600;">Homicídio (${report.relint_type || 'Ocorrência'})</span>
          </div>
        </div>

        <!-- Geolocation Details -->
        <div style="padding-top: 14px; border-top: 1px solid var(--hairline);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
            <span class="fact-label" style="font-size:12px;font-weight:600;color:var(--ink);display:flex;align-items:center;gap:6px;">
              <i data-lucide="map-pin" style="color:var(--accent-red);"></i> Localização e Georreferenciamento
            </span>
            <span class="badge ${getPrecisionBadgeClass(report.precision_level)}">${report.precision_label || 'Sem Localização'}</span>
          </div>

          <div style="font-size:13.5px;color:var(--ink);margin-bottom:8px;line-height:1.5;">
            <strong>Endereço Extraído:</strong> ${report.address || report.municipality || 'Endereço não informado'}
          </div>

          ${report.coordinates ? `
            <div style="margin-bottom:12px;display:flex;align-items:center;gap:8px;">
              <span style="font-size:12px;color:var(--ash);">Coordenadas GPS:</span>
              <code class="geo-code" style="font-size:12px;padding:3px 8px;">${report.coordinates}</code>
            </div>
          ` : ''}

          ${report.map_url ? `
            <div style="margin-top:12px;">
              <a href="${report.map_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" style="display:inline-flex;align-items:center;gap:6px;">
                <i data-lucide="external-link"></i> Abrir no Google Maps
              </a>
            </div>
          ` : ''}
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
            <span class="meta-label">Tipo de Fato:</span>
            <span class="meta-value">${factType}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 2: Participants / Envolvidos -->
    <div class="detail-tab-pane" id="homicide-detail-tab-participants">
      ${report.participants && report.participants.length > 0 ? `
        <div class="detail-section">
          <h3 class="section-title"><i data-lucide="users"></i> Envolvidos no Homicídio (${partCount})</h3>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
            <div class="participant-card">
              <h4 style="margin-top:0; color: var(--ink); border-bottom: 1px solid var(--hairline); padding-bottom: 8px; font-weight: 500; font-size: 14px;">Vítimas (${report.participants.filter(p => (p.participation_type || '').toLowerCase().includes('vítima') || (p.participation_type || '').toLowerCase().includes('vitima')).length})</h4>
              ${report.participants.filter(p => (p.participation_type || '').toLowerCase().includes('vítima') || (p.participation_type || '').toLowerCase().includes('vitima')).length ? report.participants.filter(p => (p.participation_type || '').toLowerCase().includes('vítima') || (p.participation_type || '').toLowerCase().includes('vitima')).map(v => `<div style="margin-top: 10px; margin-bottom: 8px;"><strong style="color: var(--ink);">${v.name}</strong> <br><small style="color: var(--ash);">${v.document || ''} ${v.nickname ? `(Vulgo: ${v.nickname})` : ''}</small></div>`).join('') : '<p style="color: var(--stone); font-size: 13px; margin-top: 10px;">Nenhuma vítima identificada formalmente</p>'}
            </div>
            <div class="participant-card">
              <h4 style="margin-top:0; color: var(--ink); border-bottom: 1px solid var(--hairline); padding-bottom: 8px; font-weight: 500; font-size: 14px;">Autores/Suspeitos (${report.participants.filter(p => !(p.participation_type || '').toLowerCase().includes('vítima') && !(p.participation_type || '').toLowerCase().includes('vitima')).length})</h4>
              ${report.participants.filter(p => !(p.participation_type || '').toLowerCase().includes('vítima') && !(p.participation_type || '').toLowerCase().includes('vitima')).length ? report.participants.filter(p => !(p.participation_type || '').toLowerCase().includes('vítima') && !(p.participation_type || '').toLowerCase().includes('vitima')).map(a => `<div style="margin-top: 10px; margin-bottom: 8px;"><strong style="color: var(--ink);">${a.name}</strong> <span class="badge badge-rose" style="font-size:10px;margin-left:4px;">${a.participation_type || 'Acusado'}</span><br><small style="color: var(--ash);">${a.document || ''} ${a.nickname ? `(Vulgo: ${a.nickname})` : ''}</small></div>`).join('') : '<p style="color: var(--stone); font-size: 13px; margin-top: 10px;">Nenhum autor/suspeito identificado</p>'}
            </div>
          </div>
        </div>
      ` : '<p class="text-muted">Nenhum participante registrado neste Homicídio.</p>'}
    </div>

    <!-- Tab 3: Photos -->
    <div class="detail-tab-pane" id="homicide-detail-tab-photos">
      <div class="dossier-section">
        <h3 class="section-title"><i data-lucide="image"></i> Fotos &amp; Anexos do Fato (${imgCount})</h3>
        ${imgCount === 0 ? '<p class="text-muted">Nenhuma foto extraída deste RELINT de Homicídio.</p>' : `
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
        `}
      </div>
    </div>

    <!-- Tab 4: Location -->
    <div class="detail-tab-pane" id="homicide-detail-tab-geo">
      <div class="dossier-section card-geo card" style="padding:20px;">
        <div class="geo-header" style="margin-bottom:16px;">
          <h3 class="section-title" style="margin-bottom: 0;"><i data-lucide="map-pin"></i> Localização &amp; Georreferenciamento</h3>
          <span class="badge ${getPrecisionBadgeClass(report.precision_level)}">${report.precision_label || 'Sem Localização'}</span>
        </div>
        <div class="geo-body">
          <div class="geo-address" style="margin-bottom:12px;font-size:14px;">
            <strong>Endereço Formatado:</strong> ${report.address || 'Não informado'}
          </div>
          ${report.municipality ? `<div style="font-size:13px;color:var(--ash);margin-bottom:6px;"><strong>Município:</strong> ${report.municipality}</div>` : ''}
          ${report.neighborhood ? `<div style="font-size:13px;color:var(--ash);margin-bottom:6px;"><strong>Bairro:</strong> ${report.neighborhood}</div>` : ''}
          ${report.police_unit ? `<div style="font-size:13px;color:var(--ash);margin-bottom:6px;"><strong>Unidade PM:</strong> ${report.police_unit}</div>` : ''}
          ${report.coordinates ? `<div class="geo-coords" style="margin-top:12px;"><strong>Coordenadas GPS:</strong> <code class="geo-code" style="font-size:13px;padding:4px 8px;">${report.coordinates}</code></div>` : ''}

          ${report.map_url ? `
            <div class="geo-map-action" style="margin-top:16px;">
              <a href="${report.map_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
                <i data-lucide="external-link"></i> Abrir no Google Maps
              </a>
            </div>
          ` : ''}
        </div>
      </div>
    </div>

    <!-- Tab 5: Full Transcript -->
    <div class="detail-tab-pane" id="homicide-detail-tab-transcript">
      <div class="transcript-free-header">
        <div>
          <h3 class="section-title" style="margin-bottom:4px;border-bottom:none;padding-bottom:0;">
            <i data-lucide="file-text"></i> Transcrição Literal Completa (PDF)
          </h3>
          <div style="font-size:12px;color:var(--ash);margin-top:2px;">
            ${(report.content || '').split('\n').length} linhas • ${(report.content || '').length.toLocaleString('pt-BR')} caracteres
          </div>
        </div>

        <button type="button" class="btn btn-secondary btn-sm" onclick="copyTranscriptText()">
          <i data-lucide="copy" style="width:13px;height:13px;display:inline;"></i> Copiar Texto Completo
        </button>
      </div>

      <div class="transcript-free-content" id="transcript-raw-text">${escapeHtml(formatTranscriptText(report.content))}</div>
    </div>
  `;

  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}
