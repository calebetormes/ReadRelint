<script>
  /**
   * @typedef {'info' | 'success' | 'warning' | 'error'} AlertType
   */

  /** @type {{ type?: AlertType, title?: string, dismissible?: boolean, ondismiss?: () => void, icon?: import('svelte').Snippet, children?: import('svelte').Snippet }} */
  let {
    type = 'info',
    title = '',
    dismissible = false,
    ondismiss,
    icon,
    children
  } = $props();

  let visible = $state(true);

  function handleDismiss() {
    visible = false;
    if (ondismiss) ondismiss();
  }
</script>

{#if visible}
  <div class="alert alert-{type}" role="alert">
    {#if icon}
      <div class="alert-icon" aria-hidden="true">
        {@render icon()}
      </div>
    {/if}

    <div class="alert-content">
      {#if title}
        <h4 class="alert-title">{title}</h4>
      {/if}
      {#if children}
        <div class="alert-body">
          {@render children()}
        </div>
      {/if}
    </div>

    {#if dismissible}
      <button
        type="button"
        class="alert-close"
        onclick={handleDismiss}
        aria-label="Fechar notificação"
      >
        &times;
      </button>
    {/if}
  </div>
{/if}

<style>
  .alert {
    position: relative;
    padding: var(--space-4) var(--space-5);
    border-radius: var(--radius-sm);
    background-color: var(--color-bg-surface-card);
    border: 1px solid var(--color-border-subtle);
    display: flex;
    align-items: flex-start;
    gap: var(--space-3);
    box-shadow: var(--shadow-sm);
    transition: opacity var(--duration-fast) var(--ease-standard);
    box-sizing: border-box;
  }

  .alert-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    line-height: 1;
    margin-top: 1px;
  }
  .alert-icon :global(svg) {
    display: block;
  }

  .alert-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .alert-title {
    font-family: var(--font-family-main);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    line-height: var(--line-height-20);
    display: flex;
    align-items: center;
  }

  .alert-body {
    font-family: var(--font-family-main);
    font-size: var(--font-size-ui);
    color: var(--color-text-muted);
    line-height: var(--line-height-20);
  }

  .alert-close {
    background: transparent;
    border: none;
    color: var(--color-text-muted);
    font-size: 18px;
    cursor: pointer;
    line-height: 1;
    padding: var(--space-1);
    border-radius: var(--radius-xs);
    transition: color var(--duration-fast) var(--ease-standard);
  }
  .alert-close:hover {
    color: var(--color-text-main);
  }

  /* Variants */
  .alert-info {
    border-color: rgba(59, 130, 246, 0.4);
    background-color: rgba(30, 58, 138, 0.15);
  }
  .alert-info .alert-title, .alert-info .alert-icon {
    color: var(--color-functional-info);
  }

  .alert-success {
    border-color: rgba(16, 185, 129, 0.4);
    background-color: rgba(6, 78, 59, 0.15);
  }
  .alert-success .alert-title, .alert-success .alert-icon {
    color: var(--color-functional-success);
  }

  .alert-warning {
    border-color: rgba(245, 158, 11, 0.4);
    background-color: rgba(69, 26, 3, 0.15);
  }
  .alert-warning .alert-title, .alert-warning .alert-icon {
    color: var(--color-functional-warning);
  }

  .alert-error {
    border-color: rgba(239, 68, 68, 0.4);
    background-color: rgba(127, 29, 29, 0.15);
  }
  .alert-error .alert-title, .alert-error .alert-icon {
    color: var(--color-functional-error);
  }
</style>
