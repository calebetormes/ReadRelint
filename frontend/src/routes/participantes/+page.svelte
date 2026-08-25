<!--
  ============================================================================
  ReadRelint - Rota /participantes (Página de Gerenciamento de Pessoas/Dossiês)
  ============================================================================
  Layout Master-Detail (30% Lista / 70% Dossiê) com transição fluida, busca
  e persistência direta de edições no SQLite.
  ============================================================================
-->
<script>
  import { onMount } from 'svelte';
  import ParticipantListPane from '$lib/components/participant/ParticipantListPane.svelte';
  import ParticipantDetailPane from '$lib/components/participant/ParticipantDetailPane.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { getParticipants, getParticipantById, updateParticipant } from '$lib/services/participantsService';
  import { ArrowsClockwise, CaretLeft, CaretRight } from 'phosphor-svelte';

  /** @type {any[]} */
  let participantsList = $state([]);
  let selectedPersonId = $state('');
  let activePerson = $state(/** @type {any} */ (null));
  let isLoadingList = $state(true);
  let isLoadingDetail = $state(false);
  let errorMessage = $state('');
  let isListCollapsed = $state(false);

  /**
   * Carrega a lista consolidada de participantes do SQLite
   */
  async function loadParticipantsData() {
    isLoadingList = true;
    errorMessage = '';
    try {
      const data = await getParticipants();
      participantsList = data;

      if (data.length > 0 && !selectedPersonId) {
        await handleSelectPerson(data[0]);
      } else if (selectedPersonId) {
        const current = data.find((p) => p.person_id === selectedPersonId);
        if (current) await handleSelectPerson(current);
      }
    } catch (err) {
      console.error('Erro ao carregar lista de participantes:', err);
      errorMessage = err instanceof Error ? err.message : 'Falha ao conectar com o servidor.';
    } finally {
      isLoadingList = false;
    }
  }

  /**
   * Seleciona um participante e busca o dossiê detalhado completo
   * @param {any} person
   */
  async function handleSelectPerson(person) {
    if (!person?.person_id) return;
    selectedPersonId = person.person_id;
    isLoadingDetail = true;

    try {
      const detail = await getParticipantById(person.person_id);
      activePerson = detail;
    } catch (err) {
      console.error(`Erro ao buscar dossiê de ${person.person_id}:`, err);
      activePerson = person;
    } finally {
      isLoadingDetail = false;
    }
  }

  /**
   * Salva alterações cadastrais do participante
   * @param {any} updatedPerson
   */
  async function handleSavePerson(updatedPerson) {
    if (!updatedPerson?.person_id) return;

    try {
      const saved = await updateParticipant(updatedPerson.person_id, {
        name: updatedPerson.name,
        nickname: updatedPerson.nickname,
        document: updatedPerson.document,
        background: updatedPerson.background
      });
      activePerson = saved;

      // Atualiza linha na lista lateral
      const idx = participantsList.findIndex((p) => p.person_id === saved.person_id);
      if (idx !== -1) {
        participantsList[idx] = {
          ...participantsList[idx],
          name: saved.name,
          nickname: saved.nickname,
          document: saved.document,
          background: saved.background
        };
      }
    } catch (err) {
      console.error('Erro ao salvar participante:', err);
      alert(err instanceof Error ? `Erro ao salvar: ${err.message}` : 'Erro ao salvar alterações.');
    }
  }

  onMount(() => {
    loadParticipantsData();
  });
</script>

<svelte:head>
  <title>Participantes & Vínculos | ReadRelint Dashboard</title>
</svelte:head>

