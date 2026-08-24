<script>
  /** @type {{ open?: boolean, title?: string, onclose?: () => void, header?: import('svelte').Snippet, footer?: import('svelte').Snippet, children?: import('svelte').Snippet }} */
  let {
    open = $bindable(false),
    title = '',
    onclose,
    header,
    footer,
    children
  } = $props();

  function close() {
    open = false;
    if (onclose) onclose();
  }

  /** @param {KeyboardEvent} e */
  function handleKeydown(e) {
    if (e.key === 'Escape' && open) close();
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
  <div class="modal-backdrop" onclick={close} role="presentation">
    <div
      class="modal-container"
      role="dialog"
      aria-modal="true"
      tabindex="-1"
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => e.stopPropagation()}
    >
      <div class="modal-header">
        {#if header}
          {@render header()}
        {:else if title}
          <h3 class="modal-title">{title}</h3>
        {/if}
        <button
          type="button"
          class="modal-close-btn"
          onclick={close}
          aria-label="Fechar modal"
        >
          &times;
        </button>
      </div>

      {#if children}
        <div class="modal-body">
          {@render children()}
        </div>
      {/if}

      {#if footer}
        <div class="modal-footer">
          {@render footer()}
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    z-index: var(--z-modal);
    background-color: var(--color-bg-surface-overlay);
    backdrop-filter: var(--backdrop-blur-md);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-4);
    animation: modal-fade 0.2s var(--ease-standard);
  }

  .modal-container {
    width: 100%;
    max-width: 540px;
    background-color: var(--color-bg-surface-elevated);
    border: 1px solid var(--color-border-medium);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-modal);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    animation: modal-pop 0.25s var(--ease-spring-smooth);
    outline: none;
  }

  .modal-header {
    padding: var(--space-4) var(--space-6);
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--color-border-subtle);
  }

  .modal-title {
    font-family: var(--font-family-main);
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-main);
    line-height: var(--line-height-24);
  }

  .modal-close-btn {
    background: transparent;
    border: none;
    color: var(--color-text-muted);
    font-size: 24px;
    line-height: 1;
    cursor: pointer;
    padding: var(--space-1);
    border-radius: var(--radius-xs);
    transition: color var(--duration-fast) var(--ease-standard);
  }
  .modal-close-btn:hover {
    color: var(--color-text-main);
  }

  .modal-body {
    padding: var(--space-6);
    font-family: var(--font-family-main);
    font-size: var(--font-size-base);
    color: var(--color-text-main);
    line-height: var(--line-height-24);
    max-height: calc(85vh - 140px);
    overflow-y: auto;
  }

  .modal-footer {
    padding: var(--space-4) var(--space-6);
    background-color: rgba(0, 0, 0, 0.25);
    border-top: 1px solid var(--color-border-subtle);
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: var(--space-3);
  }

  @keyframes modal-fade {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes modal-pop {
    from { transform: scale(0.95) translateY(8px); opacity: 0; }
    to { transform: scale(1) translateY(0); opacity: 1; }
  }
</style>
