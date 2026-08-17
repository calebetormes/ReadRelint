/**
 * ReadRelint Web Application Entry Point.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Handle SPA Tab Switching
  const navItems = document.querySelectorAll('.nav-item');
  const tabContents = document.querySelectorAll('.tab-content');
  const pageTitleElement = document.getElementById('page-title');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetTab = item.getAttribute('data-tab');

      // Update Nav active status
      navItems.forEach(nav => nav.classList.remove('active'));
      item.classList.add('active');

      // Update Tab Content visibility
      tabContents.forEach(content => {
        if (content.id === `tab-${targetTab}`) {
          content.classList.add('active');
        } else {
          content.classList.remove('active');
        }
      });

      // Update Page Title
      const tabTitle = item.querySelector('span')?.textContent || 'Dashboard';
      if (pageTitleElement) {
        pageTitleElement.textContent = tabTitle;
      }

      // Trigger view re-fetches if needed
      if (targetTab === 'crimes' && typeof fetchCrimesData === 'function') {
        fetchCrimesData();
      } else if (targetTab === 'monitoring' && typeof renderMonitoringView === 'function') {
        const container = document.getElementById('tab-monitoring');
        if (container) renderMonitoringView(container);
      }
    });
  });

  // Handle Collapsible Sidebar Toggle
  const sidebar = document.getElementById('sidebar');
  
  // Check saved state (default to collapsed)
  const savedState = localStorage.getItem('sidebar_collapsed');
  if (savedState === 'false') {
    sidebar?.classList.remove('collapsed');
  } else {
    sidebar?.classList.add('collapsed');
  }

  window.toggleSidebar = function() {
    const sb = document.getElementById('sidebar');
    if (!sb) return;
    sb.classList.toggle('collapsed');
    const isCollapsed = sb.classList.contains('collapsed');
    localStorage.setItem('sidebar_collapsed', isCollapsed ? 'true' : 'false');

    // Re-trigger layout/icons update
    if (window.lucide) window.lucide.createIcons();
  };

  document.getElementById('sidebar-toggle')?.addEventListener('click', (e) => {
    e.stopPropagation();
    window.toggleSidebar();
  });

  document.getElementById('top-sidebar-toggle')?.addEventListener('click', (e) => {
    e.stopPropagation();
    window.toggleSidebar();
  });

  // Check API Connection Status
  fetchApiStatus();
});

async function fetchApiStatus() {
  const statusBadge = document.getElementById('api-status-badge');
  try {
    const response = await fetch('/api/v1/health');
    if (response.ok) {
      const data = await response.json();
      if (statusBadge) {
        statusBadge.textContent = `API: ${data.status.toUpperCase()}`;
        statusBadge.className = 'badge badge-blue';
      }
    }
  } catch (error) {
    if (statusBadge) {
      statusBadge.textContent = 'API: OFFLINE';
      statusBadge.style.backgroundColor = 'rgba(239, 68, 68, 0.15)';
      statusBadge.style.color = '#ef4444';
    }
  }
}

/**
 * Global Lightbox Modal Handlers
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

/**
 * Formatação e Limpeza da Transcrição Integral do PDF.
 * Remove quebras de linha secas no meio de parágrafos mantendo parágrafos duplos (\n\n)
 * e linhas de cabeçalho (ex: DATA:, ASSUNTO:, RG:, NOME:).
 */
function formatTranscriptText(text) {
  if (!text) return 'Texto não disponível.';
  
  // 1. Uniformiza quebras de linha e remove espaços nas pontas de cada linha
  let clean = text.replace(/[ \t]*\r?\n[ \t]*/g, '\n');
  
  // 2. Preserva parágrafos duplos com um marcador temporário
  const MARKER = "___PARAGRAPH_BREAK___";
  clean = clean.replace(/\n{2,}/g, MARKER);
  
  // 3. Junta linhas de um mesmo parágrafo (desfazendo quebras secas do layout do PDF)
  const blocks = clean.split(MARKER);
  const cleanedBlocks = blocks.map(block => {
    const lines = block.split('\n').map(l => l.trim()).filter(Boolean);
    if (!lines.length) return '';
    
    const merged = [];
    lines.forEach(line => {
      if (!merged.length) {
        merged.push(line);
      } else {
        const last = merged[merged.length - 1];
        const isHeader = /^(?:[A-Z0-9_\-\.\s]{2,30}:|SUSPEITO|ANTECEDENTES|FOTO|REGISTRO|IMAGEM|ANEXOS|\-|\*|\d+[\.\)])/i.test(line);
        const lastColon = last.endsWith(':');
        
        if (isHeader || lastColon) {
          merged.push(line);
        } else {
          merged[merged.length - 1] = last + ' ' + line;
        }
      }
    });
    return merged.join('\n');
  });
  
  clean = cleanedBlocks.filter(Boolean).join('\n\n');
  
  // 4. Normaliza múltiplos espaços consecutivos e ajusta pontuações grudadas
  clean = clean.replace(/[ \t]{2,}/g, ' ');
  clean = clean.replace(/\s+([,\.\;:\?\!])/g, '$1');
  
  return clean;
}
