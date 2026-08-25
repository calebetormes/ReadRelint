<script>
  import Input from '$lib/components/ui/Input.svelte';
  import { 
    MagnifyingGlass, 
    CheckCircle, 
    Clock, 
    Crosshair, 
    Pill, 
    ShieldWarning, 
    FileText,
    FilePdf,
    CalendarBlank
  } from 'phosphor-svelte';

  /** @type {{ relints: any[], selectedId: any, onSelect: (relint: any) => void }} */
  let { relints = [], selectedId, onSelect } = $props();

  let searchQuery = $state('');
  let filterSpecialty = $state('Todos');

  const specialtyFilters = [
    { id: 'Todos', label: 'Todos' },
    { id: 'Homicídio', label: 'Homicídio', icon: Crosshair, color: 'var(--color-functional-error)' },
    { id: 'Tráfico de Drogas', label: 'Tráfico', icon: Pill, color: 'var(--color-functional-warning)' },
    { id: 'Roubos e Furtos', label: 'Patrimônio', icon: ShieldWarning, color: 'var(--color-functional-info)' }
  ];

  let filteredRelints = $derived(
    relints
      .filter((r) => {
        const matchSearch = 
          !searchQuery ||
          r.code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          r.subject?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          r.source_file?.toLowerCase().includes(searchQuery.toLowerCase());
        
        const matchSpecialty = 
          filterSpecialty === 'Todos' || r.bm_group === filterSpecialty;

        return matchSearch && matchSpecialty;
      })
      .sort((a, b) => {
        const numA = Number(a.id) || 0;
        const numB = Number(b.id) || 0;
        return numB - numA;
      })
  );



  /**
   * Extrai apenas o número do RELINT ou código limpo (ex: "RELINT 200")
   * @param {any} relint
   */
  function formatRelintNumber(relint) {
    const raw = String(relint?.source_file || relint?.code || relint?.id || '');
    // Tenta encontrar padrões como "RELINT 200", "RELINT_200", "200_RELINT", "RELINT-200" ou números
    const match = raw.match(/relint[_\-\s]*(\d+)/i) || raw.match(/(\d+)[_\-\s]*relint/i);
    if (match && match[1]) {
      return `RELINT ${parseInt(match[1], 10)}`;
    }
    // Caso não encontre palavra RELINT mas tenha ID numérico
    if (relint?.id && !isNaN(Number(relint.id))) {
      return `RELINT ${relint.id}`;
    }
    // Fallback: limpa extensão de arquivo
    return raw.replace(/\.pdf$/i, '').replace(/_/g, ' ');
  }
</script>

