/**
 * Reusable Participants Tab Component (40% / 60% Master-Detail Layout)
 */

window.ParticipantsTabComponent = {
  // Active state per report container
  state: {},

  /**
   * Render the complete Master-Detail layout into a target container element ID
   */
  render(containerId, participants = [], images = [], reportId = '') {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Store state for this view
    this.state[containerId] = {
      participants: participants || [],
      images: images || [],
      reportId: reportId,
      selectedIndex: (participants && participants.length > 0) ? 0 : -1,
      searchTerm: ''
    };

    this.updateView(containerId);
  },

  /**
   * Update the internal HTML of the container
   */
  updateView(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const st = this.state[containerId];
    if (!st) return;

    const { participants, images, selectedIndex, searchTerm } = st;

    if (!participants || participants.length === 0) {
      container.innerHTML = `
        <div class="dossier-section card" style="padding: 32px; text-align: center;">
          <i data-lucide="users-round" style="width: 48px; height: 48px; color: var(--ash); margin-bottom: 12px;"></i>
          <h4 style="margin: 0; font-weight: 500; color: var(--ink);">Nenhum participante registrado</h4>
          <p class="text-muted" style="margin-top: 6px; font-size: 13px;">Não foram identificados envolvidos ou vítimas neste relatório de inteligência.</p>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    // Filter participants based on search
    const filtered = participants.map((p, idx) => ({ ...p, originalIndex: idx })).filter(p => {
      if (!searchTerm) return true;
      const term = searchTerm.toLowerCase();
      return (p.name || '').toLowerCase().includes(term) ||
             (p.nickname || '').toLowerCase().includes(term) ||
             (p.document || '').toLowerCase().includes(term) ||
             (p.participation_type || '').toLowerCase().includes(term);
    });

    const selectedPart = selectedIndex >= 0 && selectedIndex < participants.length ? participants[selectedIndex] : null;

    container.innerHTML = `
      <div class="participants-master-detail" style="display: flex; gap: 16px; min-height: 480px; align-items: stretch;">
        
        <!-- Left Sidebar: 40% Width Participant List -->
        <div class="participants-list-pane card" style="flex: 0 0 40%; width: 40%; padding: 16px; display: flex; flex-direction: column; gap: 12px; max-height: 620px; overflow-y: auto;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <h4 style="margin: 0; font-size: 14px; font-weight: 600; color: var(--ink); display: flex; align-items: center; gap: 6px;">
              <i data-lucide="users" style="width: 16px; height: 16px; color: var(--accent-orange);"></i> 
              Envolvidos (${participants.length})
            </h4>
          </div>

          <!-- Search Input -->
          <div style="position: relative;">
            <input 
              type="text" 
              class="form-control" 
              placeholder="Buscar envolvido por nome, vulgo..." 
              value="${this.escapeHtml(searchTerm)}"
              oninput="ParticipantsTabComponent.onSearch('${containerId}', this.value)"
              style="padding-left: 32px; font-size: 12px; height: 32px;"
            />
            <i data-lucide="search" style="position: absolute; left: 10px; top: 8px; width: 14px; height: 14px; color: var(--ash);"></i>
          </div>

          <!-- Participant Cards List -->
          <div style="display: flex; flex-direction: column; gap: 8px; flex: 1; overflow-y: auto;">
            ${filtered.length === 0 ? `
              <div style="padding: 16px; text-align: center; color: var(--ash); font-size: 12px;">
                Nenhum envolvido encontrado para "${this.escapeHtml(searchTerm)}".
              </div>
            ` : filtered.map(p => {
              const isSelected = p.originalIndex === selectedIndex;
              const badgeClass = this.getBadgeClass(p.participation_type);
              
              return `
                <div 
                  class="participant-item-card ${isSelected ? 'active' : ''}" 
                  onclick="ParticipantsTabComponent.selectParticipant('${containerId}', ${p.originalIndex})"
                  style="
                    padding: 10px 12px; 
                    border-radius: var(--r-md); 
                    border: 1px solid ${isSelected ? 'var(--accent-orange)' : 'var(--hairline)'}; 
                    background: ${isSelected ? 'var(--surface-elevated)' : 'var(--canvas)'}; 
                    cursor: pointer;
                    transition: all 0.15s ease;
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                  "
                >
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
                    <span style="font-size: 13.5px; font-weight: ${isSelected ? '600' : '500'}; color: var(--ink); line-height: 1.3;">
                      ${this.escapeHtml(p.name)}
                    </span>
                    <span class="badge ${badgeClass}" style="font-size: 10px; padding: 2px 6px; flex-shrink: 0;">
                      ${this.escapeHtml(p.participation_type || 'Envolvido')}
                    </span>
                  </div>

                  ${p.nickname ? `
                    <div style="font-size: 11.5px; color: var(--accent-orange); font-weight: 500;">
                      Vulgo: <strong>${this.escapeHtml(p.nickname)}</strong>
                    </div>
                  ` : ''}

                  ${p.document ? `
                    <div style="font-size: 11px; color: var(--ash);">
                      Doc: ${this.escapeHtml(p.document)}
                    </div>
                  ` : ''}
                </div>
              `;
            }).join('')}
          </div>
        </div>

        <!-- Right Main Panel: 60% Width Participant Dossier -->
        <div class="participant-dossier-pane card" style="flex: 1; width: 60%; padding: 20px; display: flex; flex-direction: column; gap: 16px; max-height: 620px; overflow-y: auto;">
          ${selectedPart ? this.renderDossierContent(selectedPart, images) : `
            <div style="display: flex; height: 100%; align-items: center; justify-content: center; flex-direction: column; color: var(--ash);">
              <i data-lucide="user-check" style="width: 40px; height: 40px; margin-bottom: 8px;"></i>
              <span style="font-size: 13px;">Selecione um participante na lista ao lado para ver seu dossiê.</span>
            </div>
          `}
        </div>

      </div>
    `;

    if (window.lucide) window.lucide.createIcons();
  },

  /**
   * Render the right detail pane (60% Dossier)
   */
  renderDossierContent(p, images) {
    const badgeClass = this.getBadgeClass(p.participation_type);
    const initials = (p.name || 'P').split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();

    // Linked photos for this participant
    const linkedPhotos = (images || []).filter(img => 
      img.caption && img.caption.toLowerCase().includes((p.name || '').toLowerCase())
    );

    return `
      <!-- Dossier Header -->
      <div style="display: flex; align-items: center; gap: 16px; padding-bottom: 16px; border-bottom: 1px solid var(--hairline);">
        <div style="width: 52px; height: 52px; border-radius: 50%; background: var(--surface-elevated); border: 2px solid var(--hairline-strong); display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; color: var(--accent-orange); flex-shrink: 0;">
          ${initials}
        </div>
        
        <div style="flex: 1;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <h3 style="margin: 0; font-size: 17px; font-weight: 600; color: var(--ink);">${this.escapeHtml(p.name)}</h3>
            <span class="badge ${badgeClass}">${this.escapeHtml(p.participation_type || 'Acusado')}</span>
          </div>
          ${p.nickname ? `
            <div style="font-size: 13px; color: var(--accent-orange); margin-top: 2px; font-weight: 500;">
              Alcunha / Vulgo: <strong>"${this.escapeHtml(p.nickname)}"</strong>
            </div>
          ` : ''}
        </div>
      </div>

      <!-- Dossier Information Grid -->
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; background: var(--canvas); padding: 14px; border-radius: var(--r-md); border: 1px solid var(--hairline);">
        <div>
          <span style="font-size: 11px; color: var(--ash); text-transform: uppercase; display: block; margin-bottom: 2px;">Documento / Registro</span>
          <span style="font-size: 13.5px; font-weight: 500; color: var(--ink);">${this.escapeHtml(p.document || 'Não Informado')}</span>
        </div>

        <div>
          <span style="font-size: 11px; color: var(--ash); text-transform: uppercase; display: block; margin-bottom: 2px;">Enquadramento / Tipo</span>
          <span style="font-size: 13.5px; font-weight: 500; color: var(--ink);">${this.escapeHtml(p.participation_type || 'Investigado')}</span>
        </div>
      </div>

      <!-- Background / Details Block -->
      <div style="display: flex; flex-direction: column; gap: 6px;">
        <h4 style="margin: 0; font-size: 13px; font-weight: 600; color: var(--ink); display: flex; align-items: center; gap: 6px;">
          <i data-lucide="file-text" style="width: 14px; height: 14px; color: var(--ash);"></i>
          Histórico e Contexto no Fato
        </h4>
        <div style="font-size: 13px; color: var(--ink); line-height: 1.5; background: var(--canvas); padding: 12px; border-radius: var(--r-md); border: 1px solid var(--hairline); min-height: 60px;">
          ${p.background ? this.escapeHtml(p.background) : '<span style="color: var(--ash); font-style: italic;">Nenhum detalhe adicional de histórico registrado para esta pessoa.</span>'}
        </div>
      </div>

      <!-- Photos & Attachments section for Participant -->
      <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 4px;">
        <h4 style="margin: 0; font-size: 13px; font-weight: 600; color: var(--ink); display: flex; align-items: center; gap: 6px;">
          <i data-lucide="image" style="width: 14px; height: 14px; color: var(--ash);"></i>
          Fotos Relacionadas do Fato (${linkedPhotos.length})
        </h4>

        ${linkedPhotos.length > 0 ? `
          <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 8px;">
            ${linkedPhotos.map(img => `
              <div 
                class="image-card" 
                onclick="openLightbox('${this.escapeHtml(img.path)}', '${this.escapeHtml(img.caption || p.name)}')"
                style="cursor: pointer;"
              >
                <img src="${this.escapeHtml(img.path)}" alt="Foto" style="width: 100%; height: 80px; object-fit: cover; border-radius: var(--r-sm);" />
              </div>
            `).join('')}
          </div>
        ` : `
          <div style="font-size: 12px; color: var(--ash); background: var(--canvas); padding: 10px; border-radius: var(--r-sm); border: 1px dashed var(--hairline); text-align: center;">
            Nenhuma foto vinculada diretamente pelo nome.
          </div>
        `}
      </div>
    `;
  },

  selectParticipant(containerId, index) {
    if (this.state[containerId]) {
      this.state[containerId].selectedIndex = index;
      this.updateView(containerId);
    }
  },

  onSearch(containerId, val) {
    if (this.state[containerId]) {
      this.state[containerId].searchTerm = val;
      this.updateView(containerId);
    }
  },

  getBadgeClass(type) {
    if (!type) return 'badge-muted';
    const t = type.toLowerCase();
    if (t.includes('vítima') || t.includes('vitima')) return 'badge-emerald';
    if (t.includes('autor') || t.includes('acusado') || t.includes('suspeito') || t.includes('preso')) return 'badge-rose';
    return 'badge-blue';
  },

  escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
};