<div class="participants-page-wrapper">
  {#if errorMessage}
    <div class="error-banner">
      <Alert type="error" title="Erro de Comunicação com o Servidor">
        <p style="margin: 0 0 8px 0;">{errorMessage}</p>
        <Button variant="secondary" size="sm" onclick={loadParticipantsData}>
          {#snippet icon()}
            <ArrowsClockwise size={16} weight="bold" />
          {/snippet}
          TENTAR NOVAMENTE
        </Button>
      </Alert>
    </div>
  {/if}

  <div class="participants-master-detail-page" class:list-collapsed={isListCollapsed}>
    <!-- Coluna Esquerda: Lista de Pessoas -->
    <aside class="pane-left" class:collapsed={isListCollapsed}>
      <div class="pane-left-content">
        <ParticipantListPane 
          participants={participantsList} 
          selectedId={selectedPersonId} 
          onSelect={handleSelectPerson} 
        />
      </div>
    </aside>

    <!-- Botão de Recolhimento da Lista Lateral -->
    <button 
      class="collapse-toggle-btn"
      class:is-collapsed={isListCollapsed}
      onclick={() => isListCollapsed = !isListCollapsed}
      title={isListCollapsed ? "Expandir lista de participantes" : "Recolher lista"}
      aria-label="Alternar lista lateral"
    >
      {#if isListCollapsed}
        <CaretRight size={16} weight="bold" />
      {:else}
        <CaretLeft size={16} weight="bold" />
      {/if}
    </button>

    <!-- Coluna Direita: Dossiê Completo -->
    <div class="pane-right">
      {#if isLoadingDetail}
        <div class="loading-state">
          <ArrowsClockwise size={32} weight="bold" class="spinning" />
          <span>Carregando dossiê do participante...</span>
        </div>
      {:else if activePerson}
        {#key selectedPersonId}
          <div class="relint-enter-animation detail-transition-wrap">
            <ParticipantDetailPane 
              person={activePerson} 
              onSave={handleSavePerson} 
            />
          </div>
        {/key}
      {:else}
        <div class="empty-state">
          <span>Selecione um participante na lista para visualizar o dossiê.</span>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .participants-page-wrapper {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    height: 100%;
  }

  .error-banner {
    flex-shrink: 0;
  }

  .participants-master-detail-page {
    position: relative;
    display: grid;
    grid-template-columns: 30% 70%;
    height: calc(100vh - 64px - var(--space-6) * 2);
    background-color: var(--color-bg-surface-card);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-lg);
    overflow: hidden;
    transition: grid-template-columns var(--duration-normal) var(--ease-spring-snappy);
  }

  .participants-master-detail-page.list-collapsed {
    grid-template-columns: 0px 1fr;
  }

  .pane-left {
    height: 100%;
    overflow: hidden;
    transition: opacity var(--duration-fast) var(--ease-standard);
  }

  .pane-left.collapsed {
    opacity: 0;
    pointer-events: none;
  }

  .pane-left-content {
    width: 100%;
    height: 100%;
  }

  .collapse-toggle-btn {
    position: absolute;
    left: calc(30% - 12px);
    top: 50%;
    transform: translateY(-50%);
    width: 24px;
    height: 48px;
    background-color: var(--color-bg-surface-elevated);
    border: 1px solid var(--color-border-medium);
    border-radius: var(--radius-full);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-text-muted);
    cursor: pointer;
    z-index: 30;
    transition: 
      left var(--duration-normal) var(--ease-spring-snappy),
      background-color var(--duration-fast) var(--ease-standard),
      color var(--duration-fast) var(--ease-standard),
      border-color var(--duration-fast) var(--ease-standard);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  }

  .collapse-toggle-btn:hover {
    background-color: var(--color-bg-surface-card);
    color: var(--color-amber-primary);
    border-color: var(--color-amber-primary);
  }

  .collapse-toggle-btn.is-collapsed {
    left: 8px;
  }

  .pane-right {
    height: 100%;
    overflow: hidden;
    position: relative;
    min-width: 0;
  }

  .detail-transition-wrap {
    width: 100%;
    height: 100%;
    will-change: transform, opacity;
  }

  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--color-text-muted);
    font-size: var(--font-size-ui);
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: var(--space-3);
    color: var(--color-text-muted);
    font-size: var(--font-size-ui);
  }

  :global(.spinning) {
    animation: spin 1s linear infinite;
    color: var(--color-amber-primary);
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  @media (max-width: 992px) {
    .participants-master-detail-page {
      grid-template-columns: 1fr;
    }
    
    .pane-left {
      height: 300px;
    }
  }
</style>
