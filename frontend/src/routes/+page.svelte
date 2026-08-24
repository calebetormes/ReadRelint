<script>
  import StatCard from '$lib/components/ui/StatCard.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Table from '$lib/components/ui/Table.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  
  import { FileText, Brain, Users, Crosshair, ArrowRight } from 'phosphor-svelte';

  /** @type {Array<{ key: string, label: string, width?: string, align?: 'left' | 'center' | 'right' }>} */
  const recentRelintsColumns = [
    { key: 'code', label: 'CÓDIGO RELINT', width: '180px', align: 'left' },
    { key: 'spec', label: 'ESPECIALIDADE', width: '220px', align: 'left' },
    { key: 'status', label: 'STATUS', width: '160px', align: 'left' },
    { key: 'method', label: 'MÉTODO EXTRAÇÃO', width: '180px', align: 'left' },
    { key: 'action', label: 'AÇÃO', align: 'right' }
  ];

  const recentRelintsData = [
    { code: 'RELINT-2026-001', spec: 'Homicídios & Facções', status: 'Concluído', method: 'Ollama (Llama 3.2)', badge: 'success' },
    { code: 'RELINT-2026-002', spec: 'Tráfico de Drogas', status: 'Processando', method: 'Ollama (DeepSeek R1)', badge: 'warning' },
    { code: 'RELINT-2026-003', spec: 'Roubos e Furtos', status: 'Pendente', method: 'Fila de Espera', badge: 'neutral' },
    { code: 'RELINT-2026-004', spec: 'Homicídios', status: 'Erro IA', method: 'Ollama (Llama 3.2)', badge: 'error' },
  ];
</script>

<svelte:head>
  <title>Visão Geral | ReadRelint Dashboard</title>
</svelte:head>

<div class="dashboard-overview">
  <div class="overview-header">
    <h2 class="section-title">Indicadores Globais de Inteligência</h2>
    <p class="section-subtitle">Estatísticas processadas pelo motor Ollama nas últimas 24 horas.</p>
  </div>

  <div class="kpi-grid">
    <StatCard
      label="RELINTS PROCESSADOS"
      value="1.248"
      trend="+14%"
      trendType="positive"
      description="Boletins lidos e estruturados"
    >
      {#snippet icon()}
        <FileText size={24} weight="fill" color="var(--color-amber-primary)" />
      {/snippet}
    </StatCard>

    <StatCard
      label="INDIVÍDUOS QUALIFICADOS"
      value="3.502"
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
      value="98.5%"
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
      value="145"
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
      <Card variant="elevated" title="Últimos RELINTs Extraídos" subtitle="Acompanhamento em tempo real da fila de processamento IA.">
        <div class="table-container">
          <Table columns={recentRelintsColumns} data={recentRelintsData}>
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
                  <Button variant="ghost" size="sm">
                    {#snippet icon()}
                      <ArrowRight size={16} weight="bold" />
                    {/snippet}
                    ABRIR
                  </Button>
                </td>
              </tr>
            {/snippet}
          </Table>
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
            <span class="status-label">Fila de Espera</span>
            <span class="status-value" style="color: var(--color-amber-primary);">12 documentos</span>
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

  @media (max-width: 1024px) {
    .content-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
