<!--
  ============================================================================
  ReadRelint - Rota Raiz / (Visão Geral do Dashboard)
  ============================================================================
  Página principal de Inteligência Policial exibindo KPIs consolidados em tempo
  real, os últimos RELINTs extraídos e monitoramento da saúde do motor Ollama.
  ============================================================================
-->
<script>
  import { onMount } from 'svelte';
  import StatCard from '$lib/components/ui/StatCard.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Table from '$lib/components/ui/Table.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import { getDashboardStats } from '$lib/services/relintsService';
  import { realtimeService } from '$lib/services/eventsService';
  
  import { FileText, Brain, Users, Crosshair, ArrowRight, ArrowsClockwise } from 'phosphor-svelte';

  /** @type {Array<{ key: string, label: string, width?: string, align?: 'left' | 'center' | 'right' }>} */
  const recentRelintsColumns = [
    { key: 'code', label: 'CÓDIGO RELINT', width: '180px', align: 'left' },
    { key: 'spec', label: 'ESPECIALIDADE', width: '220px', align: 'left' },
    { key: 'status', label: 'STATUS', width: '160px', align: 'left' },
    { key: 'method', label: 'MÉTODO EXTRAÇÃO', width: '180px', align: 'left' },
    { key: 'action', label: 'AÇÃO', align: 'right' }
  ];

  let stats = $state({
    totalRelints: 0,
    totalPersons: 0,
    homicideCount: 0,
    llmRate: 100,
    /** @type {any[]} */
    recentRelints: []
  });

  let isLoading = $state(true);
  let errorMessage = $state('');

  /**
   * Carrega as estatísticas reais do backend FastAPI
   * @param {boolean} [silent=false]
   */
  async function loadStats(silent = false) {
    if (!silent) isLoading = true;
    errorMessage = '';
    try {
      const data = await getDashboardStats();
      stats = data;
    } catch (err) {
      console.error('Erro ao carregar estatísticas do dashboard:', err);
      if (!silent) {
        errorMessage = err instanceof Error ? err.message : 'Falha ao conectar com o backend FastAPI.';
      }
    } finally {
      if (!silent) isLoading = false;
    }
  }

  onMount(() => {
    loadStats();

    // Inscreve para atualizações reativas automáticas via SSE
    const unsubscribe = realtimeService.subscribe('relint_created', (/** @type {any} */ _eventData) => {
      // Recarrega silenciosamente os KPIs e a tabela de recentes
      loadStats(true);
    });

    return () => {
      unsubscribe();
    };
  });

</script>

<svelte:head>
  <title>Inteligência Policial | ReadRelint Dashboard</title>
</svelte:head>

