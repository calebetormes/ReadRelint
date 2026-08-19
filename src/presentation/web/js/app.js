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
      } else if (targetTab === 'participants' && typeof fetchParticipants === 'function') {
        fetchParticipants();
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

  // Handle Mobile Menu Drawer Toggle
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const sidebarOverlay = document.getElementById('sidebar-overlay');

  function openMobileMenu() {
    sidebar?.classList.add('mobile-open');
    sidebarOverlay?.classList.add('active');
  }

  function closeMobileMenu() {
    sidebar?.classList.remove('mobile-open');
    sidebarOverlay?.classList.remove('active');
  }

  mobileMenuBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    if (sidebar?.classList.contains('mobile-open')) {
      closeMobileMenu();
    } else {
      openMobileMenu();
    }
  });

  sidebarOverlay?.addEventListener('click', closeMobileMenu);

  // Close mobile drawer upon selecting any nav item
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      closeMobileMenu();
    });
  });

  document.getElementById('sidebar-toggle')?.addEventListener('click', (e) => {
    e.stopPropagation();
    window.toggleSidebar();
  });

  // Check API Connection Status
  fetchApiStatus();

  // Initialize Real-time SSE listener
  initRealtimeEvents();
});

/**
 * Inicialização do Listener SSE para Reatividade em Tempo Real
 */
function initRealtimeEvents() {
  if (typeof window.EventSource === 'undefined') return;

  const eventSource = new EventSource('/api/v1/events');

  eventSource.addEventListener('connected', (e) => {
    console.log('⚡ Conexão SSE em tempo real estabelecida com a API ReadRelint.');
  });

  eventSource.addEventListener('relint_created', (e) => {
    try {
      const data = JSON.parse(e.data);
      console.log('⚡ Novo RELINT processado:', data);
      showToastNotification('⚡ Novo RELINT Processado', data.subject || data.source_file || 'Nova ocorrência cadastrada');
      refreshActiveView();
    } catch (err) {
      console.error('Erro ao processar evento relint_created:', err);
    }
  });

  eventSource.addEventListener('relint_updated', (e) => {
    try {
      const data = JSON.parse(e.data);
      console.log('⚡ RELINT atualizado:', data);
      showToastNotification('📝 RELINT Atualizado', data.subject || 'Ocorrência revisada');
      refreshActiveView();
    } catch (err) {
      console.error('Erro ao processar evento relint_updated:', err);
    }
  });

  eventSource.onerror = () => {
    console.warn('Conexão SSE suspensa temporariamente. Aguardando reconexão automática...');
  };
}

function refreshActiveView() {
  const activeTabContent = document.querySelector('.tab-content.active');
  if (!activeTabContent) return;

  const tabId = activeTabContent.id;
  if (tabId === 'tab-crimes' && typeof fetchCrimesData === 'function') {
    fetchCrimesData();
  } else if (tabId === 'tab-relints' && typeof fetchRelintsList === 'function') {
    fetchRelintsList();
  } else if (tabId === 'tab-homicides' && typeof fetchHomicides === 'function') {
    fetchHomicides();
  } else if (tabId === 'tab-participants' && typeof fetchParticipants === 'function') {
    fetchParticipants();
  } else if (tabId === 'tab-gallery' && typeof loadGlobalGallery === 'function') {
    loadGlobalGallery();
  }
}

function showToastNotification(title, message) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:10px;pointer-events:none;';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.style.cssText = 'padding:14px 18px;background:#0d1520;border:1px solid #10b981;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,0.5);color:#fcfdff;font-family:Inter,sans-serif;min-width:280px;max-width:380px;pointer-events:auto;transition:all 0.3s ease;';

  toast.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
      <span style="font-weight:600;font-size:13px;color:#10b981;display:flex;align-items:center;gap:6px;">
        ${escapeHtml(title)}
      </span>
      <span style="font-size:11px;color:#64748b;">agora</span>
    </div>
    <div style="font-size:12.5px;color:#e2e8f0;line-height:1.35;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">
      ${escapeHtml(message)}
    </div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

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

  // 1b. Trata casos onde o cabeçalho 'ANEXOS: XXX' está grudado na mesma linha com o texto narrativo ou com divisórias '____'
  const patternInline = /\b(ANEXOS?\s*:\s*(?:XXX|NENHUMA?|NADA|\-|\d+|[A-Z0-9_\-\.]{1,20}))(?:\s*_{3,})?\s+(?=[A-Z\d\"][a-z\u00C0-\u00FF]|\bEm\b|\bNo\b|\bNa\b|\bConforme\b|\bSegundo\b|\bAo\b|\bUm\b|\bUma\b)/gi;
  clean = clean.replace(patternInline, '$1\n\n');
  
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
        const lastIsAnexos = /^ANEXOS?\s*:/i.test(last);
        
        if (isHeader || lastColon || lastIsAnexos) {
          merged.push(line);
        } else {
          merged[merged.length - 1] = last + ' ' + line;
        }
      }
    });
    return merged.join('\n');
  });
  
  clean = cleanedBlocks.filter(Boolean).join('\n\n');
  
  // 4. Garante que após a linha de ANEXOS: haja uma linha em branco (\n\n) separando o cabeçalho do texto
  clean = clean.replace(/((?:ANEXOS?\s*:[^\n]*))(\n+)(?=[^\s\n])/gi, '$1\n\n');

  // 5. Normaliza múltiplos espaços consecutivos e ajusta pontuações grudadas
  clean = clean.replace(/[ \t]{2,}/g, ' ');
  clean = clean.replace(/\s+([,\.\;:\?\!])/g, '$1');
  
  return clean;
}
