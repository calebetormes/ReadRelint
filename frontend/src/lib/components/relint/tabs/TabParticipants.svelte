<script>
  import Badge from '$lib/components/ui/Badge.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import { 
    User, 
    Plus, 
    Trash, 
    Image, 
    UserList, 
    PencilSimple, 
    FloppyDisk, 
    FileText, 
    Clock, 
    MapPin, 
    WarningCircle,
    ArrowRight
  } from 'phosphor-svelte';
  import { getParticipantById, updateParticipant } from '$lib/services/participantsService';

  /** @type {{ relint: any, disabled?: boolean, onUpdate?: (relint: any) => void }} */
  let { relint, disabled = false, onUpdate } = $props();

  let showAddModal = $state(false);
  let showDossierModal = $state(false);
  let selectedParticipant = $state(/** @type {any} */ (null));
  let isEditingDossier = $state(false);
  let isSavingDossier = $state(false);

  let editName = $state('');
  let editNickname = $state('');
  let editDocument = $state('');
  let editBackground = $state('');

  let newName = $state('');
  let newAlias = $state('');
  let newRole = $state('Autor');

  /**
   * @param {string} role
   */
  function getRoleBadgeVariant(role) {
    if (role === 'Autor' || role === 'Suspeito' || role === 'Acusado') return 'error';
    if (role === 'Vítima') return 'warning';
    if (role === 'Testemunha') return 'info';
    return 'neutral';
  }

  /**
   * Abre o dossiê completo do participante ao clicar no card
   * @param {any} participant
   */
  async function handleOpenDossier(participant) {
    selectedParticipant = participant;
    editName = participant.name || '';
    editNickname = participant.nickname || participant.alias || '';
    editDocument = participant.document || '';
    editBackground = participant.background || '';
    isEditingDossier = false;
    showDossierModal = true;

    // Busca dados complementares do banco central de pessoas
    try {
      const searchKey = participant.document || participant.name;
      if (searchKey) {
        const full = await getParticipantById(searchKey);
        if (full) {
          selectedParticipant = { ...participant, ...full };
          editName = full.name || editName;
          editNickname = full.nickname || editNickname;
          editDocument = full.document || editDocument;
          editBackground = full.background || editBackground;
        }
      }
    } catch {
      // Usa dados locais do participante
    }
  }

  async function handleSaveDossier() {
    if (!selectedParticipant) return;
    isSavingDossier = true;

    const personKey = selectedParticipant.person_id || selectedParticipant.document || selectedParticipant.name;

    try {
      await updateParticipant(personKey, {
        name: editName.trim(),
        nickname: editNickname.trim(),
        document: editDocument.trim(),
        background: editBackground.trim()
      });

      // Atualiza o participante dentro do RELINT ativo
      selectedParticipant.name = editName;
      selectedParticipant.nickname = editNickname;
      selectedParticipant.document = editDocument;
      selectedParticipant.background = editBackground;

      const idx = relint.participants?.findIndex((/** @type {any} */ p) => p.name === selectedParticipant.name || p.id === selectedParticipant.id);
      if (idx !== -1 && relint.participants) {
        relint.participants[idx].name = editName;
        relint.participants[idx].alias = editNickname;
        relint.participants[idx].document = editDocument;
        relint.participants[idx].background = editBackground;
        if (onUpdate) onUpdate(relint);
      }

      isEditingDossier = false;
    } catch (err) {
      console.error('Erro ao salvar participante:', err);
      alert(err instanceof Error ? `Erro ao salvar: ${err.message}` : 'Erro ao salvar alterações no banco.');
    } finally {
      isSavingDossier = false;
    }
  }

  function handleAddParticipant() {
    if (!newName) return;
    if (!relint.participants) relint.participants = [];
    
    relint.participants.push({
      id: Date.now(),
      name: newName,
      alias: newAlias,
      nickname: newAlias,
      role: newRole,
      participation_type: newRole,
      photo_path: null
    });

    if (onUpdate) onUpdate(relint);

    newName = '';
    newAlias = '';
    newRole = 'Autor';
    showAddModal = false;
  }

  /**
   * @param {any} p
   * @param {Event} e
   */
  function handleRemoveParticipant(p, e) {
    e.stopPropagation();
    relint.participants = relint.participants.filter((/** @type {any} */ item) => item !== p && item.id !== p.id);
    if (onUpdate) onUpdate(relint);
  }