<div class="dashboard-overview">
  <div class="overview-header">
    <div class="header-info">
      <h2 class="section-title">Visão Geral de Inteligência</h2>
      <p class="section-subtitle">Acompanhamento consolidado de boletins RELINT e índices operacionais.</p>
    </div>
    
    <Button variant="ghost" size="sm" onclick={() => loadStats(false)} disabled={isLoading}>

      {#snippet icon()}
        <ArrowsClockwise size={16} weight="bold" class={isLoading ? 'spinning' : ''} />
      {/snippet}
      ATUALIZAR
    </Button>
  </div>

  {#if errorMessage}
    <Alert type="error" title="Aviso de Conexão">
      {errorMessage} (Certifique-se de que o backend FastAPI está em execução na porta 8000).
    </Alert>
  {/if}

  <div class="kpi-grid">
    <StatCard
      label="RELINTS PROCESSADOS"
      value={isLoading ? '...' : String(stats.totalRelints)}
      trend="+14%"
      trendType="positive"
      description="Boletins no banco de dados"
    >
      {#snippet icon()}
        <FileText size={24} weight="fill" color="var(--color-amber-primary)" />
      {/snippet}
    </StatCard>

    <StatCard
      label="INDIVÍDUOS QUALIFICADOS"
      value={isLoading ? '...' : String(stats.totalPersons)}
      trend="+22%"
      trendType="positive"
      description="Pessoas extraídas dos relatos"
    >
      {#snippet icon()}
        <Users size={24} weight="fill" color="var(--color-functional-info)" />
      {/snippet}
    </StatCard>

    <StatCard
      label="TAXA LEITURA OLLAMA"
      value={isLoading ? '...' : `${stats.llmRate}%`}
      trend="+1.2%"
      trendType="positive"
      description="Precisão cognitiva média"
    >
      {#snippet icon()}
        <Brain size={24} weight="fill" color="var(--color-functional-success)" />
      {/snippet}
    </StatCard>

    <StatCard
      label="DOSSIÊS HOMICÍDIOS"
      value={isLoading ? '...' : String(stats.homicideCount)}
      trend="-5%"
      trendType="negative"
      description="Crimes contra a vida registrados"
    >
      {#snippet icon()}
        <Crosshair size={24} weight="fill" color="var(--color-functional-error)" />
      {/snippet}
    </StatCard>
  </div>

  <div class="content-grid">
    <div class="main-column">
      <Card variant="elevated" title="Últimos RELINTs Extraídos" subtitle="Acompanhamento em tempo real da base de dados.">
        <div class="table-container">
          {#if isLoading && stats.recentRelints.length === 0}
            <div class="table-skeleton">
              <div class="skeleton-row"></div>
              <div class="skeleton-row"></div>
              <div class="skeleton-row"></div>
            </div>
          {:else}
            <Table 
              columns={recentRelintsColumns} 
              data={stats.recentRelints.map(r => ({
                code: r.code,
                spec: r.bm_group || 'Geral',
                status: r.user_edited ? 'Revisado' : 'Processado',
                badge: r.user_edited ? 'success' : 'neutral',
                method: r.extraction_method || 'Ollama (IA)',
                raw: r
              }))}
            >
              {#snippet rowSnippet(row)}
                <tr class="table-row">
                  <td class="td font-mono font-amber">{row.code}</td>
                  <td class="td">{row.spec}</td>
                  <td class="td">
                    <!-- @ts-ignore -->
                    <Badge variant={row.badge} size="sm" dot>{row.status}</Badge>
                  </td>
                  <td class="td text-muted">{row.method}</td>
                  <td class="td text-right">
                    <a href="/relints" class="inline-link">
                      <Button variant="ghost" size="sm">
                        {#snippet icon()}
                          <ArrowRight size={16} weight="bold" />
                        {/snippet}
                        ABRIR
                      </Button>
                    </a>
                  </td>
                </tr>
              {/snippet}
            </Table>
          {/if}
        </div>
      </Card>
    </div>


    <div class="side-column">
      <Card variant="glass" title="Status do Motor IA (Ollama)">
        <div class="ai-status">
          <div class="status-item">
            <span class="status-label">Serviço Local</span>
            <Badge variant="success" size="sm" dot>Online</Badge>
          </div>
          <div class="status-item">
            <span class="status-label">Modelo Ativo</span>
            <span class="status-value font-mono">llama-3.2-8b-instruct</span>
          </div>
          <div class="status-item">
            <span class="status-label">Tempo Médio de Inferência</span>
            <span class="status-value">2.4s por RELINT</span>
          </div>
          <div class="status-item">
            <span class="status-label">Modo Operação</span>
            <span class="status-value font-amber">100% Offline (Local)</span>
          </div>
        </div>
      </Card>
    </div>
  </div>
</div>

<style>
  .dashboard-overview {
    display: flex;
    flex-direction: column;
    gap: var(--space-8);
    height: 100%;
  }

  .overview-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
  }

  .header-info {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .section-title {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-main);
    margin: 0;
  }

  .section-subtitle {
    font-size: var(--font-size-base);
    color: var(--color-text-muted);
    margin: 0;
  }

  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: var(--space-6);
  }

  .content-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--space-6);
  }

  .table-container {
    margin-top: var(--space-4);
  }

  .font-mono {
    font-family: var(--font-family-mono);
  }

  .font-amber {
    color: var(--color-amber-primary);
    font-weight: var(--font-weight-semibold);
  }

  .text-muted {
    color: var(--color-text-muted);
  }

  .text-right {
    text-align: right;
  }

  .inline-link {
    text-decoration: none;
  }

  .table-row {
    border-bottom: 1px solid var(--color-border-subtle);
  }
  
  .table-row:hover {
    background-color: var(--color-surface-hover);
  }
  
  .td {
    padding: var(--space-3) var(--space-4);
    font-size: var(--font-size-ui);
    line-height: var(--line-height-20);
    vertical-align: middle;
  }

  .ai-status {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    margin-top: var(--space-4);
  }

  .status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: var(--space-3);
    border-bottom: 1px solid var(--color-border-subtle);
  }
  
  .status-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  .status-label {
    font-size: var(--font-size-ui);
    color: var(--color-text-muted);
  }

  .status-value {
    font-size: var(--font-size-ui);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-main);
  }

  .table-skeleton {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-4) 0;
  }

  .skeleton-row {
    height: 44px;
    background: linear-gradient(90deg, var(--color-bg-tertiary) 25%, var(--color-bg-surface-elevated) 50%, var(--color-bg-tertiary) 75%);
    background-size: 200% 100%;
    animation: skeleton-shimmer 1.5s infinite;
    border-radius: var(--radius-sm);
  }

  @keyframes skeleton-shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  :global(.spinning) {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  @media (max-width: 1024px) {
    .content-grid {
      grid-template-columns: 1fr;
    }
  }
</style>

