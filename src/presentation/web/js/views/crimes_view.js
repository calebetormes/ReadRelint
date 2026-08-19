/**
 * Crimes & Statistics Dashboard View Renderer (Resend Design System)
 */

document.addEventListener('DOMContentLoaded', () => {
  initCrimesView();
});

function initCrimesView() {
  const container = document.getElementById('tab-crimes');
  if (!container) return;

  // Render Dashboard Layout Shell
  container.innerHTML = `
    <!-- Top KPI Cards Grid -->
    <div class="grid-4" style="margin-bottom: 24px;">
      <div class="card glow-blue" style="padding: 20px; margin-bottom: 0;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
          <span class="meta-label">Total de RELINTs</span>
          <i data-lucide="file-text" style="color: var(--accent-blue); width: 18px; height: 18px;"></i>
        </div>
        <div id="kpi-total-relints" style="font-size: 28px; font-weight: 600; color: var(--ink);">--</div>
        <div style="font-size: 12px; color: var(--ash); margin-top: 4px;">Ocorrências cadastradas</div>
      </div>

      <div class="card glow-red" style="padding: 20px; margin-bottom: 0;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
          <span class="meta-label">Homicídios / Fatais</span>
          <i data-lucide="crosshair" style="color: var(--accent-red); width: 18px; height: 18px;"></i>
        </div>
        <div id="kpi-homicides" style="font-size: 28px; font-weight: 600; color: var(--accent-red);">--</div>
        <div style="font-size: 12px; color: var(--ash); margin-top: 4px;">Homicídios & Latrocínios</div>
      </div>

      <div class="card glow-green" style="padding: 20px; margin-bottom: 0;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
          <span class="meta-label">Prisões por Tráfico</span>
          <i data-lucide="shield-check" style="color: var(--accent-green); width: 18px; height: 18px;"></i>
        </div>
        <div id="kpi-trafficking" style="font-size: 28px; font-weight: 600; color: var(--accent-green);">--</div>
        <div style="font-size: 12px; color: var(--ash); margin-top: 4px;">Apreensões & Tráfico</div>
      </div>

      <div class="card glow-orange" style="padding: 20px; margin-bottom: 0;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
          <span class="meta-label">Top Município</span>
          <i data-lucide="map-pin" style="color: var(--accent-orange); width: 18px; height: 18px;"></i>
        </div>
        <div id="kpi-top-muni" style="font-size: 20px; font-weight: 600; color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">--</div>
        <div id="kpi-top-muni-count" style="font-size: 12px; color: var(--ash); margin-top: 4px;">Maior mancha criminal</div>
      </div>
    </div>

    <!-- Charts Section: 2 Columns Grid -->
    <div class="grid-2" style="margin-bottom: 24px;">
      <!-- Chart 1: Donut Distribution of BM Groups -->
      <div class="card" style="padding: 24px; margin-bottom: 0;">
        <div class="card-title">
          <i data-lucide="pie-chart" style="color: var(--accent-blue); width: 16px; height: 16px;"></i>
          Distribuição por Grupo BM
        </div>
        <div id="chart-bm-distribution" style="min-height: 280px; display: flex; align-items: center; justify-content: center;">
          <div class="loading-state">Carregando estatísticas...</div>
        </div>
      </div>

      <!-- Chart 2: Incidents Timeline -->
      <div class="card" style="padding: 24px; margin-bottom: 0;">
        <div class="card-title">
          <i data-lucide="trending-up" style="color: var(--accent-green); width: 16px; height: 16px;"></i>
          Linha do Tempo das Ocorrências
        </div>
        <div id="chart-timeline" style="min-height: 280px; display: flex; align-items: center; justify-content: center;">
          <div class="loading-state">Carregando linha do tempo...</div>
        </div>
      </div>
    </div>

    <!-- Recent Incidents Feed -->
    <div class="card" style="padding: 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div class="card-title" style="margin-bottom: 0;">
          <i data-lucide="clock" style="color: var(--accent-orange); width: 16px; height: 16px;"></i>
          Últimas Ocorrências Analisadas
        </div>
        <span class="badge badge-muted" id="recent-count-badge">-- Ocorrências</span>
      </div>

      <div id="recent-incidents-list" style="display: flex; flex-direction: column; gap: 8px;">
        <div class="loading-state">Carregando feed de ocorrências...</div>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
  fetchCrimesData();
}

let bmChartInstance = null;
let timelineChartInstance = null;

async function fetchCrimesData() {
  try {
    const res = await fetch('/api/v1/relints');
    if (!res.ok) throw new Error('Falha ao carregar relatórios para o dashboard');
    const relints = await res.json();

    updateKPIs(relints);
    renderBMDistributionChart(relints);
    renderTimelineChart(relints);
    renderRecentIncidentsFeed(relints);
  } catch (err) {
    console.error(err);
  }
}

function updateKPIs(relints) {
  const total = relints.length;
  let homicides = 0;
  let trafficking = 0;
  const muniCounts = {};

  relints.forEach(r => {
    const bm = (r.bm_group || r.grupo_bm || '').toLowerCase();
    if (bm.includes('homicíd') || bm.includes('homicid')) homicides++;
    if (bm.includes('tráfico') || bm.includes('trafico')) trafficking++;

    const muni = r.municipality || r.municipio || 'Não Informado';
    if (muni !== 'Não Informado' && muni !== 'N/I' && muni.trim() !== '') {
      muniCounts[muni] = (muniCounts[muni] || 0) + 1;
    }
  });

  // Top municipality
  let topMuni = 'N/I';
  let topCount = 0;
  Object.entries(muniCounts).forEach(([muni, count]) => {
    if (count > topCount) {
      topCount = count;
      topMuni = muni;
    }
  });

  document.getElementById('kpi-total-relints').textContent = total;
  document.getElementById('kpi-homicides').textContent = homicides;
  document.getElementById('kpi-trafficking').textContent = trafficking;
  document.getElementById('kpi-top-muni').textContent = topMuni;
  document.getElementById('kpi-top-muni-count').textContent = topCount ? `${topCount} ocorrência(s)` : 'Sem registro';
}

function renderBMDistributionChart(relints) {
  const container = document.getElementById('chart-bm-distribution');
  if (!container) return;

  const counts = {};
  relints.forEach(r => {
    const bm = r.bm_group || r.grupo_bm || 'Outros';
    counts[bm] = (counts[bm] || 0) + 1;
  });

  const labels = Object.keys(counts);
  const series = Object.values(counts);

  if (labels.length === 0) {
    container.innerHTML = '<div class="empty-state"><p>Sem dados suficientes</p></div>';
    return;
  }

  container.innerHTML = '';

  const options = {
    chart: {
      type: 'donut',
      height: 280,
      background: 'transparent',
      foreColor: '#a1a4a5',
      toolbar: { show: false }
    },
    series: series,
    labels: labels,
    colors: ['#ff801f', '#ff2047', '#11ff99', '#3b9eff', '#ffc53d', '#a78bfa', '#888e90'],
    stroke: {
      show: true,
      colors: ['#0a0a0c'],
      width: 2
    },
    dataLabels: {
      enabled: false
    },
    legend: {
      position: 'bottom',
      fontSize: '12px',
      fontFamily: 'Inter, sans-serif',
      labels: {
        colors: '#fcfdff'
      },
      markers: {
        radius: 4
      }
    },
    tooltip: {
      theme: 'dark',
      style: {
        fontSize: '12px',
        fontFamily: 'Inter, sans-serif'
      }
    },
    plotOptions: {
      pie: {
        donut: {
          size: '70%',
          labels: {
            show: true,
            total: {
              show: true,
              label: 'Total',
              color: '#a1a4a5',
              formatter: () => series.reduce((a, b) => a + b, 0)
            },
            value: {
              color: '#fcfdff',
              fontSize: '22px',
              fontWeight: 600
            }
          }
        }
      }
    }
  };

  if (bmChartInstance) bmChartInstance.destroy();
  if (typeof ApexCharts !== 'undefined') {
    bmChartInstance = new ApexCharts(container, options);
    bmChartInstance.render();
  }
}

function renderTimelineChart(relints) {
  const container = document.getElementById('chart-timeline');
  if (!container) return;

  const dateCounts = {};
  relints.forEach(r => {
    const date = r.date_of_fact || r.data_fato || 'Indefinido';
    if (date !== 'Indefinido' && date.trim() !== '') {
      dateCounts[date] = (dateCounts[date] || 0) + 1;
    }
  });

  // Sort dates
  const sortedDates = Object.keys(dateCounts).sort();
  const seriesData = sortedDates.map(d => dateCounts[d]);

  if (sortedDates.length === 0) {
    container.innerHTML = '<div class="empty-state"><p>Sem datas registradas</p></div>';
    return;
  }

  container.innerHTML = '';

  const options = {
    chart: {
      type: 'area',
      height: 280,
      background: 'transparent',
      foreColor: '#a1a4a5',
      toolbar: { show: false }
    },
    series: [{
      name: 'Ocorrências',
      data: seriesData
    }],
    xaxis: {
      categories: sortedDates,
      labels: {
        style: { colors: '#888e90', fontSize: '11px' }
      },
      axisBorder: { color: 'rgba(255,255,255,0.06)' },
      axisTicks: { color: 'rgba(255,255,255,0.06)' }
    },
    yaxis: {
      labels: {
        style: { colors: '#888e90', fontSize: '11px' }
      }
    },
    colors: ['#11ff99'],
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.35,
        opacityTo: 0.02,
        stops: [0, 90, 100]
      }
    },
    stroke: {
      curve: 'smooth',
      width: 2
    },
    grid: {
      borderColor: 'rgba(255,255,255,0.06)',
      strokeDashArray: 4
    },
    tooltip: {
      theme: 'dark'
    }
  };

  if (timelineChartInstance) timelineChartInstance.destroy();
  if (typeof ApexCharts !== 'undefined') {
    timelineChartInstance = new ApexCharts(container, options);
    timelineChartInstance.render();
  }
}

function renderRecentIncidentsFeed(relints) {
  const container = document.getElementById('recent-incidents-list');
  const badge = document.getElementById('recent-count-badge');
  if (!container) return;

  if (badge) badge.textContent = `${relints.length} Ocorrências`;

  if (relints.length === 0) {
    container.innerHTML = '<div class="empty-state"><p>Nenhuma ocorrência registrada.</p></div>';
    return;
  }

  // Sort descending by ID to ensure latest read are at top
  const sorted = [...relints].sort((a, b) => (Number(b.id) || 0) - (Number(a.id) || 0));
  const recent = sorted.slice(0, 6);

  container.innerHTML = recent.map(r => {
    const bmVal = r.bm_group || r.grupo_bm || '';
    const isHomicide = bmVal.toLowerCase().includes('homicíd') || bmVal.toLowerCase().includes('homicid');
    const badgeClass = isHomicide ? 'badge-rose' : 'badge-amber';
    const subj = r.subject || r.assunto || r.source_file || r.arquivo_origem || 'Sem Assunto';
    const muni = r.municipality || r.municipio || 'Local Indefinido';
    const dateVal = r.date_of_fact || r.data_fato || 'Data Indefinida';

    return `
      <div class="card" style="padding: 14px 18px; margin-bottom: 0; display: flex; justify-content: space-between; align-items: center; background-color: var(--surface-card); border-color: var(--hairline-strong);">
        <div style="display: flex; align-items: center; gap: 14px;">
          <div style="width: 36px; height: 36px; border-radius: var(--r-md); background-color: var(--surface-elevated); border: 1px solid var(--hairline-strong); display: flex; align-items: center; justify-content: center; color: var(--ink);">
            <i data-lucide="${isHomicide ? 'crosshair' : 'file-text'}" style="width: 18px; height: 18px;"></i>
          </div>
          <div>
            <div style="font-weight: 500; font-size: 14px; color: var(--ink);">${escapeHtml(subj)}</div>
            <div style="font-size: 12px; color: var(--ash); margin-top: 2px;">
              <i data-lucide="map-pin" style="width: 12px; height: 12px; display: inline; vertical-align: middle;"></i> ${escapeHtml(muni)} &bull; ${escapeHtml(dateVal)}
            </div>
          </div>
        </div>

        <div style="display: flex; align-items: center; gap: 12px;">
          <span class="badge ${badgeClass}">${escapeHtml(bmVal || 'Outros')}</span>
        </div>
      </div>
    `;
  }).join('');

  if (window.lucide) window.lucide.createIcons();
}
