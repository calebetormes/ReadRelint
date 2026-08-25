<!--
  ============================================================================
  ReadRelint - Painel Detalhado de Dossiê do Participante (Detail Pane 70%)
  ============================================================================
  Exibe a qualificação completa do investigado, fotos, antecedentes criminais
  e o histórico de todos os RELINTs onde o indivíduo foi citado.
  ============================================================================
-->
<script>
  import Button from '$lib/components/ui/Button.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import { 
    User, 
    PencilSimple, 
    FloppyDisk, 
    IdentificationCard, 
    FileText, 
    Clock, 
    MapPin, 
    Images, 
    ArrowRight,
    WarningCircle,
    CheckCircle,
    UserCircle
  } from 'phosphor-svelte';

  /** @type {{ person: any, onSave?: (updatedPerson: any) => void }} */
  let { person, onSave } = $props();

  let isEditing = $state(false);
  let isSaving = $state(false);

  let editName = $state('');
  let editNickname = $state('');
  let editDocument = $state('');
  let editBackground = $state('');

  // Sincroniza formulário ao mudar de pessoa
  $effect(() => {
    if (person?.person_id) {
      editName = person.name || '';
      editNickname = person.nickname || '';
      editDocument = person.document || '';
      editBackground = person.background || '';
      isEditing = false;
    }
  });

  async function handleToggleEdit() {
    if (!isEditing) {
      isEditing = true;
    } else {
      isSaving = true;
      const updated = {
        ...person,
        name: editName.trim() || person.name,
        nickname: editNickname.trim(),
        document: editDocument.trim(),
        background: editBackground.trim()
      };

      if (onSave) {
        await onSave(updated);
      }
      isSaving = false;
      isEditing = false;
    }
  }

  function handleCancelEdit() {
    editName = person.name || '';
    editNickname = person.nickname || '';
    editDocument = person.document || '';
    editBackground = person.background || '';
    isEditing = false;
  }
</script>

