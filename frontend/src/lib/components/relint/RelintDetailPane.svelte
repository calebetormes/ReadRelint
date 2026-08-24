<script>
  import Tabs from '$lib/components/ui/Tabs.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import { CheckCircle, FloppyDisk, FileText } from 'phosphor-svelte';

  import TabGeneral from './tabs/TabGeneral.svelte';
  import TabLocation from './tabs/TabLocation.svelte';
  import TabSpecialty from './tabs/TabSpecialty.svelte';
  import TabParticipants from './tabs/TabParticipants.svelte';
  import TabTranscription from './tabs/TabTranscription.svelte';

  /** @type {{ relint: any, onSave?: (relint: any) => void }} */
  let { relint, onSave } = $props();

  let activeTab = $state('geral');
  let isSaving = $state(false);

  const tabsItems = [
    { id: 'geral', label: '1. Geral' },
    { id: 'localizacao', label: '2. Localização' },
    { id: 'especialidade', label: '3. Especialidade' },
    { id: 'participantes', label: '4. Participantes' },
    { id: 'transcricao', label: '5. Transcrição' }
  ];

  function handleSave() {
    isSaving = true;
    relint.user_edited = true;
    if (onSave) onSave(relint);
    setTimeout(() => isSaving = false, 600);
  }
</script>

<div class="detail-pane">
  {#if relint}
    <!-- Header de Ações do Relatório Ativo -->
    <div class="detail-header">
      <div class="header-titles">
        <div class="code-row">
          <span class="relint-code font-mono">{relint.code}</span>
          {#if relint.user_edited}
            <Badge variant="success" size="sm">
              {#snippet icon()}
                <CheckCircle size={14} weight="fill" />
              {/snippet}
              Revisado
            </Badge>
          {:else}
            <Badge variant="neutral" size="sm">Pendente Revisão</Badge>
          {/if}
        </div>
        <h2 class="relint-subject">{relint.subject || 'Sem assunto definido'}</h2>
      </div>

      <div class="header-actions">
        <Button variant="primary" size="md" onclick={handleSave}>
          {#snippet icon()}
            <FloppyDisk size={18} weight="bold" />
          {/snippet}
          {isSaving ? 'SALVANDO...' : 'SALVAR E MARCAR REVISADO'}
        </Button>
      </div>
    </div>

    <!-- Navegação de Abas do Dossiê -->
    <div class="tabs-wrapper">
      <Tabs tabs={tabsItems} bind:activeTab />
    </div>

    <!-- Conteúdo Dinâmico por Aba -->
    <div class="tab-content-area">
      {#if activeTab === 'geral'}
        <TabGeneral {relint} />
      {:else if activeTab === 'localizacao'}
        <TabLocation {relint} />
      {:else if activeTab === 'especialidade'}
        <TabSpecialty {relint} />
      {:else if activeTab === 'participantes'}
        <TabParticipants {relint} />
      {:else if activeTab === 'transcricao'}
        <TabTranscription {relint} />
      {/if}
    </div>
  {:else}
    <div class="no-selection">
      <FileText size={48} weight="fill" color="var(--color-border-medium)" />
      <h3>Nenhum RELINT selecionado</h3>
      <p>Selecione um relatório na lista à esquerda para inspecionar e gerenciar os dados.</p>
    </div>
  {/if}
</div>

<style>
  .detail-pane {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: var(--color-bg-primary);
    padding: var(--space-6);
    box-sizing: border-box;
    overflow-y: auto;
  }

  .detail-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--space-4);
    padding-bottom: var(--space-4);
    border-bottom: 1px solid var(--color-border-subtle);
  }

  .header-titles {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .code-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .relint-code {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-bold);
    color: var(--color-amber-primary);
  }

  .relint-subject {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-main);
    margin: 0;
  }

  .tabs-wrapper {
    margin-top: var(--space-4);
  }

  .tab-content-area {
    flex: 1;
    margin-top: var(--space-2);
  }

  .font-mono {
    font-family: var(--font-family-mono);
  }

  .no-selection {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: var(--space-3);
    color: var(--color-text-muted);
    text-align: center;
  }

  .no-selection h3 {
    color: var(--color-text-main);
    margin: 0;
  }
  
  .no-selection p {
    margin: 0;
    max-width: 320px;
    font-size: var(--font-size-ui);
  }
</style>
