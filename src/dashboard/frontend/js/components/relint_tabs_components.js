/**
 * Shared RELINT Detail Tabs Component Library (DRY Architecture)
 */

window.RelintTabsComponents = {
  /**
   * 1. Render Synthesis Tab
   */
  renderSynthesisTab(report) {
    if (!report) return '';

    const summaryText = this.escapeHtml(report.summary || 'Nenhuma síntese gerada.');
    const dateText = this.escapeHtml(report.date_of_fact || 'N/I');
    const timeText = report.time_of_fact ? `às ${this.escapeHtml(report.time_of_fact)}` : '';
    const groupText = this.escapeHtml(report.bm_group || 'Ocorrência');
    const addressText = this.escapeHtml(report.address || report.municipality || 'Endereço não informado');
    const mapUrl = report.map_url ? this.escapeHtml(report.map_url) : '';
    const precisionLevel = report.precision_level || '';
    const precisionLabel = this.escapeHtml(report.precision_label || 'Sem Localização');

    return `
      <!-- Compact Fact Details -->
      <div class="dossier-section card" style="padding: 16px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; background: var(--canvas);">
        <div style="display:flex; flex-direction: column; gap: 8px;">
          <div style="display:flex; gap: 16px; align-items: center;">
            <div style="font-size: 13px; display: flex; align-items: center; gap: 6px;">
              <i data-lucide="calendar" style="width:14px;height:14px;color:var(--ash);"></i> 
              <strong>${dateText} ${timeText}</strong>
            </div>
            <div style="font-size: 13px; display: flex; align-items: center; gap: 6px;">
              <i data-lucide="shield" style="width:14px;height:14px;color:var(--ash);"></i> 
              <strong>${groupText}</strong>
            </div>
          </div>
          <div style="font-size: 13px; display: flex; align-items: center; gap: 6px; color: var(--ash);">
            <i data-lucide="map-pin" style="width:14px;height:14px;"></i> 
            ${addressText}
            <span title="Precisão da Localização" class="badge ${this.getPrecisionBadgeClass(precisionLevel)}" style="font-size: 10px; padding: 2px 6px; margin-left: 8px; display: inline-flex; align-items: center; gap: 4px;">
              ${this.getPrecisionIconHtml(precisionLevel)} ${precisionLabel}
            </span>
          </div>
        </div>
        
        ${mapUrl ? `
          <a href="${mapUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" style="display:inline-flex; align-items:center; gap:6px;">
            <i data-lucide="external-link" style="width:14px;height:14px;"></i> Abrir Mapa
          </a>
        ` : ''}
      </div>

      <!-- Highlighted Synthesis Card -->
      <div class="synthesis-card" style="border-left-color: var(--accent-red);">
        <h3 class="synthesis-title" style="color: var(--accent-red);"><i data-lucide="sparkles"></i> Síntese da Ocorrência</h3>
        <p class="synthesis-text">${summaryText}</p>
      </div>
    `;
  },

  /**
   * 2. Render Specialties Tab
   */
  renderSpecialtiesTab(report) {
    if (!report) return '';

    const groupName = this.escapeHtml(report.bm_group || 'Especialidade');
    let specHtml = '';

    if (report.bm_group === 'Homicídio' && report.homicide_details) {
      const h = report.homicide_details;
      specHtml = `
        <div><strong>Tipo do Fato:</strong> ${this.escapeHtml(h.fact_type || 'Não Informado')}</div>
        <div><strong>Motivação Presumida:</strong> ${this.escapeHtml(h.motivation || 'Não Informado')}</div>
        <div><strong>Registro Policial:</strong> ${this.escapeHtml(h.registry_number || 'N/A')} - ${this.escapeHtml(h.registry_agency || 'N/A')} (${this.escapeHtml(h.registry_year || 'N/A')})</div>
      `;
    } else if (report.bm_group === 'Prisão por Tráfico' && report.drug_trafficking_details) {
      const d = report.drug_trafficking_details;
      specHtml = `
        <div><strong>Quantidade de Drogas:</strong> ${this.escapeHtml(d.drug_quantity || 'Não Informada')}</div>
        <div><strong>Tipos de Drogas:</strong> ${this.escapeHtml(d.drug_types || 'Não Informados')}</div>
      `;
    } else if (report.bm_group === 'Roubo a Estabelecimento' && report.establishment_robbery_details) {
      const e = report.establishment_robbery_details;
      specHtml = `
        <div><strong>Tipo de Estabelecimento:</strong> ${this.escapeHtml(e.establishment_type || 'N/A')}</div>
        <div><strong>Tipo de Local:</strong> ${this.escapeHtml(e.location_type || 'N/A')}</div>
        <div><strong>Vítimas Lesionadas:</strong> ${this.escapeHtml(e.injured_victims || 0)}</div>
        <div><strong>Reféns:</strong> ${e.hostage_victim ? 'Sim' : 'Não'}</div>
      `;
    } else if (report.bm_group === 'Roubo a Residência' && report.residence_robbery_details) {
      const r = report.residence_robbery_details;
      specHtml = `
        <div><strong>Tipo de Local:</strong> ${this.escapeHtml(r.location_type || 'N/A')}</div>
        <div><strong>Vítimas Lesionadas:</strong> ${this.escapeHtml(r.injured_victims || 0)}</div>
        <div><strong>Reféns:</strong> ${r.hostage_victim ? 'Sim' : 'Não'}</div>
      `;
    } else if (report.bm_group === 'Roubo de Veículo' && report.vehicle_robbery_details) {
      const v = report.vehicle_robbery_details;
      specHtml = `
        <div><strong>Veículo (Modelo):</strong> ${this.escapeHtml(v.vehicle_model || 'N/A')}</div>
        <div><strong>Placa:</strong> ${this.escapeHtml(v.license_plate || 'N/A')}</div>
        <div><strong>Recuperado:</strong> ${v.recovered ? 'Sim' : 'Não'}</div>
        <div><strong>Local de Recuperação:</strong> ${this.escapeHtml(v.recovery_location || 'N/A')}</div>
      `;
    } else if (report.bm_group === 'Roubo a Pedestre' && report.pedestrian_robbery_details) {
      const p = report.pedestrian_robbery_details;
      specHtml = `
        <div><strong>Vítimas Lesionadas:</strong> ${this.escapeHtml(p.injured_victims || 0)}</div>
        <div><strong>Arma Utilizada:</strong> ${this.escapeHtml(p.weapon_used || 'N/A')}</div>
        <div><strong>Objeto Roubado:</strong> ${this.escapeHtml(p.stolen_object || 'N/A')}</div>
      `;
    } else if (report.bm_group === 'Furto de Veículo' && report.vehicle_theft_details) {
      const vt = report.vehicle_theft_details;
      specHtml = `
        <div><strong>Veículo (Modelo):</strong> ${this.escapeHtml(vt.vehicle_model || 'N/A')}</div>
        <div><strong>Placa:</strong> ${this.escapeHtml(vt.license_plate || 'N/A')}</div>
        <div><strong>Recuperado:</strong> ${vt.recovered ? 'Sim' : 'Não'}</div>
        <div><strong>Local de Recuperação:</strong> ${this.escapeHtml(vt.recovery_location || 'N/A')}</div>
      `;
    } else {
      specHtml = `<div>Nenhum detalhe adicional estruturado para esta ocorrência.</div>`;
    }

    return `
      <div class="dossier-section card" style="padding: 20px;">
        <h3 class="section-title" style="margin-top: 0; color: var(--accent-orange);">
          <i data-lucide="target"></i> Detalhes Específicos: ${groupName}
        </h3>
        <div class="grid-2" style="gap: 16px; font-size: 14px;">
          ${specHtml}
        </div>
      </div>
    `;
  },

  /**
   * 3. Render Photos Tab
   */
  renderPhotosTab(report) {
    if (!report) return '';

    const imagesList = report.images || report.imagens || [];
    const imgCount = imagesList.length;
    const subject = this.escapeHtml(report.subject || 'Foto do Fato');

    return `
      <div class="dossier-section card" style="padding: 20px;">
        <h3 class="section-title" style="margin-top: 0;"><i data-lucide="image"></i> Fotos &amp; Anexos do Fato (${imgCount})</h3>
        ${imgCount === 0 ? '<p class="text-muted" style="font-size: 0.9rem;">Nenhuma foto extraída deste RELINT.</p>' : `
          <div class="images-gallery-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px;">
            ${imagesList.map(img => `
              <div class="image-card" onclick="openLightbox('${this.escapeHtml(img.path)}', '${this.escapeHtml(img.caption || subject)}')" style="cursor: pointer;">
                <div class="image-card-thumb-wrapper" style="height: 140px; background: var(--canvas); overflow: hidden; border-radius: var(--r-sm);">
                  <img src="${this.escapeHtml(img.path)}" alt="${this.escapeHtml(img.caption || 'Foto do Fato')}" class="image-card-thumb" style="width:100%; height:100%; object-fit:cover;" onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'200\\' height=\\'150\\' viewBox=\\'0 0 200 150\\' fill=\\'%231e293b\\'><rect width=\\'200\\' height=\\'150\\' fill=\\'%230f172a\\'/><text x=\\'50%25\\' y=\\'50%25\\' dominant-baseline=\\'middle\\' text-anchor=\\'middle\\' fill=\\'%2364748b\\' font-size=\\'14\\'>Sem Imagem</text></svg>';" />
                </div>
                ${img.caption ? `<div class="image-card-caption" style="font-size: 11px; margin-top: 6px; color: var(--ash);">${this.escapeHtml(img.caption)}</div>` : ''}
              </div>
            `).join('')}
          </div>
        `}
      </div>
    `;
  },

  /**
   * 4. Render Location Tab
   */
  renderLocationTab(report) {
    if (!report) return '';

    const address = this.escapeHtml(report.address || 'Não informado');
    const municipality = report.municipality ? this.escapeHtml(report.municipality) : '';
    const neighborhood = report.neighborhood ? this.escapeHtml(report.neighborhood) : '';
    const coordinates = report.coordinates ? this.escapeHtml(report.coordinates) : '';
    const precisionLevel = report.precision_level || '';
    const precisionLabel = this.escapeHtml(report.precision_label || 'Sem Localização Exata');
    const mapUrl = report.map_url ? this.escapeHtml(report.map_url) : '';

    return `
      <div class="dossier-section card" style="padding: 24px;">
        <h3 class="section-title" style="margin-top: 0; margin-bottom: 20px;">
          <i data-lucide="map"></i> Informações Geográficas
        </h3>

        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 20px;">
          <div>
            <div style="font-size:15px;color:var(--ink);margin-bottom:12px;line-height:1.5;">
              <strong>Endereço Completo:</strong> ${address}
            </div>
            ${municipality ? `<div style="font-size:14px;color:var(--ash);margin-bottom:8px;"><strong>Município:</strong> ${municipality}</div>` : ''}
            ${neighborhood ? `<div style="font-size:14px;color:var(--ash);margin-bottom:8px;"><strong>Bairro:</strong> ${neighborhood}</div>` : ''}
            ${coordinates ? `<div class="geo-coords" style="margin-top:12px;font-size:14px;color:var(--ink);"><strong>Coordenadas GPS:</strong> <code class="geo-code" style="font-size:13px;padding:4px 8px;">${coordinates}</code></div>` : ''}
            
            <div style="margin-top:20px;">
              <span class="badge ${this.getPrecisionBadgeClass(precisionLevel)}">
                ${this.getPrecisionIconHtml(precisionLevel)} ${precisionLabel}
              </span>
            </div>
            
            ${mapUrl ? `
              <div class="geo-map-action" style="margin-top:24px;">
                <a href="${mapUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="display:inline-flex;align-items:center;gap:6px;">
                  <i data-lucide="external-link"></i> Abrir no Google Maps
                </a>
              </div>
            ` : ''}
          </div>
          
          <!-- Map Thumbnail -->
          ${coordinates ? `
            <div style="width: 350px; height: 250px; border-radius: var(--r-md); overflow: hidden; border: 1px solid var(--hairline); flex-shrink: 0; background: var(--canvas);">
              <iframe 
                width="100%" 
                height="100%" 
                frameborder="0" 
                scrolling="no" 
                marginheight="0" 
                marginwidth="0" 
                src="https://www.openstreetmap.org/export/embed.html?bbox=${coordinates.split(',')[1]?.trim() || ''},${coordinates.split(',')[0]?.trim() || ''},${coordinates.split(',')[1]?.trim() || ''},${coordinates.split(',')[0]?.trim() || ''}&layer=mapnik&marker=${coordinates.replace(/\s/g, '')}"
                style="border: none;">
              </iframe>
            </div>
          ` : `
            <div style="width: 350px; height: 250px; border-radius: var(--r-md); border: 1px dashed var(--ash); flex-shrink: 0; background: var(--canvas); display:flex; align-items:center; justify-content:center; flex-direction:column; color: var(--ash);">
              <i data-lucide="map-pin-off" style="width:48px;height:48px;margin-bottom:12px;"></i>
              <span style="font-size:13px;">Miniatura não disponível (Sem coordenadas)</span>
            </div>
          `}
        </div>
      </div>
    `;
  },

  /**
   * 5. Render Transcript Tab
   */
  renderTranscriptTab(report) {
    if (!report) return '';

    const content = report.content || '';
    const lineCount = content.split('\n').length;
    const charCount = content.length.toLocaleString('pt-BR');
    const formattedText = this.escapeHtml(this.formatTranscriptText(content));

    return `
      <div class="transcript-free-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div>
          <h3 class="section-title" style="margin-bottom:4px;border-bottom:none;padding-bottom:0;">
            <i data-lucide="file-text"></i> Transcrição Literal Completa (PDF)
          </h3>
          <div style="font-size:12px;color:var(--ash);margin-top:2px;">
            ${lineCount} linhas • ${charCount} caracteres
          </div>
        </div>

        <button type="button" class="btn btn-secondary btn-sm" onclick="RelintTabsComponents.copyTranscriptText('transcript-raw-text')">
          <i data-lucide="copy" style="width:13px;height:13px;display:inline;"></i> Copiar Texto Completo
        </button>
      </div>

      <div class="transcript-free-content" id="transcript-raw-text" style="background: var(--canvas); padding: 16px; border-radius: var(--r-md); border: 1px solid var(--hairline); font-family: var(--font-mono, monospace); font-size: 12px; white-space: pre-wrap; word-break: break-word; max-height: 500px; overflow-y: auto;">${formattedText}</div>
    `;
  },

  // Helper Utilities
  getPrecisionBadgeClass(level) {
    switch (level) {
      case 'exact_coords': return 'badge-emerald';
      case 'direct_link': return 'badge-blue';
      case 'address_inferred':
      case 'low_precision': return 'badge-amber';
      default: return 'badge-muted';
    }
  },

  getPrecisionIconHtml(level) {
    switch (level) {
      case 'exact_coords': return '<i data-lucide="crosshair" style="width:12px;height:12px;display:inline;"></i>';
      case 'direct_link': return '<i data-lucide="link" style="width:12px;height:12px;display:inline;"></i>';
      case 'address_inferred':
      case 'low_precision': return '<i data-lucide="search" style="width:12px;height:12px;display:inline;"></i>';
      default: return '<i data-lucide="map-pin-off" style="width:12px;height:12px;display:inline;"></i>';
    }
  },

  formatTranscriptText(txt) {
    if (!txt) return '';
    return txt;
  },

  copyTranscriptText(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const text = el.innerText || el.textContent;
    navigator.clipboard.writeText(text).then(() => {
      alert('Transcrição literal copiada para a área de transferência!');
    }).catch(err => {
      console.error('Falha ao copiar:', err);
    });
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