<div class="participant-detail-pane">
  {#if person}
    <!-- Header do Dossiê -->
    <div class="dossier-header">
      <div class="header-main-info">
        <div class="large-avatar-box">
          {#if person.photo_path}
            <img src={person.photo_path} alt={person.name} class="large-avatar-img" />
          {:else}
            <User size={44} weight="fill" color="var(--color-amber-primary)" />
          {/if}
        </div>

        <div class="header-text-block">
          <div class="name-badge-row">
            <h1 class="dossier-name">{person.name}</h1>
            {#if person.linked_relints_count > 1}
              <Badge variant="warning" size="md" dot>Reincidente ({person.linked_relints_count}x)</Badge>
            {:else}
              <Badge variant="neutral" size="md">Primário (1x)</Badge>
            {/if}
          </div>

          <div class="sub-info-row">
            {#if person.nickname}
              <span class="sub-nickname">Vulgo: <strong>{person.nickname}</strong></span>
            {/if}
            {#if person.document}
              <span class="sub-doc">Doc: <strong class="font-mono">{person.document}</strong></span>
            {/if}
            <span class="sub-id font-mono">ID: {person.person_id}</span>
          </div>
        </div>
      </div>

      <!-- Ações do Header -->
      <div class="header-actions">
        {#if isEditing}
          <Button variant="ghost" size="sm" onclick={handleCancelEdit} disabled={isSaving}>
            CANCELAR
          </Button>
        {/if}
        <Button 
          variant={isEditing ? 'primary' : 'secondary'} 
          size="sm" 
          onclick={handleToggleEdit}
          disabled={isSaving}
        >
          {#snippet icon()}
            {#if isEditing}
              <FloppyDisk size={16} weight="bold" />
            {:else}
              <PencilSimple size={16} weight="bold" />
            {/if}
          {/snippet}
          {isEditing ? (isSaving ? 'SALVANDO...' : 'SALVAR ALTERAÇÕES') : 'EDITAR CADASTRO'}
        </Button>
      </div>
    </div>

    <!-- Conteúdo em Seções / Cards -->
    <div class="dossier-body">
      <!-- Seção 1: Dados Qualificatórios -->
      <Card variant="elevated" title="Qualificação e Dados Cadastrais">
        {#if isEditing}
          <div class="edit-form-grid">
            <Input label="NOME COMPLETO" bind:value={editName} />
            <Input label="VULGO / ALCUNHA" bind:value={editNickname} placeholder="ex: Carlinhos / Nego" />
            <Input label="DOCUMENTO (RG / CPF)" bind:value={editDocument} placeholder="ex: 1234567890" />
            <div class="form-full-row">
              <label class="field-label" for="edit-background">ANTECEDENTES / OBSERVAÇÕES POLICIAIS</label>
              <textarea 
                id="edit-background"
                class="custom-textarea" 
                rows="4" 
                bind:value={editBackground} 
                placeholder="Registros criminais, passagens anteriores, facção..."
              ></textarea>
            </div>
          </div>
        {:else}
          <div class="read-only-grid">
            <div class="info-block">
              <span class="info-label">Nome Completo</span>
              <span class="info-value highlight">{person.name}</span>
            </div>
            <div class="info-block">
              <span class="info-label">Alcunha / Vulgo</span>
              <span class="info-value">{person.nickname || '—'}</span>
            </div>
            <div class="info-block">
              <span class="info-label">Documento de Identificação</span>
              <span class="info-value font-mono">{person.document || '—'}</span>
            </div>
            <div class="info-block full-width">
              <span class="info-label">Antecedentes & Histórico Criminal</span>
              <div class="background-box">
                {person.background || 'Nenhum antecedente criminal ou observação registrada para este indivíduo.'}
              </div>
            </div>
          </div>
        {/if}
      </Card>

      <!-- Seção 2: Galeria de Fotos Extraídas -->
      {#if person.photos && person.photos.length > 0}
        <Card variant="base" title="Galeria de Fotos do Investigado ({person.photos.length})">
          <div class="photos-grid">
            {#each person.photos as photo}
              <div class="photo-card">
                <img src={photo} alt="Foto do Investigado" class="photo-img" />
              </div>
            {/each}
          </div>
        </Card>
      {/if}


      <!-- Seção 3: Histórico de RELINTs Vinculados -->
      <Card variant="elevated" title="Ocorrências & Boletins Vinculados ({person.linked_relints?.length || 0})">
        <div class="relints-history-list">
          {#if person.linked_relints && person.linked_relints.length > 0}
            {#each person.linked_relints as relint}
              <div class="relint-history-card">
                <div class="relint-icon-col">
                  <FileText size={24} weight="fill" color="var(--color-amber-primary)" />
                </div>

                <div class="relint-details-col">
                  <div class="relint-top-meta">
                    <span class="relint-code font-mono">{relint.source_file.replace(/\.pdf$/i, '')}</span>
                    <Badge variant="neutral" size="sm">{relint.participation_type || 'Acusado'}</Badge>
                    {#if relint.municipality}
                      <span class="relint-muni">
                        <MapPin size={12} weight="fill" />
                        {relint.municipality}
                      </span>
                    {/if}
                    {#if relint.date_of_fact}
                      <span class="relint-date">
                        <Clock size={12} weight="bold" />
                        {relint.date_of_fact}
                      </span>
                    {/if}
                  </div>

                  <p class="relint-subject">{relint.subject || 'Sem descrição de assunto.'}</p>
                </div>

                <div class="relint-action-col">
                  <a href="/relints" class="action-link">
                    <Button variant="ghost" size="sm">
                      {#snippet icon()}
                        <ArrowRight size={14} weight="bold" />
                      {/snippet}
                      VER RELINT
                    </Button>
                  </a>
                </div>
              </div>
            {/each}
          {:else}
            <div class="empty-history">
              <p>Nenhuma ocorrência registrada no histórico.</p>
            </div>
          {/if}
        </div>
      </Card>
    </div>
  {:else}
    <div class="no-selection-placeholder">
      <UserCircle size={56} weight="thin" color="var(--color-text-muted)" />
      <h3>Nenhum participante selecionado</h3>
      <p>Selecione um indivíduo na coluna esquerda para abrir o dossiê completo.</p>
    </div>
  {/if}
</div>

<style>
  .participant-detail-pane {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: auto;
    background-color: var(--color-bg-primary);
    box-sizing: border-box;
  }

  .dossier-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-6);
    background-color: var(--color-bg-surface-card);
    border-bottom: 1px solid var(--color-border-subtle);
    gap: var(--space-4);
    position: sticky;
    top: 0;
    z-index: 20;
  }

  .header-main-info {
    display: flex;
    align-items: center;
    gap: var(--space-5);
  }

  .large-avatar-box {
    width: 64px;
    height: 64px;
    border-radius: var(--radius-full);
    background-color: var(--color-bg-secondary);
    border: 2px solid var(--color-amber-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    flex-shrink: 0;
    box-shadow: 0 0 16px rgba(224, 159, 62, 0.2);
  }

  .large-avatar-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .header-text-block {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .name-badge-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .dossier-name {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-main);
    margin: 0;
    letter-spacing: var(--letter-spacing-tight);
  }

  .sub-info-row {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
  }

  .sub-nickname strong {
    color: var(--color-amber-primary);
  }

  .sub-doc strong {
    color: var(--color-text-main);
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .dossier-body {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
    padding: var(--space-6);
  }

  .edit-form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: var(--space-4);
  }

  .form-full-row {
    grid-column: 1 / -1;
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .field-label {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-muted);
    letter-spacing: var(--letter-spacing-wide);
  }

  .custom-textarea {
    width: 100%;
    background-color: var(--color-bg-tertiary);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-default);
    color: var(--color-text-main);
    padding: var(--space-3);
    font-family: inherit;
    font-size: var(--font-size-base);
    line-height: var(--line-height-24);
    resize: vertical;
    outline: none;
    box-sizing: border-box;
  }

  .custom-textarea:focus {
    border-color: var(--color-border-focus);
    box-shadow: 0 0 0 3px rgba(224, 159, 62, 0.2);
  }

  .read-only-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-4);
  }

  .info-block {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    background-color: var(--color-bg-secondary);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border-subtle);
  }

  .info-block.full-width {
    grid-column: 1 / -1;
  }

  .info-label {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: var(--letter-spacing-wide);
  }

  .info-value {
    font-size: var(--font-size-base);
    color: var(--color-text-main);
  }

  .info-value.highlight {
    font-weight: var(--font-weight-bold);
    color: var(--color-amber-primary);
  }

  .background-box {
    font-size: var(--font-size-base);
    line-height: var(--line-height-24);
    color: var(--color-text-main);
    padding-top: var(--space-1);
    white-space: pre-wrap;
  }

  .photos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: var(--space-3);
  }

  .photo-card {
    height: 140px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border-subtle);
    overflow: hidden;
    background-color: var(--color-bg-primary);
  }

  .photo-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .relints-history-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .relint-history-card {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-4);
    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-default);
    transition: border-color var(--duration-fast) var(--ease-standard);
  }

  .relint-history-card:hover {
    border-color: var(--color-border-medium);
  }

  .relint-icon-col {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .relint-details-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
  }

  .relint-top-meta {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .relint-code {
    font-size: var(--font-size-ui);
    font-weight: var(--font-weight-bold);
    color: var(--color-amber-primary);
  }

  .relint-muni, .relint-date {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
  }

  .relint-subject {
    font-size: var(--font-size-ui);
    color: var(--color-text-main);
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .action-link {
    text-decoration: none;
  }

  .font-mono {
    font-family: var(--font-family-mono);
  }

  .no-selection-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: var(--space-12);
    text-align: center;
    color: var(--color-text-muted);
    gap: var(--space-3);
  }

  .no-selection-placeholder h3 {
    margin: 0;
    color: var(--color-text-main);
    font-size: var(--font-size-lg);
  }

  .no-selection-placeholder p {
    margin: 0;
    font-size: var(--font-size-ui);
  }

  @media (max-width: 992px) {
    .dossier-header {
      flex-direction: column;
      align-items: flex-start;
    }
    .edit-form-grid, .read-only-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
