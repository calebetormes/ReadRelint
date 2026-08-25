<script>
  import Tabs from '$lib/components/ui/Tabs.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import { 
    CheckCircle, 
    Clock,
    FloppyDisk, 
    PencilSimple, 
    FileText, 
    Info, 
    MapPin, 
    Shield, 
    UserList, 
    Article,
    CalendarBlank,
    Buildings,
    Sparkle,
    Cpu,
    Hash
  } from 'phosphor-svelte';

  import TabGeneral from './tabs/TabGeneral.svelte';
  import TabLocation from './tabs/TabLocation.svelte';
  import TabSpecialty from './tabs/TabSpecialty.svelte';
  import TabParticipants from './tabs/TabParticipants.svelte';
  import TabTranscription from './tabs/TabTranscription.svelte';

  /** @type {{ relint: any, onSave?: (relint: any) => void }} */
  let { relint, onSave } = $props();

  let activeTab = $state('geral');
  let isEditing = $state(false);
  let isSaving = $state(false);

  // Quando trocar de relint, voltar para modo leitura por padrão
  $effect(() => {
    if (relint?.id) {
      isEditing = false;
    }
  });

  function isLlmMethod(method) {
    const m = String(method || '').toLowerCase();
    return (m.includes('ollama') || m.includes('ia')) && !m.includes('sem ia') && !m.includes('regex');
  }

  function handleButtonClick() {
    if (!isEditing) {
      isEditing = true;
    } else {
      isSaving = true;
      relint.user_edited = true;
      if (onSave) onSave(relint);
      setTimeout(() => {
        isSaving = false;
        isEditing = false;
      }, 400);
    }
  }

  const tabsItems = [
    { id: 'geral', label: 'Síntese', icon: iconSparkle },
    { id: 'localizacao', label: 'Localização', icon: iconMapPin },
    { id: 'especialidade', label: 'Especialidade', icon: iconShield },
    { id: 'participantes', label: 'Participantes', icon: iconUserList },
    { id: 'transcricao', label: 'Transcrição', icon: iconArticle }
  ];
</script>

