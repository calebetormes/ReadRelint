<script>
  import Input from '$lib/components/ui/Input.svelte';
  import { 
    MagnifyingGlass, 
    CheckCircle, 
    Clock, 
    Funnel, 
    Crosshair, 
    Pill, 
    ShieldWarning, 
    FileText 
  } from 'phosphor-svelte';

  /** @type {{ relints: any[], selectedId: any, onSelect: (relint: any) => void }} */
  let { relints = [], selectedId, onSelect } = $props();

  let searchQuery = $state('');
  let filterSpecialty = $state('Todos');

  let filteredRelints = $derived(() => {
    return relints.filter((r) => {
      const matchSearch = 
        !searchQuery ||
        r.code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.subject?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.source_file?.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchSpecialty = 
        filterSpecialty === 'Todos' || r.bm_group === filterSpecialty;

      return matchSearch && matchSpecialty;
    });
  });
</script>

<div class="list-pane">
  <div class="list-controls">
    <Input 
      placeholder="Buscar por código, assunto..." 
      bind:value={searchQuery}
    >
      {#snippet prefixIcon()}
        <MagnifyingGlass size={16} weight="bold" color="var(--color-text-muted)" />
      {/snippet}
    </Input>

    <div class="filter-bar">
      <Funnel size={14} weight="fill" color="var(--color-text-muted)" />
      <select 
        class="filter-select"
        value={filterSpecialty}
        onchange={(e) => filterSpecialty = e.currentTarget.value}
      >
        <option value="Todos">Todas Especialidades</option>
        <option value="Homicídio">Homicídio</option>
        <option value="Tráfico de Drogas">Tráfico de Drogas</option>
        <option value="Roubos e Furtos">Roubos e Furtos</option>
        <option value="Geral">Geral</option>
      </select>
    </div>
  </div>

  <div class="relint-items-list">
    {#each filteredRelints() as relint (relint.id)}
      {@const isSelected = selectedId === relint.id}
      <button 
        class="relint-card-item" 
        class:is-selected={isSelected}
        onclick={() => onSelect(relint)}
      >
        <div class="item-header">
          <div class="code-and-specialty">
            {#if relint.bm_group === 'Homicídio'}
              <span title="Especialidade: Homicídio" class="icon-inline">
                <Crosshair size={14} weight="fill" color="var(--color-functional-error)" />
              </span>
            {:else if relint.bm_group === 'Tráfico de Drogas'}
              <span title="Especialidade: Tráfico de Drogas" class="icon-inline">
                <Pill size={14} weight="fill" color="var(--color-functional-warning)" />
              </span>
            {:else if relint.bm_group === 'Roubos e Furtos'}
              <span title="Especialidade: Roubos e Furtos" class="icon-inline">
                <ShieldWarning size={14} weight="fill" color="var(--color-functional-info)" />
              </span>
            {:else}
              <span title="Especialidade: Geral" class="icon-inline">
                <FileText size={14} weight="fill" color="var(--color-text-muted)" />
              </span>
            {/if}
            <span class="relint-code font-mono">{relint.code}</span>
          </div>

          <div class="status-icon-box">
            {#if relint.user_edited}
              <span title="Revisado por Humano" class="icon-inline">
                <CheckCircle size={14} weight="fill" color="var(--color-functional-success)" />
              </span>
            {:else}
              <span title="Pendente Revisão" class="icon-inline">
                <Clock size={14} weight="fill" color="var(--color-text-disabled)" />
              </span>
            {/if}
          </div>
        </div>

        <h4 class="item-subject">{relint.subject || 'Sem assunto especificado'}</h4>

        <div class="item-footer">
          <span class="item-date">{relint.date_of_fact || 'Data N/I'}</span>
        </div>
      </button>
    {:else}
      <div class="empty-list">
        <span>Nenhum RELINT encontrado.</span>
      </div>
    {/each}
  </div>
</div>

<style>
  .list-pane {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: var(--color-bg-surface-card);
    border-right: 1px solid var(--color-border-subtle);
    box-sizing: border-box;
  }

  .list-controls {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-4);
    border-bottom: 1px solid var(--color-border-subtle);
  }

  .filter-bar {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  .filter-select {
    flex: 1;
    height: 32px;
    background-color: var(--color-bg-primary);
    border: 1px solid var(--color-border-medium);
    border-radius: var(--radius-sm);
    color: var(--color-text-main);
    font-size: var(--font-size-xs);
    padding: 0 var(--space-2);
    outline: none;
  }

  .relint-items-list {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    padding: var(--space-2);
    gap: var(--space-2);
  }

  .relint-card-item {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    padding: var(--space-2) var(--space-3);
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: var(--radius-sm);
    text-align: left;
    cursor: pointer;
    transition: 
      background-color var(--duration-fast) var(--ease-standard),
      border-color var(--duration-fast) var(--ease-standard);
  }

  .relint-card-item:hover {
    background-color: var(--color-surface-hover);
  }

  .relint-card-item.is-selected {
    background-color: rgba(224, 159, 62, 0.08);
    border-color: var(--color-amber-primary);
  }

  .item-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .code-and-specialty {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  .icon-inline {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
  }

  .relint-code {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-amber-primary);
  }

  .item-subject {
    font-size: var(--font-size-ui);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-main);
    margin: 0;
    line-height: var(--line-height-140);
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .item-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .item-date {
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
  }

  .font-mono {
    font-family: var(--font-family-mono);
  }

  .empty-list {
    padding: var(--space-6);
    text-align: center;
    color: var(--color-text-muted);
    font-size: var(--font-size-ui);
  }
</style>
