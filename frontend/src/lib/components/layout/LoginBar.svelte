<!--
  ============================================================================
  ReadRelint - Barra de Login / Identificação do Operador
  ============================================================================
  Renderiza o crachá visual do operador no cabeçalho com indicador de plantão,
  foto/avatar, e abre o modal rápido para troca de operador ou encerramento.
  ============================================================================
-->
<script>
  import { authStore } from '$lib/stores/auth';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import { 
    UserCircle, 
    IdentificationCard, 
    SignOut, 
    SignIn, 
    Shield, 
    Buildings, 
    CheckCircle,
    CaretDown
  } from 'phosphor-svelte';

  let isModalOpen = $state(false);
  let editName = $state('');
  let editBadge = $state('');
  let editRole = $state('');
  let editUnit = $state('');

  function openLoginModal() {
    editName = $authStore.name;
    editBadge = $authStore.badge;
    editRole = $authStore.role;
    editUnit = $authStore.unit;
    isModalOpen = true;
  }

  function handleSaveLogin() {
    authStore.login({
      name: editName.trim() || 'Operador de Plantão',
      badge: editBadge.trim() || 'P2-0000',
      role: editRole.trim() || 'Analista de Inteligência',
      unit: editUnit.trim() || 'Seção de Inteligência'
    });
    isModalOpen = false;
  }

  function handleToggleAuth() {
    if ($authStore.isAuthenticated) {
      authStore.logout();
    } else {
      openLoginModal();
    }
  }
</script>

