<script>
  /**
   * @typedef {'base' | 'elevated' | 'glass' | 'interactive'} CardVariant
   */

  /** @type {{ variant?: CardVariant, title?: string, subtitle?: string, onclick?: (e: MouseEvent) => void, header?: import('svelte').Snippet, actions?: import('svelte').Snippet, footer?: import('svelte').Snippet, children?: import('svelte').Snippet }} */
  let {
    variant = 'base',
    title = '',
    subtitle = '',
    onclick,
    header,
    actions,
    footer,
    children
  } = $props();
</script>

{#if onclick || variant === 'interactive'}
  <button
    type="button"
    class="card card-{variant} is-interactive"
    {onclick}
  >
    {#if header || title || subtitle || actions}
      <div class="card-header">
        {#if header}
          {@render header()}
        {:else}
          <div class="card-title-group">
            {#if title}
              <h3 class="card-title">{title}</h3>
            {/if}
            {#if subtitle}
              <p class="card-subtitle">{subtitle}</p>
            {/if}
          </div>
        {/if}

        {#if actions}
          <div class="card-actions">
            {@render actions()}
          </div>
        {/if}
      </div>
    {/if}

    {#if children}
      <div class="card-body">
        {@render children()}
      </div>
    {/if}

    {#if footer}
      <div class="card-footer">
        {@render footer()}
      </div>
    {/if}
  </button>
{:else}
  <div class="card card-{variant}">
    {#if header || title || subtitle || actions}
      <div class="card-header">
        {#if header}
          {@render header()}
        {:else}
          <div class="card-title-group">
            {#if title}
              <h3 class="card-title">{title}</h3>
            {/if}
            {#if subtitle}
              <p class="card-subtitle">{subtitle}</p>
            {/if}
          </div>
        {/if}

        {#if actions}
          <div class="card-actions">
            {@render actions()}
          </div>
        {/if}
      </div>
    {/if}

    {#if children}
      <div class="card-body">
        {@render children()}
      </div>
    {/if}

    {#if footer}
      <div class="card-footer">
        {@render footer()}
      </div>
    {/if}
  </div>
{/if}

<style>
  .card {
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border-subtle);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    text-align: left;
    transition: 
      background-color var(--duration-fast) var(--ease-standard),
      border-color var(--duration-fast) var(--ease-standard),
      box-shadow var(--duration-normal) var(--ease-spring-smooth),
      transform var(--duration-fast) var(--ease-spring-snappy);
    font-family: inherit;
    color: inherit;
  }

  button.card {
    width: 100%;
    cursor: pointer;
    background: transparent;
    padding: 0;
  }

  /* Variants */
  .card-base {
    background-color: var(--color-bg-surface-card);
    box-shadow: var(--shadow-sm);
  }

  .card-elevated {
    background-color: var(--color-bg-surface-elevated);
    border-color: var(--color-border-medium);
    box-shadow: var(--shadow-md);
  }

  .card-glass {
    background-color: var(--color-bg-surface-glass);
    backdrop-filter: var(--backdrop-blur-md);
    border-color: var(--color-border-medium);
    box-shadow: var(--shadow-md);
  }

  .card-interactive, .is-interactive {
    background-color: var(--color-bg-surface-card);
    cursor: pointer;
    box-shadow: var(--shadow-sm);
  }
  .card-interactive:hover, .is-interactive:hover {
    background-color: var(--color-bg-surface-elevated);
    border-color: rgba(224, 159, 62, 0.4);
    box-shadow: var(--shadow-lg), var(--glow-amber-subtle);
    transform: translateY(-2px);
  }
  .card-interactive:active, .is-interactive:active {
    transform: scale(0.99);
  }

  /* Internal Structure with 4px Grid Spacings */
  .card-header {
    padding: var(--space-4) var(--space-5);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
    border-bottom: 1px solid var(--color-border-subtle);
  }

  .card-title-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .card-title {
    font-family: var(--font-family-main);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-main);
    line-height: var(--line-height-24);
  }

  .card-subtitle {
    font-family: var(--font-family-main);
    font-size: var(--font-size-sm);
    color: var(--color-text-muted);
    line-height: var(--line-height-16);
  }

  .card-body {
    padding: var(--space-5);
    color: var(--color-text-main);
    font-size: var(--font-size-base);
    line-height: var(--line-height-20);
    flex: 1;
  }

  .card-footer {
    padding: var(--space-3) var(--space-5);
    background-color: rgba(0, 0, 0, 0.2);
    border-top: 1px solid var(--color-border-subtle);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
  }
</style>
