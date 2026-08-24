<script>
  import Button from '$lib/components/ui/Button.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import StatCard from '$lib/components/ui/StatCard.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Switch from '$lib/components/ui/Switch.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Table from '$lib/components/ui/Table.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import Tabs from '$lib/components/ui/Tabs.svelte';

  // Phosphor Icons (Fill Weight)
  import {
    ShieldCheck,
    FileText,
    Brain,
    Crosshair,
    MagnifyingGlass,
    LockKey,
    CheckCircle,
    WarningCircle,
    Warning,
    Info,
    SquaresFour,
    UserCircle,
    GearSix,
    Database,
    ChartBar,
    MapPin,
    Fingerprint,
    ClockCountdown,
    Trash,
    PlusCircle,
    DownloadSimple,
    SlidersHorizontal,
    Sparkle
  } from 'phosphor-svelte';

  let activeTab = $state('geral');
  let searchVal = $state('');
  let isAiEnabled = $state(true);
  let isSilentMode = $state(false);
  let isModalOpen = $state(false);
  let isLoadingBtn = $state(false);

  function simulateLoading() {
    isLoadingBtn = true;
    setTimeout(() => {
      isLoadingBtn = false;
    }, 2000);
  }

  /** @type {Array<{ key: string, label: string, width?: string, align?: 'left' | 'center' | 'right' }>} */
  const tableColumns = [
    { key: 'code', label: 'CÓDIGO RELINT', width: '180px', align: 'left' },
    { key: 'spec', label: 'ESPECIALIDADE', width: '220px', align: 'left' },
    { key: 'status', label: 'STATUS', width: '160px', align: 'left' },
    { key: 'method', label: 'PROCESSAMENTO', width: '180px', align: 'left' },
    { key: 'action', label: 'AÇÃO', align: 'right' }
  ];

  const sampleData = [
    { code: 'RELINT-2026-001', spec: 'Homicídios & Facções', status: 'Concluído', method: 'Ollama (DeepSeek R1)', badge: /** @type {const} */('success') },
    { code: 'RELINT-2026-002', spec: 'Tráfico de Drogas', status: 'Processando', method: 'Ollama (Llama 3.2)', badge: /** @type {const} */('amber') },
    { code: 'RELINT-2026-003', spec: 'Roubos e Furtos de Cargas', status: 'Pendente', method: 'Regex Parser', badge: /** @type {const} */('neutral') }
  ];

  /** @type {Array<{ id: string, label: string, badge?: string, icon?: any }>} */
  const tabsList = [
    { id: 'geral', label: 'Visão Geral', badge: '1.248', icon: tabIconGeral },
    { id: 'homicidios', label: 'Dossiês de Homicídios', icon: tabIconHomicidios },
    { id: 'config', label: 'Configurações IA', icon: tabIconConfig }
  ];

  const policeIcons = [
    { name: 'ShieldCheck', comp: ShieldCheck, category: 'Segurança' },
    { name: 'Fingerprint', comp: Fingerprint, category: 'Identificação' },
    { name: 'FileText', comp: FileText, category: 'Relatórios' },
    { name: 'Brain', comp: Brain, category: 'Inteligência IA' },
    { name: 'Crosshair', comp: Crosshair, category: 'Operações' },
    { name: 'Database', comp: Database, category: 'Registros' },
    { name: 'MapPin', comp: MapPin, category: 'Localização' },
    { name: 'ChartBar', comp: ChartBar, category: 'Estatísticas' },
    { name: 'LockKey', comp: LockKey, category: 'Acesso Restrito' },
    { name: 'MagnifyingGlass', comp: MagnifyingGlass, category: 'Investigação' },
    { name: 'ClockCountdown', comp: ClockCountdown, category: 'Auditoria' },
    { name: 'SlidersHorizontal', comp: SlidersHorizontal, category: 'Parâmetros' }
  ];
</script>