<div class="login-bar-container">
  {#if $authStore.isAuthenticated}
    <button 
      class="operator-badge-btn" 
      onclick={openLoginModal}
      title="Clique para editar operador ou trocar de plantão"
      aria-label="Perfil do Operador"
    >
      <div class="avatar-wrap">
        <div class="avatar-circle">
          <UserCircle size={28} weight="fill" color="var(--color-amber-primary)" />
        </div>
        <span class="status-indicator-dot" title={$authStore.status}></span>
      </div>

      <div class="operator-meta">
        <div class="name-row">
          <span class="operator-name">{$authStore.name}</span>
          <span class="operator-badge">{$authStore.badge}</span>
        </div>
        <span class="operator-role">{$authStore.unit} • {$authStore.role}</span>
      </div>

      <CaretDown size={14} weight="bold" class="caret-icon" />
    </button>
  {:else}
    <Button variant="primary" size="sm" onclick={openLoginModal}>
      {#snippet icon()}
        <SignIn size={16} weight="bold" />
      {/snippet}
      ENTRAR NO SISTEMA
    </Button>
  {/if}
</div>

<!-- Modal de Login / Troca de Operador -->
<Modal bind:open={isModalOpen} title="Identificação do Operador">
  <div class="login-modal-content">
    <div class="modal-banner">
      <div class="banner-icon">
        <Shield size={32} weight="fill" color="var(--color-amber-primary)" />
      </div>
      <div class="banner-text">
        <h4>Sessão de Inteligência Operacional</h4>
        <p>Identifique o analista responsável pela curadoria e extração dos RELINTs.</p>
      </div>
    </div>

    <form onsubmit={(e) => { e.preventDefault(); handleSaveLogin(); }} class="login-form">
      <Input
        label="NOME COMPLETO / GUERRA"
        placeholder="Ex: Capitão Silva"
        bind:value={editName}
      >
        {#snippet prefixIcon()}
          <IdentificationCard size={18} />
        {/snippet}
      </Input>


      <div class="form-row-grid">
        <Input
          label="MATRÍCULA / REGISTRO"
          placeholder="Ex: BM-84920"
          bind:value={editBadge}
        >
          {#snippet prefixIcon()}
            <Shield size={18} />
          {/snippet}
        </Input>

        <Input
          label="UNIDADE POLICIAL"
          placeholder="Ex: 2º BPM / P2"
          bind:value={editUnit}
        >
          {#snippet prefixIcon()}
            <Buildings size={18} />
          {/snippet}
        </Input>
      </div>

      <Input
        label="FUNÇÃO / CARGO"
        placeholder="Ex: Analista Chefe de Inteligência"
        bind:value={editRole}
      >
        {#snippet prefixIcon()}
          <CheckCircle size={18} />
        {/snippet}
      </Input>
    </form>
  </div>

  {#snippet footer()}
    <div class="modal-footer-actions">
      {#if $authStore.isAuthenticated}
        <Button 
          variant="danger" 
          size="sm" 
          onclick={() => { authStore.logout(); isModalOpen = false; }}
        >
          {#snippet icon()}
            <SignOut size={16} weight="bold" />
          {/snippet}
          DESCONECTAR
        </Button>
      {/if}
      <div class="spacer"></div>
      <Button variant="ghost" size="sm" onclick={() => isModalOpen = false}>
        CANCELAR
      </Button>
      <Button variant="primary" size="sm" onclick={handleSaveLogin}>
        {#snippet icon()}
          <CheckCircle size={16} weight="bold" />
        {/snippet}
        CONFIRMAR ACESSO
      </Button>
    </div>
  {/snippet}
</Modal>

<style>
  .login-bar-container {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .operator-badge-btn {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: 6px 14px 6px 10px;
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-full);
    cursor: pointer;
    text-align: left;
    transition: 
      background-color var(--duration-fast) var(--ease-standard),
      border-color var(--duration-fast) var(--ease-standard),
      box-shadow var(--duration-fast) var(--ease-standard),
      transform var(--duration-instant) var(--ease-spring-snappy);
  }

  .operator-badge-btn:hover {
    background-color: var(--color-bg-surface-elevated);
    border-color: rgba(224, 159, 62, 0.4);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.25), var(--glow-amber-subtle);
  }

  .operator-badge-btn:active {
    transform: scale(0.98);
  }

  .avatar-wrap {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 2px;
  }

  .avatar-circle {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-full);
    background-color: rgba(224, 159, 62, 0.12);
    border: 1px solid rgba(224, 159, 62, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .status-indicator-dot {
    position: absolute;
    bottom: 0px;
    right: 0px;
    width: 10px;
    height: 10px;
    border-radius: var(--radius-full);
    background-color: var(--color-functional-success);
    border: 2px solid #0D0D0D;
    box-shadow: 0 0 8px rgba(16, 185, 129, 0.8);
  }

  .operator-meta {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding-right: 4px;
  }

  .name-row {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }

  .operator-name {
    font-family: var(--font-family-main);
    font-size: var(--font-size-ui);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-main);
    line-height: 1.2;
    letter-spacing: -0.01em;
  }

  .operator-badge {
    font-family: var(--font-family-mono);
    font-size: 10px;
    font-weight: var(--font-weight-semibold);
    color: var(--color-amber-primary);
    background-color: rgba(224, 159, 62, 0.12);
    border: 1px solid rgba(224, 159, 62, 0.25);
    padding: 2px 6px;
    border-radius: var(--radius-xs);
    letter-spacing: 0.04em;
    line-height: 1;
  }

  .operator-role {
    font-family: var(--font-family-main);
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
    line-height: 1.2;
  }

  :global(.caret-icon) {
    color: var(--color-text-muted);
    margin-left: var(--space-2);
    transition: transform var(--duration-fast) var(--ease-standard), color var(--duration-fast) var(--ease-standard);
  }

  .operator-badge-btn:hover :global(.caret-icon) {
    color: var(--color-amber-primary);
  }



  /* Modal Layout */
  .login-modal-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-5);
  }

  .modal-banner {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-3) var(--space-4);
    background-color: rgba(224, 159, 62, 0.06);
    border: 1px solid rgba(224, 159, 62, 0.2);
    border-radius: var(--radius-default);
  }

  .banner-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .banner-text h4 {
    margin: 0 0 2px 0;
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-bold);
    color: var(--color-amber-primary);
  }

  .banner-text p {
    margin: 0;
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
  }

  .login-form {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .form-row-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-4);
  }

  .modal-footer-actions {
    display: flex;
    align-items: center;
    width: 100%;
    gap: var(--space-3);
  }

  .spacer {
    flex: 1;
  }

  @media (max-width: 768px) {
    .operator-role {
      display: none;
    }
    .form-row-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
