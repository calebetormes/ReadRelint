/**
 * ReadRelint — Aba Participantes (Layout Master-Detail 40% / 60%)
 * Cruzamento de Envolvidos, Fotos Cruzadas e Dossiê Individual
 */

let allParticipantsCache = [];
let currentSelectedPersonId = null;

async function fetchParticipants() {
  const container = document.getElementById('tab-participants');
  if (!container) return;

  // Renderiza a estrutura básica Master-Detail (40% / 60%)
  container.innerHTML = `
    <div class="participants-layout">
      <!-- Coluna da Esquerda (40%): Master List & Filtros -->
      <div class="participant-master-pane">
        <!-- Barra de Filtros e Busca -->
        <div style="display:flex; flex-direction:column; gap:10px; padding-bottom:12px; border-bottom:1px solid var(--hairline);">
          <div style="display:flex; align-items:center; justify-content:space-between;">
            <div style="font-size:14px; font-weight:600; color:var(--ink); display:flex; align-items:center; gap:6px;">
              <i data-lucide="users" style="color:var(--accent-blue); width:16px; height:16px;"></i> Envolvidos
            </div>
            <span id="part-stats-kpi" class="badge badge-muted" style="font-size:11px;">Carregando...</span>
          </div>

          <!-- Input de Busca -->
          <div style="position:relative;">
            <input type="text" id="participant-search-input" class="form-control" placeholder="Buscar por Nome, Vulgo, RG/CPF..." oninput="filterParticipantsList()" style="padding-left:30px; height:34px; font-size:12px;" />
            <i data-lucide="search" style="position:absolute; left:9px; top:50%; transform:translateY(-50%); width:13px; height:13px; color:var(--ash);"></i>
          </div>

          <!-- Toggle Apenas Reincidentes -->
          <label style="font-size:12px; color:var(--ink); display:flex; align-items:center; justify-content:space-between; cursor:pointer; background:var(--canvas); padding:6px 10px; border-radius:6px; border:1px solid var(--hairline);">
            <span style="display:flex; align-items:center; gap:6px;">
              <span style="width:8px; height:8px; border-radius:50%; background:var(--accent-red); display:inline-block;"></span>
              Apenas Reincidentes (&gt;1 RELINT)
            </span>
            <input type="checkbox" id="chk-recurrent-only" onchange="filterParticipantsList()" style="accent-color:var(--accent-red);" />
          </label>
        </div>

        <!-- Lista Scrollável de Participantes -->
        <div class="participant-list-container" id="participant-master-list">
          <div class="loading-state" style="padding:24px; text-align:center; color:var(--ash);">
            <svg class="spin-fast" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom:6px;"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
            <div>Carregando envolvidos...</div>
          </div>
        </div>
      </div>

      <!-- Coluna da Direita (70%): Painel do Dossiê do Participante -->
      <div class="participant-detail-pane" id="participant-detail-pane">
        <div class="empty-detail-state" style="height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; color:var(--stone); gap:12px;">
          <i data-lucide="user-search" style="width:48px; height:48px; color:var(--ash);"></i>
          <h3 style="color:var(--ink); font-size:16px; font-weight:500;">Nenhum participante selecionado</h3>
          <p style="font-size:13px; max-width:320px; color:var(--ash); line-height:1.4;">Selecione um indivíduo da lista à esquerda para visualizar seu dossiê completo, fotos extraídas e histórico de ocorrências.</p>
        </div>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();

  try {
    const res = await fetch('/api/v1/participants');
    if (!res.ok) {
      const errTxt = await res.text();
      throw new Error(`HTTP ${res.status}: ${errTxt || res.statusText}`);
    }

    allParticipantsCache = await res.json();
    filterParticipantsList();
  } catch (err) {
    const listEl = document.getElementById('participant-master-list');
    if (listEl) {
      listEl.innerHTML = `
        <div class="card glow-red" style="padding:16px; color:var(--accent-red); margin:8px;">
          <div style="font-weight:600; font-size:13px; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
            <i data-lucide="alert-triangle" style="width:14px; height:14px;"></i> Erro de Carregamento
          </div>
          <div style="font-size:11px; opacity:0.9; margin-bottom:10px;">${escapeHtml(err.message)}</div>
          <button type="button" class="btn btn-secondary btn-sm" onclick="fetchParticipants()" style="width:100%; justify-content:center;">
            <i data-lucide="refresh-cw" style="width:12px; height:12px; display:inline;"></i> Tentar Novamente
          </button>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
    }
  }
}

