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
