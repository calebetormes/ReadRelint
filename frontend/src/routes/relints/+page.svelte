<!--
  ============================================================================
  ReadRelint - Rota /relints (Página de Gerenciamento de RELINTs)
  ============================================================================
  Esta página orquestra o layout Master-Detail (30% / 70%) para visualização
  e edição dos Boletins RELINT consumindo os dados reais da API FastAPI.
  Possui carregamento assíncrono, feedback de erro e persistência automática.
  ============================================================================
-->
<script>
  import { onMount } from 'svelte';
  import RelintListPane from '$lib/components/relint/RelintListPane.svelte';
  import RelintDetailPane from '$lib/components/relint/RelintDetailPane.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { getRelints, getRelintById, updateRelint } from '$lib/services/relintsService';
  import { ArrowsClockwise, WarningCircle, CaretLeft, CaretRight, ListDashes } from 'phosphor-svelte';

  /** @type {any[]} */
  let relintsList = $state([]);
  let selectedRelintId = $state('');
  let activeRelint = $state(/** @type {any} */ (null));
  let isLoadingList = $state(true);
  let isLoadingDetail = $state(false);
  let errorMessage = $state('');
  let isListCollapsed = $state(false);

  /**
   * Carrega a lista inicial de RELINTs do banco de dados
   */
  async function loadRelintsData() {
    isLoadingList = true;
    errorMessage = '';
    try {
      const data = await getRelints();
      relintsList = data;
      
      // Se houver relatórios e nenhum selecionado, seleciona o primeiro
      if (data.length > 0 && !selectedRelintId) {
        await handleSelectRelint(data[0]);
      } else if (selectedRelintId) {
        const current = data.find((r) => r.id === selectedRelintId);
        if (current) await handleSelectRelint(current);
      }
    } catch (err) {
      console.error('Erro ao carregar lista de RELINTs:', err);
      errorMessage = err instanceof Error ? err.message : 'Falha ao conectar com a API FastAPI local.';
    } finally {
      isLoadingList = false;
    }
  }

  /**
   * Seleciona um relatório e busca o dossiê detalhado completo
   * @param {any} relint
   */
  async function handleSelectRelint(relint) {
    if (!relint?.id) return;
    selectedRelintId = relint.id;
    isLoadingDetail = true;
    
    try {
      const detail = await getRelintById(relint.id);
      activeRelint = detail;
    } catch (err) {
      console.error(`Erro ao buscar dossiê do RELINT ${relint.id}:`, err);
      // Fallback para os dados parciais que já temos na lista caso o detalhe falhe
      activeRelint = relint;
    } finally {
      isLoadingDetail = false;
    }
  }

  /**
   * Salva as alterações editadas no backend FastAPI
   * @param {any} updatedRelint
   */
  async function handleSaveRelint(updatedRelint) {
    if (!updatedRelint?.id) return;
    
    try {
      const saved = await updateRelint(updatedRelint.id, updatedRelint);
      activeRelint = saved;
      
      // Atualiza a linha correspondente na lista lateral
      const idx = relintsList.findIndex((r) => r.id === saved.id);
      if (idx !== -1) {
        relintsList[idx] = {
          ...relintsList[idx],
          subject: saved.subject,
          date_of_fact: saved.date_of_fact,
          bm_group: saved.bm_group,
          user_edited: true
        };
      }
    } catch (err) {
      console.error('Erro ao salvar RELINT:', err);
      alert(err instanceof Error ? `Erro ao salvar: ${err.message}` : 'Erro ao salvar alterações no banco.');
    }
  }

  onMount(() => {
    loadRelintsData();
  });
</script>

<svelte:head>
  <title>Boletins RELINT | ReadRelint Dashboard</title>
</svelte:head>

<div class="relints-page-wrapper">
  {#if errorMessage}
    <div class="error-banner">
      <Alert type="error" title="Erro de Comunicação com o Servidor">
        <p style="margin: 0 0 8px 0;">{errorMessage}</p>
        <Button variant="secondary" size="sm" onclick={loadRelintsData}>
          {#snippet icon()}
            <ArrowsClockwise size={16} weight="bold" />
          {/snippet}
          TENTAR NOVAMENTE
        </Button>
      </Alert>
    </div>
  {/if}

  <div class="relints-master-detail-page" class:list-collapsed={isListCollapsed}>
    <aside class="pane-left" class:collapsed={isListCollapsed}>
      <div class="pane-left-content">
        <RelintListPane 
          relints={relintsList} 
          selectedId={selectedRelintId} 
          onSelect={handleSelectRelint} 
        />
      </div>
    </aside>

    <!-- Botão Flutuante de Toggle da Lista Lateral -->
    <button 
      class="collapse-toggle-btn"
      class:is-collapsed={isListCollapsed}
      onclick={() => isListCollapsed = !isListCollapsed}
      title={isListCollapsed ? "Expandir lista de RELINTs (Ctrl + B)" : "Recolher lista para ampliar leitura"}
      aria-label="Alternar lista lateral"
    >
      {#if isListCollapsed}
        <CaretRight size={16} weight="bold" />
      {:else}
        <CaretLeft size={16} weight="bold" />
      {/if}
    </button>

    <div class="pane-right">
      {#if isLoadingDetail}
        <div class="loading-state">
          <ArrowsClockwise size={32} weight="bold" class="spinning" />
          <span>Carregando dossiê completo...</span>
        </div>
      {:else}
        <RelintDetailPane 
          relint={activeRelint} 
          onSave={handleSaveRelint} 
        />
      {/if}
    </div>
  </div>
</div>

<style>
  .relints-page-wrapper {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    height: 100%;
  }

  .error-banner {
    flex-shrink: 0;
  }

  .relints-master-detail-page {
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

  .relints-master-detail-page.list-collapsed {
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
    .relints-master-detail-page {
      grid-template-columns: 1fr;
    }
    
    .pane-left {
      height: 300px;
    }
  }
</style>