function filterParticipantsList() {
  const searchVal = (document.getElementById('participant-search-input')?.value || '').toLowerCase().trim();
  const recurrentOnly = document.getElementById('chk-recurrent-only')?.checked || false;

  const filtered = allParticipantsCache.filter(p => {
    if (recurrentOnly && (p.linked_relints_count || p.quantidade_relints || 0) <= 1) {
      return false;
    }
    if (searchVal) {
      const nameMatch = (p.name || p.nome || '').toLowerCase().includes(searchVal);
      const nickMatch = (p.nickname || p.alcunha || '').toLowerCase().includes(searchVal);
      const docMatch = (p.document || p.documento || '').toLowerCase().replace(/[\.\-]/g, '').includes(searchVal.replace(/[\.\-]/g, ''));
      if (!nameMatch && !nickMatch && !docMatch) return false;
    }
    return true;
  });

  // Atualiza Badge de Métricas no topo do Master Pane
  const kpiEl = document.getElementById('part-stats-kpi');
  if (kpiEl) {
    const totalRecurrent = filtered.filter(p => (p.linked_relints_count || p.quantidade_relints || 0) > 1).length;
    kpiEl.textContent = `${filtered.length} indivíduo${filtered.length !== 1 ? 's' : ''}`;
  }

  renderParticipantMasterList(filtered);
}

function renderParticipantMasterList(list) {
  const listContainer = document.getElementById('participant-master-list');
  if (!listContainer) return;

  if (list.length === 0) {
    listContainer.innerHTML = `
      <div style="padding:24px 12px; text-align:center; color:var(--ash); font-size:12px;">
        <i data-lucide="user-x" style="width:24px; height:24px; margin-bottom:6px; color:var(--stone);"></i>
        <div>Nenhum participante encontrado com os filtros atuais.</div>
      </div>
    `;
    if (window.lucide) window.lucide.createIcons();
    return;
  }

  listContainer.innerHTML = list.map(p => {
    const pId = p.person_id || p.chave_pessoa;
    const photo = p.photo_path || p.caminho_foto || '';
    const name = p.name || p.nome || 'Não identificado';
    const nick = p.nickname || p.alcunha || '';
    const doc = p.document || p.documento || '';
    const relintCount = p.linked_relints_count || p.quantidade_relints || 0;
    const isRecurrent = relintCount > 1;
    const isActive = (pId === currentSelectedPersonId);

    return `
      <div class="participant-item-card ${isActive ? 'active' : ''} ${isRecurrent ? 'glow-red' : ''}" onclick="selectParticipant('${escapeHtml(pId)}')">
        <div class="participant-avatar-thumb">
          ${photo ? `<img src="${escapeHtml(photo)}" alt="${escapeHtml(name)}" />` : `<i data-lucide="user" style="width:20px; height:20px; color:var(--ash);"></i>`}
        </div>

        <div class="participant-item-info">
          <div class="participant-item-name" title="${escapeHtml(name)}">${escapeHtml(name)}</div>
          ${nick ? `<div class="participant-item-nick">Vulgo: "${escapeHtml(nick)}"</div>` : ''}
          ${doc ? `<div class="participant-item-doc">doc: ${escapeHtml(doc)}</div>` : ''}
        </div>

        <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px; flex-shrink:0;">
          <span class="badge ${isRecurrent ? 'badge-red' : 'badge-emerald'}" style="font-size:10px; padding:2px 6px;">
            ${isRecurrent ? `🔴 ${relintCount}` : `🟢 1`}
          </span>
          ${p.photos && p.photos.length > 1 ? `<span style="font-size:10px; color:var(--accent-blue);"><i data-lucide="image" style="width:10px;height:10px;display:inline;"></i> ${p.photos.length}</span>` : ''}
        </div>
      </div>
    `;
  }).join('');

  if (window.lucide) window.lucide.createIcons();

  // Se nada foi selecionado ainda, auto-seleciona o primeiro participante da lista
  if (!currentSelectedPersonId && list.length > 0) {
    const firstId = list[0].person_id || list[0].chave_pessoa;
    selectParticipant(firstId);
  }
}