{#snippet iconSparkle()} <Sparkle size={16} weight="fill" /> {/snippet}
{#snippet iconMapPin()} <MapPin size={16} weight="fill" /> {/snippet}
{#snippet iconShield()} <Shield size={16} weight="fill" /> {/snippet}
{#snippet iconUserList()} <UserList size={16} weight="fill" /> {/snippet}
{#snippet iconArticle()} <Article size={16} weight="fill" /> {/snippet}

<div class="detail-pane">
  {#if relint}
    <!-- Header de Ações do Relatório Ativo -->
    <div class="detail-header">
      <div class="header-titles">
        <div class="code-row">
          <span class="relint-code font-mono">{relint.code}</span>
          
          {#if isEditing}
            <Badge variant="amber" size="sm" dot>Modo Edição Ativo</Badge>
          {/if}
        </div>

        <h2 class="relint-subject">{relint.subject || 'Sem assunto definido'}</h2>

        <!-- Barra de Metadados Rápida -->
        <div class="header-meta-bar">
          {#if relint.date_of_fact}
            <div class="meta-item" title="Data do Fato">
              <CalendarBlank size={14} weight="bold" color="var(--color-text-muted)" />
              <span>{relint.date_of_fact}</span>
            </div>
          {/if}

          {#if relint.municipality && relint.municipality !== 'Não Informado' && relint.municipality !== 'N/I'}
            <div class="meta-item" title="Município">
              <MapPin size={14} weight="bold" color="var(--color-text-muted)" />
              <span>{relint.municipality}</span>
            </div>
          {/if}

          {#if relint.police_unit}
            <div class="meta-item" title="Unidade Policial">
              <Buildings size={14} weight="bold" color="var(--color-text-muted)" />
              <span>{relint.police_unit}</span>
            </div>
          {/if}

          <!-- Método de Extração Apenas com Ícone -->
          <div class="meta-item">
            {#if isLlmMethod(relint.extraction_method)}
              <span class="extraction-icon-pill is-ia" title="Extraído com Inteligência Artificial (Ollama)">
                <Sparkle size={13} weight="fill" />
              </span>
            {:else}
              <span class="extraction-icon-pill is-regex" title="Extraído deterministicamente sem IA (Regex)">
                <Cpu size={13} weight="bold" />
              </span>
            {/if}
          </div>
        </div>
      </div>

      <div class="header-actions">
        <Button variant={isEditing ? "primary" : "secondary"} size="md" onclick={handleButtonClick}>
          {#snippet icon()}
            {#if isEditing}
              <FloppyDisk size={16} weight="bold" />
            {:else}
              <PencilSimple size={16} weight="bold" />
            {/if}
          {/snippet}
          {#if isEditing}
            {isSaving ? 'SALVANDO...' : 'SALVAR E REVISAR'}
          {:else}
            EDITAR
          {/if}
        </Button>

        <!-- Status de Revisão como Alerta Compacto Abaixo do Botão -->
        <div class="status-alert-box">
          {#if relint.user_edited}
            <span class="status-pill is-success" title="Relatório revisado por curadoria humana">
              <CheckCircle size={13} weight="fill" />
              <span>Revisado</span>
            </span>
          {:else}
            <span class="status-pill is-warning" title="Aguardando validação humana">
              <Clock size={13} weight="bold" />
              <span>Pendente Revisão</span>
            </span>
          {/if}
        </div>
      </div>
    </div>

    <!-- Navegação de Abas do Dossiê -->
    <div class="tabs-wrapper">
      <Tabs tabs={tabsItems} bind:activeTab />
    </div>

    <!-- Conteúdo Dinâmico por Aba -->
    <div class="tab-content-area" class:is-disabled-read-only={!isEditing}>
      {#if activeTab === 'geral'}
        <TabGeneral {relint} disabled={!isEditing} />
      {:else if activeTab === 'localizacao'}
        <TabLocation {relint} disabled={!isEditing} />
      {:else if activeTab === 'especialidade'}
        <TabSpecialty {relint} disabled={!isEditing} />
      {:else if activeTab === 'participantes'}
        <TabParticipants {relint} disabled={!isEditing} />
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
    flex: 1;
    min-width: 0;
  }

  .code-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .relint-code {
    font-size: 11px;
    font-weight: var(--font-weight-medium);
    color: var(--color-amber-primary);
    letter-spacing: 0.2px;
    opacity: 0.9;
  }

  .relint-subject {
    font-size: 18px;
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-main);
    margin: 0;
    line-height: var(--line-height-140);
    letter-spacing: -0.2px;
  }

  .header-meta-bar {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    flex-wrap: wrap;
    margin-top: 4px;
  }

  .meta-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
  }

  .meta-item span {
    color: var(--color-text-main);
    font-size: 12px;
  }

  .extraction-icon-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: var(--radius-sm);
    cursor: default;
    transition: all var(--duration-fast) var(--ease-standard);
  }

  .extraction-icon-pill.is-ia {
    color: #10b981;
    background-color: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.25);
  }

  .extraction-icon-pill.is-regex {
    color: #f59e0b;
    background-color: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.25);
  }

  .header-actions {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: var(--space-2);
    flex-shrink: 0;
  }

  .status-alert-box {
    display: flex;
    align-items: center;
  }

  .status-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 8px;
    border-radius: var(--radius-sm);
    font-size: 11px;
    font-weight: var(--font-weight-semibold);
    letter-spacing: 0.2px;
    text-transform: uppercase;
    transition: all var(--duration-fast) var(--ease-standard);
  }

  .status-pill.is-warning {
    color: #fbbf24;
    background-color: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.25);
  }

  .status-pill.is-success {
    color: #34d399;
    background-color: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.25);
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
