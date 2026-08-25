<!--
  ============================================================================
  ReadRelint - Painel Lateral de Lista de Participantes (Master List 30%)
  ============================================================================
  Renderiza a lista de indivíduos com busca instantânea, contadores de ocorrência
  e filtro de reincidentes.
  ============================================================================
-->
<script>
  import Input from '$lib/components/ui/Input.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import { 
    MagnifyingGlass, 
    User, 
    Users,
    IdentificationCard,
    WarningCircle,
    FileText,
    Images
  } from 'phosphor-svelte';

  /** @type {{ participants: any[], selectedId: any, onSelect: (person: any) => void }} */
  let { participants = [], selectedId, onSelect } = $props();

  let searchQuery = $state('');
  let filterRecurrent = $state(false);

  let filteredParticipants = $derived(() => {
    return participants.filter((p) => {
      const matchSearch = 
        !searchQuery ||
        p.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.nickname?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.document?.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchRecurrent = !filterRecurrent || (p.linked_relints_count > 1);

      return matchSearch && matchRecurrent;
    });
  });
</script>

<div class="participant-list-pane">
  <!-- Header da Lista -->
  <div class="list-header">
    <div class="header-title-row">
      <div class="title-with-icon">
        <Users size={20} weight="fill" color="var(--color-amber-primary)" />
        <h2 class="list-title">Participantes</h2>
      </div>
      <span class="count-badge">{filteredParticipants().length}</span>
    </div>

    <!-- Barra de Busca -->
    <div class="search-box">
      <Input 
        placeholder="Buscar por nome, alcunha ou RG/CPF..." 
        bind:value={searchQuery}
      >
        {#snippet prefixIcon()}
          <MagnifyingGlass size={16} weight="bold" />
        {/snippet}
      </Input>
    </div>

    <!-- Filtro de Reincidência -->
    <div class="filters-bar">
      <button 
        class="filter-pill" 
        class:is-active={!filterRecurrent}
        onclick={() => filterRecurrent = false}
      >
        Todos
      </button>
      <button 
        class="filter-pill warning-pill" 
        class:is-active={filterRecurrent}
        onclick={() => filterRecurrent = true}
      >
        <WarningCircle size={14} weight="fill" />
        Reincidentes (2+)
      </button>
    </div>
  </div>

  <!-- Lista de Participantes com Rolagem -->
  <div class="list-scroll-container">
    {#if filteredParticipants().length > 0}
      {#each filteredParticipants() as person (person.person_id)}
        {@const isSelected = selectedId === person.person_id}
        <div 
          class="person-card" 
          class:is-selected={isSelected}
          role="button"
          tabindex="0"
          onclick={() => onSelect(person)}
          onkeydown={(e) => e.key === 'Enter' && onSelect(person)}
        >
          <!-- Avatar / Foto -->
          <div class="avatar-box">
            {#if person.photo_path}
              <img src={person.photo_path} alt={person.name} class="avatar-img" />
            {:else}
              <User size={26} weight="fill" color="var(--color-text-muted)" />
            {/if}
          </div>

          <!-- Metadados -->
          <div class="person-card-info">
            <div class="card-top-row">
              <span class="person-name" title={person.name}>{person.name}</span>
              {#if person.linked_relints_count > 1}
                <Badge variant="warning" size="sm" dot>Reincidente</Badge>
              {/if}
            </div>

            {#if person.nickname}
              <span class="person-nickname">Vulgo: "{person.nickname}"</span>
            {/if}

            <div class="card-bottom-row">
              {#if person.document}
                <span class="person-doc">{person.document}</span>
              {:else}
                <span class="person-doc text-muted">Sem documento</span>
              {/if}

              <div class="relints-counter" title="{person.linked_relints_count} boletins vinculados">
                <FileText size={13} weight="bold" />
                <span>{person.linked_relints_count} RELINT{person.linked_relints_count !== 1 ? 's' : ''}</span>
              </div>
            </div>
          </div>
        </div>
      {/each}
    {:else}
      <div class="empty-list">
        <Users size={32} weight="thin" />
        <p>Nenhum participante encontrado com os filtros atuais.</p>
      </div>
    {/if}
  </div>
</div>

<style>
  .participant-list-pane {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: var(--color-bg-surface-card);
    border-right: 1px solid var(--color-border-subtle);
    box-sizing: border-box;
    overflow: hidden;
  }

  .list-header {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-4);
    border-bottom: 1px solid var(--color-border-subtle);
    background-color: var(--color-bg-secondary);
    flex-shrink: 0;
  }

  .header-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .title-with-icon {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  .list-title {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-main);
    margin: 0;
    letter-spacing: var(--letter-spacing-snug);
  }

  .count-badge {
    font-family: var(--font-family-mono);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-amber-primary);
    background-color: rgba(224, 159, 62, 0.12);
    padding: 2px 8px;
    border-radius: var(--radius-full);
    border: 1px solid rgba(224, 159, 62, 0.2);
  }

  .filters-bar {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  .filter-pill {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    background-color: var(--color-bg-tertiary);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-full);
    color: var(--color-text-muted);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    cursor: pointer;
    transition: 
      background-color var(--duration-fast) var(--ease-standard),
      color var(--duration-fast) var(--ease-standard),
      border-color var(--duration-fast) var(--ease-standard);
  }

  .filter-pill:hover {
    background-color: var(--color-bg-surface-elevated);
    color: var(--color-text-main);
  }

  .filter-pill.is-active {
    background-color: rgba(224, 159, 62, 0.15);
    color: var(--color-amber-primary);
    border-color: var(--color-amber-primary);
  }

  .filter-pill.warning-pill.is-active {
    background-color: rgba(245, 158, 11, 0.15);
    color: var(--color-functional-warning);
    border-color: var(--color-functional-warning);
  }

  .list-scroll-container {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-2);
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .person-card {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3);
    background-color: var(--color-bg-surface-card);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-default);
    cursor: pointer;
    transition: 
      background-color var(--duration-fast) var(--ease-standard),
      border-color var(--duration-fast) var(--ease-standard),
      transform var(--duration-instant) var(--ease-spring-snappy);
    text-align: left;
    outline: none;
  }

  .person-card:hover {
    background-color: var(--color-bg-surface-elevated);
    border-color: var(--color-border-medium);
  }

  .person-card.is-selected {
    background-color: var(--color-bg-tertiary);
    border-color: var(--color-amber-primary);
    box-shadow: 0 0 0 1px var(--color-amber-primary), var(--glow-amber-subtle);
  }

  .avatar-box {
    width: 44px;
    height: 44px;
    border-radius: var(--radius-full);
    background-color: var(--color-bg-primary);
    border: 1px solid var(--color-border-medium);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    overflow: hidden;
  }

  .avatar-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .person-card-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 3px;
    min-width: 0;
  }

  .card-top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
  }

  .person-name {
    font-size: var(--font-size-ui);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-main);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .person-nickname {
    font-size: var(--font-size-xs);
    color: var(--color-amber-primary);
    font-weight: var(--font-weight-medium);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .card-bottom-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
    margin-top: 2px;
  }

  .person-doc {
    font-family: var(--font-family-mono);
    font-size: 11px;
    color: var(--color-text-muted);
  }

  .relints-counter {
    display: flex;
    align-items: center;
    gap: 4px;
    font-family: var(--font-family-mono);
    font-size: 11px;
    color: var(--color-text-muted);
  }

  .text-muted {
    color: var(--color-text-disabled);
  }

  .empty-list {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-8) var(--space-4);
    text-align: center;
    color: var(--color-text-muted);
    gap: var(--space-3);
  }
</style>