</script>

<div class="tab-participants">
  <div class="participants-header">
    <div class="header-info">
      <UserList size={22} weight="fill" color="var(--color-amber-primary)" />
      <span class="info-title">Indivíduos Qualificados e Envolvidos no RELINT ({relint.participants?.length || 0})</span>
    </div>
    
    {#if !disabled}
      <Button variant="secondary" size="sm" onclick={() => showAddModal = true}>
        {#snippet icon()}
          <Plus size={16} weight="bold" />
        {/snippet}
        ADICIONAR PARTICIPANTE
      </Button>
    {/if}
  </div>

  <div class="participants-grid">
    {#if relint.participants && relint.participants.length > 0}
      {#each relint.participants as p}
        <div 
          class="participant-card"
          role="button"
          tabindex="0"
          onclick={() => handleOpenDossier(p)}
          onkeydown={(e) => e.key === 'Enter' && handleOpenDossier(p)}
          title="Clique para abrir o dossiê completo e editar"
        >
          <div class="avatar-box">
            {#if p.photo_path}
              <img src={p.photo_path} alt={p.name} class="avatar-img" />
            {:else}
              <User size={32} weight="fill" color="var(--color-text-muted)" />
            {/if}
          </div>

          <div class="card-content">
            <div class="card-header">
              <span class="person-name">{p.name}</span>
              <!-- @ts-ignore -->
              <Badge variant={getRoleBadgeVariant(p.participation_type || p.role)} size="sm">{p.participation_type || p.role || 'Acusado'}</Badge>
            </div>
            
            {#if p.nickname || p.alias}
              <span class="person-alias">Vulgo: "{p.nickname || p.alias}"</span>
            {:else}
              <span class="person-alias text-muted">Sem alcunha cadastrada</span>
            {/if}

            {#if p.document}
              <span class="person-doc font-mono">Doc: {p.document}</span>
            {/if}

            {#if !disabled}
              <div class="card-actions">
                <button 
                  class="icon-action-btn danger" 
                  title="Remover do RELINT"
                  onclick={(e) => handleRemoveParticipant(p, e)}
                >
                  <Trash size={15} weight="bold" />
                </button>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    {:else}
      <div class="empty-state">
        <p>Nenhum participante extraído ou vinculado a este RELINT ainda.</p>
      </div>
    {/if}
  </div>
</div>

<!-- Modal de Dossiê e Edição do Participante -->
<Modal open={showDossierModal} title="Dossiê do Envolvido" onclose={() => showDossierModal = false}>
  {#if selectedParticipant}
    <div class="dossier-modal-wrap">
      <div class="modal-profile-header">
        <div class="modal-avatar">
          {#if selectedParticipant.photo_path}
            <img src={selectedParticipant.photo_path} alt={selectedParticipant.name} class="avatar-img" />
          {:else}
            <User size={36} weight="fill" color="var(--color-amber-primary)" />
          {/if}
        </div>
        <div class="modal-profile-info">
          <h3>{selectedParticipant.name}</h3>
          <div class="modal-sub-info">
            {#if selectedParticipant.linked_relints_count > 1}
              <Badge variant="warning" size="sm" dot>Reincidente ({selectedParticipant.linked_relints_count}x)</Badge>
            {:else}
              <Badge variant="neutral" size="sm">1 Ocorrência</Badge>
            {/if}
            <span class="badge-role">{selectedParticipant.participation_type || selectedParticipant.role || 'Acusado'}</span>
          </div>
        </div>
      </div>

      {#if isEditingDossier}
        <div class="dossier-edit-form">
          <Input label="NOME COMPLETO" bind:value={editName} />
          <Input label="VULGO / ALCUNHA" bind:value={editNickname} placeholder="ex: Nego / Carlinhos" />
          <Input label="DOCUMENTO (RG/CPF)" bind:value={editDocument} placeholder="ex: 1234567890" />
          
          <div class="form-group-full">
            <label class="field-label" for="part-antecedentes">ANTECEDENTES & OBSERVAÇÕES POLICIAIS</label>
            <textarea 
              id="part-antecedentes"
              class="custom-textarea" 
              rows="3" 
              bind:value={editBackground} 
              placeholder="Registros criminais, antecedentes, passagens anteriores..."
            ></textarea>
          </div>
        </div>
      {:else}
        <div class="dossier-view-fields">
          <div class="view-item">
            <span class="v-label">Nome Completo</span>
            <span class="v-val highlight">{selectedParticipant.name}</span>
          </div>
          <div class="view-item">
            <span class="v-label">Alcunha</span>
            <span class="v-val">{selectedParticipant.nickname || selectedParticipant.alias || '—'}</span>
          </div>
          <div class="view-item">
            <span class="v-label">Documento</span>
            <span class="v-val font-mono">{selectedParticipant.document || '—'}</span>
          </div>
          <div class="view-item full-width">
            <span class="v-label">Antecedentes Criminais</span>
            <div class="v-text-box">
              {selectedParticipant.background || 'Nenhum antecedente registrado.'}
            </div>
          </div>
        </div>

        {#if selectedParticipant.linked_relints && selectedParticipant.linked_relints.length > 0}
          <div class="linked-relints-section">
            <h4 class="section-title">Outras Ocorrências Vinculadas ({selectedParticipant.linked_relints.length})</h4>
            <div class="linked-list">
              {#each selectedParticipant.linked_relints as r}
                <div class="linked-item">
                  <FileText size={16} weight="fill" color="var(--color-amber-primary)" />
                  <span class="r-code font-mono">{r.source_file.replace(/\.pdf$/i, '')}</span>
                  <span class="r-subject">{r.subject}</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      {/if}
    </div>
  {/if}

  {#snippet footer()}
    {#if isEditingDossier}
      <Button variant="ghost" onclick={() => isEditingDossier = false} disabled={isSavingDossier}>CANCELAR</Button>
      <Button variant="primary" onclick={handleSaveDossier} disabled={isSavingDossier}>
        {#snippet icon()}
          <FloppyDisk size={16} weight="bold" />
        {/snippet}
        {isSavingDossier ? 'SALVANDO...' : 'SALVAR ALTERAÇÕES'}
      </Button>
    {:else}
      <Button variant="ghost" onclick={() => showDossierModal = false}>FECHAR</Button>
      <Button variant="secondary" onclick={() => isEditingDossier = true}>
        {#snippet icon()}
          <PencilSimple size={16} weight="bold" />
        {/snippet}
        EDITAR DADOS
      </Button>
    {/if}
  {/snippet}
</Modal>

<!-- Modal Adicionar Participante -->
<Modal open={showAddModal} title="Adicionar Participante ao RELINT" onclose={() => showAddModal = false}>
  <div class="modal-form">
    <Input label="NOME COMPLETO" bind:value={newName} placeholder="ex: Carlos Eduardo da Silva" />
    <Input label="ALCUNHA / APELIDO" bind:value={newAlias} placeholder="ex: Carlinhos / Nego" />
    
    <div class="form-group">
      <label class="field-label" for="participant-role">TIPO DE PARTICIPAÇÃO / PAPEL</label>
      <select id="participant-role" class="custom-select" bind:value={newRole}>
        <option value="Autor">Autor / Indiciado</option>
        <option value="Suspeito">Suspeito</option>
        <option value="Vítima">Vítima</option>
        <option value="Testemunha">Testemunha</option>
      </select>
    </div>
  </div>

  {#snippet footer()}
    <Button variant="ghost" onclick={() => showAddModal = false}>CANCELAR</Button>
    <Button variant="primary" onclick={handleAddParticipant}>CONFIRMAR E ADICIONAR</Button>
  {/snippet}
</Modal>


<style>
  .tab-participants {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-4) 0;
  }

  .participants-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: var(--color-bg-primary);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border-subtle);
  }

  .header-info {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .info-title {
    font-size: var(--font-size-ui);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-main);
  }

  .participants-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--space-4);
  }

  .participant-card {
    display: flex;
    align-items: flex-start;
    gap: var(--space-4);
    background-color: var(--color-bg-surface-card);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-default);
    padding: var(--space-4);
    transition: border-color var(--duration-fast) var(--ease-standard);
  }

  .participant-card:hover {
    border-color: var(--color-amber-primary);
  }

  .avatar-box {
    width: 48px;
    height: 48px;
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

  .card-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    min-width: 0;
  }

  .card-header {
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

  .person-alias {
    font-size: var(--font-size-xs);
    color: var(--color-amber-primary);
    font-weight: var(--font-weight-medium);
  }

  .text-muted {
    color: var(--color-text-muted);
  }

  .card-actions {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-top: var(--space-2);
  }

  .icon-action-btn {
    background: transparent;
    border: none;
    color: var(--color-text-muted);
    cursor: pointer;
    padding: var(--space-1);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color var(--duration-fast) var(--ease-standard);
  }

  .icon-action-btn:hover {
    color: var(--color-text-main);
    background-color: var(--color-surface-hover);
  }

  .icon-action-btn.danger:hover {
    color: var(--color-functional-error);
  }

  .empty-state {
    grid-column: 1 / -1;
    padding: var(--space-6);
    text-align: center;
    color: var(--color-text-muted);
    border: 1px dashed var(--color-border-medium);
    border-radius: var(--radius-default);
  }

  .modal-form {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-2) 0;
  }

  .field-label {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-muted);
    display: block;
    margin-bottom: var(--space-2);
  }

  .custom-select {
    width: 100%;
    height: 40px;
    background-color: var(--color-bg-primary);
    border: 1px solid var(--color-border-medium);
    border-radius: var(--radius-sm);
    color: var(--color-text-main);
    padding: 0 var(--space-3);
    font-size: var(--font-size-ui);
    outline: none;
  }

  /* Estilos do Modal de Dossiê */
  .dossier-modal-wrap {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .modal-profile-header {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding-bottom: var(--space-3);
    border-bottom: 1px solid var(--color-border-subtle);
  }

  .modal-avatar {
    width: 52px;
    height: 52px;
    border-radius: var(--radius-full);
    background-color: var(--color-bg-primary);
    border: 2px solid var(--color-amber-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    flex-shrink: 0;
  }

  .modal-profile-info h3 {
    margin: 0 0 4px 0;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-main);
  }

  .modal-sub-info {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  .badge-role {
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
    font-family: var(--font-family-mono);
  }

  .dossier-edit-form {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .form-group-full {
    display: flex;
    flex-direction: column;
    gap: 4px;
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
    resize: vertical;
    outline: none;
    box-sizing: border-box;
  }

  .dossier-view-fields {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3);
  }

  .view-item {
    display: flex;
    flex-direction: column;
    gap: 2px;
    background-color: var(--color-bg-secondary);
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border-subtle);
  }

  .view-item.full-width {
    grid-column: 1 / -1;
  }

  .v-label {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-muted);
    text-transform: uppercase;
  }

  .v-val {
    font-size: var(--font-size-ui);
    color: var(--color-text-main);
  }

  .v-val.highlight {
    color: var(--color-amber-primary);
    font-weight: var(--font-weight-bold);
  }

  .v-text-box {
    font-size: var(--font-size-ui);
    line-height: var(--line-height-20);
    color: var(--color-text-main);
    padding-top: 2px;
    white-space: pre-wrap;
  }

  .linked-relints-section {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    margin-top: var(--space-2);
  }

  .section-title {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-muted);
    text-transform: uppercase;
    margin: 0;
  }

  .linked-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-height: 140px;
    overflow-y: auto;
  }

  .linked-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: 6px 10px;
    background-color: var(--color-bg-secondary);
    border-radius: var(--radius-xs);
    border: 1px solid var(--color-border-subtle);
    font-size: var(--font-size-xs);
  }

  .r-code {
    color: var(--color-amber-primary);
    font-weight: var(--font-weight-semibold);
  }

  .r-subject {
    color: var(--color-text-main);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>