<div class="list-pane">
  <!-- Cabeçalho com Busca e Contador -->
  <div class="list-header">
    <div class="header-top-row">
      <span class="header-title">Boletins</span>
      <span class="count-badge">{filteredRelints.length} {filteredRelints.length === 1 ? 'relatório' : 'relatórios'}</span>
    </div>


    <Input 
      placeholder="Buscar por código, assunto..." 
      bind:value={searchQuery}
    >
      {#snippet prefixIcon()}
        <MagnifyingGlass size={15} weight="bold" color="var(--color-text-muted)" />
      {/snippet}
    </Input>

    <!-- Chips Horizontais de Filtro -->
    <div class="filter-chips">
      {#each specialtyFilters as filter}
        <button 
          class="chip-btn" 
          class:active={filterSpecialty === filter.id}
          onclick={() => filterSpecialty = filter.id}
        >
          {#if filter.icon}
            {@const IconComponent = filter.icon}
            <IconComponent size={12} weight="fill" color={filter.color} />
          {/if}
          <span>{filter.label}</span>
        </button>
      {/each}
    </div>
  </div>

  <!-- Lista com Cards Estilizados -->
  <div class="relint-items-list">
    {#each filteredRelints as relint (relint.id)}
      {@const isSelected = selectedId === relint.id}

      <button 
        class="relint-card-item" 
        class:is-selected={isSelected}
        onclick={() => onSelect(relint)}
      >
        <!-- Linha 1: Ícone PDF + Número do RELINT (Esquerda) e Ícone Especialidade + Status Revisão (Direita Lado a Lado) -->
        <div class="card-row-top">
          <div class="code-and-pdf">
            <FilePdf size={16} weight="duotone" class="file-icon" />
            <span class="relint-code font-mono">{formatRelintNumber(relint)}</span>
          </div>

          <div class="indicators-box">
            {#if relint.bm_group === 'Homicídio'}
              <span title="Especialidade: Homicídio" class="icon-indicator icon-homicidio">
                <Crosshair size={14} weight="fill" />
              </span>
            {:else if relint.bm_group === 'Tráfico de Drogas'}
              <span title="Especialidade: Tráfico de Drogas" class="icon-indicator icon-trafico">
                <Pill size={14} weight="fill" />
              </span>
            {:else if relint.bm_group === 'Roubos e Furtos'}
              <span title="Especialidade: Roubos e Furtos" class="icon-indicator icon-patrimonio">
                <ShieldWarning size={14} weight="fill" />
              </span>
            {/if}

            {#if relint.user_edited}
              <span title="Revisado por Humano" class="status-indicator success">
                <CheckCircle size={15} weight="fill" />
              </span>
            {:else}
              <span title="Pendente de Revisão" class="status-indicator pending">
                <Clock size={15} weight="fill" />
              </span>
            {/if}
          </div>
        </div>

        <!-- Linha 2: Texto do Assunto -->
        <div class="card-row-subject">
          <span class="item-subject" title={relint.subject || relint.source_file}>
            {relint.subject || 'Sem assunto especificado'}
          </span>
        </div>

        <!-- Linha 3: Rodapé com Apenas a Data -->
        <div class="card-row-footer">
          <div class="date-tag">
            <CalendarBlank size={12} weight="regular" />
            <span>{relint.date_of_fact || 'Data N/I'}</span>
          </div>

          {#if relint.modification_date_history}
            <span class="file-date-subtle" title="Data do Arquivo">
              {relint.modification_date_history}
            </span>
          {/if}
        </div>
      </button>
    {:else}
      <div class="empty-list">
        <FileText size={32} weight="duotone" color="var(--color-border-medium)" />
        <span>Nenhum RELINT encontrado</span>
      </div>
    {/each}
  </div>
</div>

<style>
  .list-pane {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: #0d0d0d;
    border-right: 1px solid var(--color-border-subtle);
    box-sizing: border-box;
  }

  .list-header {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-4);
    background-color: #121212;
    border-bottom: 1px solid var(--color-border-subtle);
  }

  .header-top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .header-title {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-main);
    letter-spacing: -0.2px;
  }

  .count-badge {
    font-size: var(--font-size-xs);
    font-family: var(--font-family-mono);
    color: var(--color-text-muted);
    background-color: rgba(255, 255, 255, 0.05);
    padding: 2px 8px;
    border-radius: var(--radius-full);
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  .filter-chips {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding-bottom: 2px;
  }

  .filter-chips::-webkit-scrollbar {
    display: none;
  }

  .chip-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: var(--radius-full);
    color: var(--color-text-muted);
    font-size: 11px;
    font-weight: var(--font-weight-medium);
    cursor: pointer;
    white-space: nowrap;
    transition: all var(--duration-fast) var(--ease-standard);
  }

  .chip-btn:hover {
    background-color: rgba(255, 255, 255, 0.08);
    color: var(--color-text-main);
    border-color: rgba(255, 255, 255, 0.15);
  }

  .chip-btn.active {
    background-color: rgba(224, 159, 62, 0.12);
    border-color: var(--color-amber-primary);
    color: var(--color-amber-primary);
    font-weight: var(--font-weight-semibold);
  }

  .relint-items-list {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    padding: var(--space-3);
    gap: 8px;
  }

  .relint-card-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 10px 12px;
    background-color: #141414;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-left: 3px solid transparent;
    border-radius: var(--radius-default);
    text-align: left;
    cursor: pointer;
    transition: 
      background-color var(--duration-fast) var(--ease-standard),
      border-color var(--duration-fast) var(--ease-standard),
      transform var(--duration-fast) var(--ease-standard);
  }

  .relint-card-item:hover {
    background-color: #1a1a1a;
    border-color: rgba(255, 255, 255, 0.12);
  }

  .relint-card-item.is-selected {
    background-color: #1b1712;
    border-color: rgba(224, 159, 62, 0.3);
    border-left: 3px solid var(--color-amber-primary);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }

  .card-row-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
  }

  .code-and-pdf {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  :global(.file-icon) {
    color: var(--color-amber-primary);
    opacity: 0.9;
    flex-shrink: 0;
  }

  .relint-code {
    font-size: 12px;
    font-weight: var(--font-weight-bold);
    color: var(--color-amber-primary);
    letter-spacing: 0.3px;
  }

  .indicators-box {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .icon-indicator {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
    padding: 2px;
    border-radius: 4px;
  }

  .icon-homicidio {
    color: #f87171;
    background-color: rgba(239, 68, 68, 0.12);
  }

  .icon-trafico {
    color: #fbbf24;
    background-color: rgba(245, 158, 11, 0.12);
  }

  .icon-patrimonio {
    color: #60a5fa;
    background-color: rgba(59, 130, 246, 0.12);
  }

  .status-indicator.success {
    color: var(--color-functional-success);
    display: inline-flex;
    align-items: center;
  }

  .status-indicator.pending {
    color: var(--color-text-disabled);
    opacity: 0.5;
    display: inline-flex;
    align-items: center;
  }

  .card-row-subject {
    min-width: 0;
  }

  .item-subject {
    font-size: 12px;
    font-weight: var(--font-weight-medium);
    color: var(--color-text-main);
    line-height: 1.35;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    word-break: break-word;
  }

  .relint-card-item.is-selected .item-subject {
    color: #ffffff;
    font-weight: var(--font-weight-semibold);
  }

  .card-row-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
    margin-top: 1px;
    padding-top: 4px;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
  }

  .date-tag {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    color: var(--color-text-muted);
  }

  .file-date-subtle {
    font-size: 10px;
    font-family: var(--font-family-mono);
    color: var(--color-text-disabled);
  }

  .font-mono {
    font-family: var(--font-family-mono);
  }

  .empty-list {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-8) var(--space-4);
    gap: var(--space-2);
    color: var(--color-text-muted);
    font-size: var(--font-size-ui);
    text-align: center;
  }
</style>