async function selectParticipant(personId) {
  currentSelectedPersonId = personId;

  // Atualiza classe .active nos itens da lista master
  document.querySelectorAll('.participant-item-card').forEach(card => {
    card.classList.remove('active');
  });

  const activeCard = document.querySelector(`.participant-item-card[onclick*="${personId}"]`);
  if (activeCard) activeCard.classList.add('active');

  const detailPane = document.getElementById('participant-detail-pane');
  if (!detailPane) return;

  detailPane.innerHTML = `
    <div style="height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; color:var(--ash); gap:10px;">
      <svg class="spin-fast" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--accent-blue)" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
      <div style="font-size:13px; font-weight:500;">Montando dossiê do participante...</div>
    </div>
  `;

  try {
    const res = await fetch(`/api/v1/participants/${personId}`);
    if (!res.ok) throw new Error('Não foi possível carregar o dossiê deste participante.');

    const dossier = await res.json();
    renderParticipantDossierView(dossier, detailPane);
  } catch (err) {
    detailPane.innerHTML = `
      <div class="card glow-red" style="padding:24px; color:var(--accent-red);">
        <strong>Erro ao carregar dossiê:</strong> ${escapeHtml(err.message)}
      </div>
    `;
  }
}

function renderParticipantDossierView(dossier, container) {
  const name = dossier.name || dossier.nome || 'Não identificado';
  const nick = dossier.nickname || dossier.alcunha || '';
  const doc = dossier.document || dossier.documento || '';
  const bg = dossier.background || dossier.antecedentes || '';
  const photos = dossier.photos || dossier.galeria_fotos || [];
  const mainPhoto = dossier.photo_path || dossier.caminho_foto || (photos[0] || '');
  const relints = dossier.linked_relints || [];

  container.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:20px; animation: fadeUp 0.25s ease-out both;">
      <!-- Top Header do Dossiê -->
      <div class="detail-header" style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0; padding-bottom:16px; border-bottom:1px solid var(--hairline); gap:16px;">
        <div style="display:flex; gap:16px; align-items:flex-start; flex:1; min-width:240px;">
          <!-- Foto Principal Avatar -->
          <div style="width:84px; height:84px; border-radius:10px; overflow:hidden; background:var(--canvas); border:1px solid var(--hairline-strong); flex-shrink:0; display:flex; align-items:center; justify-content:center; position:relative; group">
            ${mainPhoto ? `
              <img src="${escapeHtml(mainPhoto)}" alt="${escapeHtml(name)}" style="width:100%; height:100%; object-fit:cover; cursor:pointer;" onclick="openLightbox('${escapeHtml(mainPhoto)}', '${escapeHtml(name)}')" title="Clique para ampliar" />
            ` : `
              <i data-lucide="user" style="width:36px; height:36px; color:var(--ash);"></i>
            `}
          </div>

          <!-- Informações de Identificação -->
          <div style="flex:1;">
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:4px;">
              <h2 style="font-size:18px; font-weight:600; color:var(--ink); margin:0;">${escapeHtml(name)}</h2>
              ${relints.length > 1 ? `<span class="badge badge-red" style="font-size:11px; padding:3px 8px;">🔴 ${relints.length} Ocorrências</span>` : `<span class="badge badge-emerald" style="font-size:11px; padding:3px 8px;">🟢 1 Ocorrência</span>`}
            </div>

            <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-top:4px;">
              ${nick ? `<span class="badge badge-amber" style="font-size:12px; font-weight:500;">Vulgo: "${escapeHtml(nick)}"</span>` : ''}
              ${doc ? `<span style="font-size:12px; color:var(--ash); font-family:monospace; background:var(--canvas); padding:2px 8px; border-radius:4px; border:1px solid var(--hairline);">RG/CPF: ${escapeHtml(doc)}</span>` : ''}
            </div>

            ${bg ? `
              <div style="font-size:12px; color:var(--accent-red); margin-top:8px; background:rgba(255, 32, 71, 0.08); padding:6px 10px; border-radius:6px; border:1px solid rgba(255, 32, 71, 0.2);">
                <strong>Antecedentes:</strong> ${escapeHtml(bg)}
              </div>
            ` : ''}
          </div>
        </div>

        <!-- Ações Rápidas -->
        <div style="display:flex; gap:8px;">
          <button type="button" class="btn btn-secondary btn-sm" onclick="copyParticipantName('${escapeHtml(name)}')" title="Copiar Nome">
            <i data-lucide="copy" style="width:13px; height:13px;"></i> Copiar
          </button>
        </div>
      </div>

      <!-- Navegação por Sub-Abas do Dossiê -->
      <div class="detail-tabs-nav" style="display:flex; gap:8px; border-bottom:1px solid var(--hairline); padding-bottom:8px;">
        <button type="button" class="modal-tab-btn active" onclick="switchDossierTab(this, 'dossier-pane-relints')">
          <i data-lucide="file-text" style="width:14px; height:14px; display:inline;"></i> RELINTs Vinculados (${relints.length})
        </button>
        <button type="button" class="modal-tab-btn" onclick="switchDossierTab(this, 'dossier-pane-gallery')">
          <i data-lucide="image" style="width:14px; height:14px; display:inline;"></i> Galeria Cruzada (${photos.length})
        </button>
        <button type="button" class="modal-tab-btn" onclick="switchDossierTab(this, 'dossier-pane-info')">
          <i data-lucide="info" style="width:14px; height:14px; display:inline;"></i> Ficha Completa
        </button>
      </div>

      <!-- Conteúdo da Sub-Aba 1: Linha do Tempo de RELINTs -->
      <div id="dossier-pane-relints" class="modal-tab-pane active">
        <div style="display:flex; flex-direction:column; gap:10px;">
          ${relints.map(r => `
            <div class="card" style="padding:14px 18px; margin-bottom:0; background:var(--canvas); border:1px solid var(--hairline-strong); display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; transition:border-color 0.2s;" onmouseenter="this.style.borderColor='var(--accent-blue)'" onmouseleave="this.style.borderColor='var(--hairline-strong)'">
              <div style="flex:1; min-width:220px;">
                <div style="font-size:11px; color:var(--ash); margin-bottom:4px; display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                  ${r.date_of_fact ? `<span>📅 ${escapeHtml(r.date_of_fact)}</span>` : ''}
                  ${r.municipality ? `<span>📍 ${escapeHtml(r.municipality)}</span>` : ''}
                  <span class="badge ${getParticipationBadgeClass(r.participation_type)}" style="font-size:10px;">${escapeHtml(r.participation_type)}</span>
                </div>

                <div style="font-size:13.5px; font-weight:600; color:var(--ink); line-height:1.3; margin-bottom:4px;">
                  ${escapeHtml(r.subject)}
                </div>

                <div style="font-size:11px; color:var(--stone);">
                  Arquivo Origem: ${escapeHtml(r.source_file)}
                </div>
              </div>

              <div>
                <button type="button" class="btn btn-secondary btn-sm" onclick="navigateToRelintFromDossier('${r.relint_id}')">
                  <i data-lucide="file-search" style="width:13px; height:13px; display:inline;"></i> Abrir RELINT
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Conteúdo da Sub-Aba 2: Galeria Cruzada de Fotos -->
      <div id="dossier-pane-gallery" class="modal-tab-pane" style="display:none;">
        ${photos.length > 0 ? `
          <div class="gallery-grid" style="grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap:12px;">
            ${photos.map((pUrl, i) => `
              <div style="aspect-ratio:1; border-radius:8px; overflow:hidden; border:1px solid var(--hairline-strong); cursor:pointer; background:var(--canvas); position:relative;" onclick="openLightbox('${escapeHtml(pUrl)}', '${escapeHtml(name)} — Foto ${i+1}')">
                <img src="${escapeHtml(pUrl)}" alt="Foto ${i+1}" style="width:100%; height:100%; object-fit:cover; transition:transform 0.2s;" onmouseenter="this.style.transform='scale(1.05)'" onmouseleave="this.style.transform='scale(1)'" />
                <span style="position:absolute; bottom:4px; right:4px; font-size:9px; background:rgba(0,0,0,0.7); color:#fff; padding:1px 5px; border-radius:3px;">#${i+1}</span>
              </div>
            `).join('')}
          </div>
        ` : `
          <div style="text-align:center; padding:32px; color:var(--ash); font-size:13px; font-style:italic;">
            Nenhuma foto extraída vinculada a este participante.
          </div>
        `}
      </div>

      <!-- Conteúdo da Sub-Aba 3: Ficha Civil & Criminal -->
      <div id="dossier-pane-info" class="modal-tab-pane" style="display:none;">
        <div class="card" style="padding:20px; background:var(--canvas); margin-bottom:0;">
          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:16px;">
            <div>
              <div style="font-size:11px; color:var(--ash); text-transform:uppercase; font-weight:600; margin-bottom:2px;">Nome Completo</div>
              <div style="font-size:13px; color:var(--ink); font-weight:500;">${escapeHtml(name)}</div>
            </div>
            <div>
              <div style="font-size:11px; color:var(--ash); text-transform:uppercase; font-weight:600; margin-bottom:2px;">Alcunha / Vulgo</div>
              <div style="font-size:13px; color:var(--accent-amber); font-weight:500;">${nick ? escapeHtml(nick) : 'Nenhuma alcunha cadastrada'}</div>
            </div>
            <div>
              <div style="font-size:11px; color:var(--ash); text-transform:uppercase; font-weight:600; margin-bottom:2px;">RG / CPF</div>
              <div style="font-size:13px; color:var(--ink); font-family:monospace;">${doc ? escapeHtml(doc) : 'Não informado'}</div>
            </div>
            <div>
              <div style="font-size:11px; color:var(--ash); text-transform:uppercase; font-weight:600; margin-bottom:2px;">Reincidência</div>
              <div style="font-size:13px; color:var(--ink); font-weight:500;">${relints.length} RELINT(s) no sistema</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function switchDossierTab(btnEl, targetPaneId) {
  const container = btnEl.closest('.participant-detail-pane');
  if (!container) return;

  container.querySelectorAll('.detail-tabs-nav .modal-tab-btn').forEach(b => b.classList.remove('active'));
  container.querySelectorAll('.modal-tab-pane').forEach(p => {
    p.classList.remove('active');
    p.style.display = 'none';
  });

  btnEl.classList.add('active');
  const targetPane = container.querySelector('#' + targetPaneId);
  if (targetPane) {
    targetPane.classList.add('active');
    targetPane.style.display = 'block';
  }
}

function navigateToRelintFromDossier(relintId) {
  // Troca para a aba relints
  const navBtn = document.querySelector('.nav-item[data-tab="relints"]');
  if (navBtn) {
    navBtn.click();
    setTimeout(() => {
      if (typeof selectRelint === 'function') {
        selectRelint(relintId);
      }
    }, 150);
  }
}

function copyParticipantName(name) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(name).then(() => {
      if (typeof showToastNotification === 'function') {
        showToastNotification('📋 Nome Copiado', name);
      } else {
        alert('Nome copiado: ' + name);
      }
    });
  }
}

function getParticipationBadgeClass(type) {
  switch ((type || '').toLowerCase()) {
    case 'acusado':
    case 'suspeito':
      return 'badge-red';
    case 'vítima':
    case 'vitima':
      return 'badge-blue';
    case 'testemunha':
      return 'badge-emerald';
    default:
      return 'badge-muted';
  }
}
