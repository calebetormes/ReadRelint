/**
 * Gallery View Controller & Global Lightbox Handler
 */

document.addEventListener('DOMContentLoaded', () => {
  // Listen for tab switch to gallery
  const galleryNavItem = document.querySelector('[data-tab="gallery"]');
  if (galleryNavItem) {
    galleryNavItem.addEventListener('click', loadGlobalGallery);
  }
});

async function loadGlobalGallery() {
  const container = document.getElementById('gallery-container');
  const badge = document.getElementById('gallery-count-badge');
  if (!container) return;

  container.innerHTML = `<div class="loading-state">Carregando galeria de fotos...</div>`;

  try {
    const res = await fetch('/api/v1/relints');
    if (!res.ok) throw new Error('Erro ao buscar relatórios');
    const relintsSummary = await res.json();

    // Fetch full details of all relints to gather images
    const detailPromises = relintsSummary.map(r => fetch(`/api/v1/relints/${r.id}`).then(res => res.json()).catch(() => null));
    const fullRelints = (await Promise.all(detailPromises)).filter(Boolean);

    let allImages = [];
    fullRelints.forEach(r => {
      if (r.images && Array.isArray(r.images)) {
        r.images.forEach(img => {
          allImages.push({
            path: img.path,
            caption: img.caption || r.subject || 'Foto do Fato',
            page: img.page || 1,
            relintId: r.id,
            sourceFile: r.source_file,
            subject: r.subject
          });
        });
      }
    });

    if (badge) badge.textContent = `${allImages.length} Imagens Extraídas`;

    if (allImages.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <p>Nenhuma foto ou anexo foi encontrado nos RELINTs cadastrados.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = allImages.map(img => `
      <div class="image-card" onclick="openLightbox('${escapeHtml(img.path)}', '${escapeHtml((img.caption ? img.caption + ' — ' : '') + img.sourceFile)}')">
        <div class="image-card-thumb-wrapper">
          <img src="${escapeHtml(img.path)}" alt="${escapeHtml(img.caption)}" class="image-card-thumb" onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'150\' viewBox=\'0 0 200 150\' fill=\'%231e293b\'><rect width=\'200\' height=\'150\' fill=\'%230f172a\'/><text x=\'50%25\' y=\'50%25\' dominant-baseline=\'middle\' text-anchor=\'middle\' fill=\'%2364748b\' font-size=\'14\'>Sem Imagem</text></svg>';" />
          <span class="image-card-badge">Pág ${img.page}</span>
        </div>
        <div class="image-card-caption">
          <div style="font-weight: 600; color: var(--accent-blue); margin-bottom: 2px;">${escapeHtml(img.sourceFile)}</div>
          <div>${escapeHtml(img.caption)}</div>
        </div>
      </div>
    `).join('');

  } catch (err) {
    container.innerHTML = `<div class="error-state" style="grid-column: 1 / -1;">Erro ao carregar galeria: ${err.message}</div>`;
  }
}

/**
 * Global Lightbox Modal Functions
 */
function openLightbox(src, caption) {
  const modal = document.getElementById('lightbox-modal');
  const imgEl = document.getElementById('lightbox-img');
  const captionEl = document.getElementById('lightbox-caption');

  if (!modal || !imgEl) return;

  imgEl.src = src;
  if (captionEl) captionEl.textContent = caption || '';
  modal.classList.add('active');
}

function closeLightbox(event) {
  const modal = document.getElementById('lightbox-modal');
  if (modal) {
    modal.classList.remove('active');
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
