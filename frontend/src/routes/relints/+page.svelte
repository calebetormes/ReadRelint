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
  import { ArrowsClockwise, WarningCircle } from 'phosphor-svelte';

  /** @type {any[]} */
  let relintsList = $state([]);
  let selectedRelintId = $state('');
  let activeRelint = $state(/** @type {any} */ (null));
  let isLoadingList = $state(true);
  let isLoadingDetail = $state(false);
  let errorMessage = $state('');

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

  <div class="relints-master-detail-page">
    <div class="pane-left">
      <RelintListPane 
        relints={relintsList} 
        selectedId={selectedRelintId} 
        onSelect={handleSelectRelint} 
      />
    </div>

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
    display: grid;
    grid-template-columns: 320px 1fr;
    height: calc(100vh - 64px - var(--space-6) * 2);
    background-color: var(--color-bg-surface-card);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-lg);
    overflow: hidden;
  }

  .pane-left {
    height: 100%;
    overflow: hidden;
  }

  .pane-right {
    height: 100%;
    overflow: hidden;
    position: relative;
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
