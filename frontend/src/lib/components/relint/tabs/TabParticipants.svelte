<script>
  import Badge from '$lib/components/ui/Badge.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import { User, Plus, Trash, Image, UserList } from 'phosphor-svelte';

  /** @type {{ relint: any, onUpdate?: (relint: any) => void }} */
  let { relint, onUpdate } = $props();

  let showAddModal = $state(false);
  let newName = $state('');
  let newAlias = $state('');
  let newRole = $state('Autor');

  /**
   * @param {string} role
   */
  function getRoleBadgeVariant(role) {
    if (role === 'Autor' || role === 'Suspeito') return 'error';
    if (role === 'Vítima') return 'warning';
    if (role === 'Testemunha') return 'info';
    return 'neutral';
  }

  function handleAddParticipant() {
    if (!newName) return;
    if (!relint.participants) relint.participants = [];
    
    relint.participants.push({
      id: Date.now(),
      name: newName,
      alias: newAlias,
      role: newRole,
      photo_path: null
    });

    if (onUpdate) onUpdate(relint);

    newName = '';
    newAlias = '';
    newRole = 'Autor';
    showAddModal = false;
  }

  /**
   * @param {number} id
   */
  function handleRemoveParticipant(id) {
    relint.participants = relint.participants.filter((/** @type {any} */ p) => p.id !== id);
    if (onUpdate) onUpdate(relint);
  }
</script>

<div class="tab-participants">
  <div class="participants-header">
    <div class="header-info">
      <UserList size={22} weight="fill" color="var(--color-amber-primary)" />
      <span class="info-title">Indivíduos Qualificados e Envolvidos no RELINT ({relint.participants?.length || 0})</span>
    </div>
    
    <Button variant="secondary" size="sm" onclick={() => showAddModal = true}>
      {#snippet icon()}
        <Plus size={16} weight="bold" />
      {/snippet}
      ADICIONAR PARTICIPANTE
    </Button>
  </div>

  <div class="participants-grid">
    {#if relint.participants && relint.participants.length > 0}
      {#each relint.participants as p}
        <div class="participant-card">
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
              <Badge variant={getRoleBadgeVariant(p.role)} size="sm">{p.role}</Badge>
            </div>
            
            {#if p.alias}
              <span class="person-alias">Alcunha: "{p.alias}"</span>
            {:else}
              <span class="person-alias text-muted">Sem alcunha cadastrada</span>
            {/if}

            <div class="card-actions">
              <button class="icon-action-btn" title="Vincular foto do PDF">
                <Image size={16} weight="bold" />
              </button>
              <button 
                class="icon-action-btn danger" 
                title="Remover do RELINT"
                onclick={() => handleRemoveParticipant(p.id)}
              >
                <Trash size={16} weight="bold" />
              </button>
            </div>
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
</style>