{#snippet tabIconGeral()}
  <SquaresFour size={16} weight="fill" />
{/snippet}

{#snippet tabIconHomicidios()}
  <Crosshair size={16} weight="fill" />
{/snippet}

{#snippet tabIconConfig()}
  <GearSix size={16} weight="fill" />
{/snippet}

<svelte:head>
  <title>Design System & UI Library | ReadRelint</title>
</svelte:head>

<main class="ds-container">
  <header class="ds-header">
    <div class="ds-title-group">
      <div class="ds-badges-top">
        <Badge variant="amber" size="sm" dot>DESIGN SYSTEM v2.0</Badge>
        <Badge variant="success" size="sm" dot>PHOSPHOR ICONS (FILL)</Badge>
        <Badge variant="info" size="sm" dot>PIXEL-PERFECT (4PX GRID)</Badge>
      </div>
      <h1 class="ds-title">Biblioteca de Componentes Oficiais</h1>
      <p class="ds-subtitle">
        Construída com <strong>Svelte 5</strong>, paleta escura com destaques em <strong>Âmbar</strong>, ícones <strong>Phosphor Icons (Fill)</strong>, tipografia <strong>Elms Sans</strong> e interações táteis fluidas do <strong>Apple Design</strong>.
      </p>
    </div>

    <div class="ds-header-actions">
      <Button variant="glow" onclick={() => isModalOpen = true}>
        {#snippet icon()}
          <Sparkle size={18} weight="fill" />
        {/snippet}
        ABRIR MODAL DEMO
      </Button>
    </div>
  </header>

  <!-- 1. STATCARDS -->
  <section class="ds-section">
    <h2 class="ds-section-title">1. Cartões de Métrica (StatCard)</h2>
    <div class="grid-3">
      <StatCard
        label="TOTAL DE RELINTS"
        value="1.248"
        trend="+14%"
        trendType="positive"
        description="Comparado aos últimos 30 dias de inteligência"
      >
        {#snippet icon()}
          <FileText size={24} weight="fill" color="var(--color-amber-primary)" />
        {/snippet}
      </StatCard>

      <StatCard
        label="PROCESSADOS COM IA"
        value="982"
        trend="+8%"
        trendType="positive"
        description="Extrações estruturadas via Ollama local"
      >
        {#snippet icon()}
          <Brain size={24} weight="fill" color="var(--color-functional-success)" />
        {/snippet}
      </StatCard>

      <StatCard
        label="EM PROCESSAMENTO"
        value="45"
        trend="-3%"
        trendType="negative"
        description="Fila de documentos aguardando transcrição"
      >
        {#snippet icon()}
          <ClockCountdown size={24} weight="fill" color="var(--color-functional-warning)" />
        {/snippet}
      </StatCard>
    </div>
  </section>

  <!-- 2. PHOSPHOR ICONS GALLERY (FILL) -->
  <section class="ds-section">
    <h2 class="ds-section-title">2. Catálogo de Ícones Policiais (Phosphor Icons - Fill)</h2>
    <div class="ds-card-panel">
      <div class="icons-grid">
        {#each policeIcons as iconItem}
          {@const IconComp = iconItem.comp}
          <div class="icon-card">
            <div class="icon-wrapper">
              <IconComp size={28} weight="fill" />
            </div>
            <span class="icon-name">{iconItem.name}</span>
            <span class="icon-cat">{iconItem.category}</span>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- 3. BUTTONS WITH ICONS -->
  <section class="ds-section">
    <h2 class="ds-section-title">3. Botões de Ação com Ícones (Button)</h2>
    <div class="ds-card-panel">
      <div class="button-group">
        <Button variant="primary">
          {#snippet icon()}
            <PlusCircle size={18} weight="fill" />
          {/snippet}
          NOVO RELINT
        </Button>

        <Button variant="glow">
          {#snippet icon()}
            <Brain size={18} weight="fill" />
          {/snippet}
          EXTRAIR COM IA
        </Button>

        <Button variant="secondary">
          {#snippet icon()}
            <DownloadSimple size={18} weight="fill" />
          {/snippet}
          EXPORTAR CSV
        </Button>

        <Button variant="outline">
          {#snippet icon()}
            <MagnifyingGlass size={18} weight="fill" />
          {/snippet}
          BUSCA AVANÇADA
        </Button>

        <Button variant="danger">
          {#snippet icon()}
            <Trash size={18} weight="fill" />
          {/snippet}
          EXCLUIR
        </Button>

        <Button variant="primary" loading={isLoadingBtn} onclick={simulateLoading}>
          {isLoadingBtn ? 'PROCESSANDO...' : 'TESTAR LOADING'}
        </Button>
      </div>

      <div class="button-group" style="margin-top: var(--space-4);">
        <Button variant="primary" size="sm">
          {#snippet icon()}
            <ShieldCheck size={16} weight="fill" />
          {/snippet}
          TAMANHO SM (32px)
        </Button>
        <Button variant="primary" size="md">
          {#snippet icon()}
            <ShieldCheck size={18} weight="fill" />
          {/snippet}
          TAMANHO MD (40px)
        </Button>
        <Button variant="primary" size="lg">
          {#snippet icon()}
            <ShieldCheck size={20} weight="fill" />
          {/snippet}
          TAMANHO LG (48px)
        </Button>
      </div>
    </div>
  </section>

  <!-- 4. BADGES -->
  <section class="ds-section">
    <h2 class="ds-section-title">4. Badges & Chips (Badge)</h2>
    <div class="ds-card-panel">
      <div class="badge-group">
        <Badge variant="amber" dot>ÂMBAR DESTAQUE</Badge>
        <Badge variant="success" dot>CONCLUÍDO</Badge>
        <Badge variant="warning" dot>PROCESSANDO</Badge>
        <Badge variant="error" dot>ERRO DE EXTRAÇÃO</Badge>
        <Badge variant="info" dot>INFORMAÇÃO</Badge>
        <Badge variant="neutral">NEUTRO REGULAR</Badge>
      </div>

      <div class="badge-group" style="margin-top: var(--space-4);">
        <Badge variant="amber" size="sm">COMPACTO SM (20px)</Badge>
        <Badge variant="amber" size="md">PADRÃO MD (24px)</Badge>
      </div>
    </div>
  </section>

  <!-- 5. TABS & FORM CONTROLS WITH ICONS -->
  <section class="ds-section">
    <h2 class="ds-section-title">5. Navegação & Formulários (Tabs, Input, Switch)</h2>
    <div class="grid-2">
      <Card variant="base" title="Controles de Formulário" subtitle="Inputs com ícones Phosphor e foco âmbar">
        <div class="form-stack">
          <Input
            label="CÓDIGO DE IDENTIFICAÇÃO"
            placeholder="Ex: RELINT-2026-001"
            bind:value={searchVal}
            hint="Código único do relatório de inteligência"
          >
            {#snippet prefixIcon()}
              <MagnifyingGlass size={18} weight="fill" />
            {/snippet}
            {#snippet suffixIcon()}
              <Fingerprint size={18} weight="fill" color="var(--color-amber-primary)" />
            {/snippet}
          </Input>

          <Input
            label="SENHA DE ACESSO AO SISTEMA"
            type="password"
            value="segredo_inteligencia"
          >
            {#snippet prefixIcon()}
              <LockKey size={18} weight="fill" />
            {/snippet}
          </Input>

          <div class="switch-row">
            <Switch
              bind:checked={isAiEnabled}
              label="Ativar Motor de Inteligência Artificial (Ollama)"
            />
          </div>

          <div class="switch-row">
            <Switch
              bind:checked={isSilentMode}
              label="Modo de Operação Silencioso"
            />
          </div>
        </div>
      </Card>

      <Card variant="glass" title="Navegação em Abas Segmentadas" subtitle="Controle com ícones integrados e mola fluida">
        <div style="margin-bottom: var(--space-4);">
          <Tabs tabs={tabsList} bind:activeTab />
        </div>

        <p style="color: var(--color-text-muted); font-size: var(--font-size-base); line-height: var(--line-height-24);">
          Aba selecionada no momento: <strong style="color: var(--color-amber-primary);">{activeTab.toUpperCase()}</strong>.
          O componente Tabs utiliza cálculo matemático da grade base de 4px para garantir alinhamento perfeito.
        </p>

        {#snippet footer()}
          <span style="font-size: var(--font-size-xs); color: var(--color-text-muted);">
            Renderizado em container de vidro translúcido com backdrop-blur.
          </span>
          <Button variant="secondary" size="sm">
            {#snippet icon()}
              <SlidersHorizontal size={14} weight="fill" />
            {/snippet}
            SAIBA MAIS
          </Button>
        {/snippet}
      </Card>
    </div>
  </section>

  <!-- 6. TABLE / DATAGRID -->
  <section class="ds-section">
    <h2 class="ds-section-title">6. Tabela de Inteligência Policial (Table)</h2>
    <Table columns={tableColumns} data={sampleData}>
      {#snippet rowSnippet(row)}
        <tr class="table-row">
          <td class="td font-mono font-amber">{row.code}</td>
          <td class="td">{row.spec}</td>
          <td class="td">
            <Badge variant={row.badge} size="sm" dot>{row.status}</Badge>
          </td>
          <td class="td text-muted">{row.method}</td>
          <td class="td text-right">
            <Button variant="outline" size="sm">
              {#snippet icon()}
                <FileText size={14} weight="fill" />
              {/snippet}
              DETALHES
            </Button>
          </td>
        </tr>
      {/snippet}
    </Table>
  </section>

  <!-- 7. ALERTS WITH ICONS -->
  <section class="ds-section">
    <h2 class="ds-section-title">7. Notificações e Alertas (Alert)</h2>
    <div class="alert-stack">
      <Alert type="info" title="Sistema ReadRelint v2.0 Online">
        {#snippet icon()}
          <Info size={22} weight="fill" />
        {/snippet}
        O leitor de inteligência relint está conectado e sincronizado com o banco de dados policial.
      </Alert>

      <Alert type="success" title="Extração Concluída com Sucesso">
        {#snippet icon()}
          <CheckCircle size={22} weight="fill" />
        {/snippet}
        Todos os 15 relatórios selecionados foram lidos e categorizados com sucesso.
      </Alert>

      <Alert type="warning" title="Atenção ao Motor Local">
        {#snippet icon()}
          <Warning size={22} weight="fill" />
        {/snippet}
        O modelo Ollama local está operando com fila alta. O processamento pode levar mais tempo.
      </Alert>

      <Alert type="error" title="Falha de Conexão">
        {#snippet icon()}
          <WarningCircle size={22} weight="fill" />
        {/snippet}
        Não foi possível se conectar com o backend FastAPI. Verifique se o serviço local está ativo.
      </Alert>
    </div>
  </section>
</main>

<!-- MODAL DEMO -->
<Modal bind:open={isModalOpen} title="Dossiê de Inteligência Policial">
  <p style="margin-bottom: var(--space-4);">
    Este é um exemplo de <strong>Modal Dialog</strong> construído com o Design System. Ele utiliza sobreposição com <code>backdrop-filter: blur(16px)</code>, contornos suaves e fechamento por tecla <code>ESC</code> ou clique externo.
  </p>
  <div class="form-stack">
    <Input label="NOME DO RESPONSÁVEL" value="Agente da Inteligência">
      {#snippet prefixIcon()}
        <UserCircle size={18} weight="fill" />
      {/snippet}
    </Input>
    <Input label="OBSERVAÇÃO OPERACIONAL" placeholder="Digite uma nota sobre a operação...">
      {#snippet prefixIcon()}
        <FileText size={18} weight="fill" />
      {/snippet}
    </Input>
  </div>

  {#snippet footer()}
    <Button variant="ghost" onclick={() => isModalOpen = false}>CANCELAR</Button>
    <Button variant="primary" onclick={() => isModalOpen = false}>
      {#snippet icon()}
        <CheckCircle size={16} weight="fill" />
      {/snippet}
      SALVAR ALTERAÇÕES
    </Button>
  {/snippet}
</Modal>

<style>
  .ds-container {
    max-width: 1280px;
    margin: 0 auto;
    padding: var(--space-8) var(--space-6) var(--space-16) var(--space-6);
    display: flex;
    flex-direction: column;
    gap: var(--space-10);
  }

  .ds-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--space-6);
    padding-bottom: var(--space-6);
    border-bottom: 1px solid var(--color-border-subtle);
  }

  .ds-title-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .ds-badges-top {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  .ds-title {
    font-size: var(--font-size-3xl);
    font-weight: var(--font-weight-bold);
    letter-spacing: var(--letter-spacing-tight);
    line-height: var(--line-height-40);
    color: var(--color-text-main);
  }

  .ds-subtitle {
    font-size: var(--font-size-md);
    color: var(--color-text-muted);
    line-height: var(--line-height-24);
    max-width: 720px;
  }

  .ds-section {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .ds-section-title {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    color: var(--color-amber-primary);
    line-height: var(--line-height-32);
    letter-spacing: var(--letter-spacing-snug);
  }

  .ds-card-panel {
    background-color: var(--color-bg-surface-card);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-md);
    padding: var(--space-6);
  }

  .icons-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: var(--space-4);
  }

  .icon-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-4);
    background-color: var(--color-bg-tertiary);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-sm);
    gap: var(--space-2);
    transition: 
      border-color var(--duration-fast) var(--ease-standard),
      background-color var(--duration-fast) var(--ease-standard),
      transform var(--duration-fast) var(--ease-spring-snappy);
    cursor: pointer;
  }

  .icon-card:hover {
    border-color: var(--color-amber-primary);
    background-color: var(--color-bg-surface-elevated);
    transform: translateY(-2px);
  }

  .icon-wrapper {
    color: var(--color-amber-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform var(--duration-fast) var(--ease-spring-bounce);
  }

  .icon-card:hover .icon-wrapper {
    transform: scale(1.15);
  }

  .icon-name {
    font-family: var(--font-family-mono);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-main);
    text-align: center;
  }

  .icon-cat {
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
    text-align: center;
  }

  .grid-3 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--space-4);
  }

  .grid-2 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
    gap: var(--space-6);
  }

  .button-group, .badge-group {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-3);
  }

  .form-stack {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .switch-row {
    padding-top: var(--space-1);
  }

  .alert-stack {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
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
</style>
