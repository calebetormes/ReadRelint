<script>
  /**
   * @typedef {'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'glow'} ButtonVariant
   * @typedef {'sm' | 'md' | 'lg'} ButtonSize
   */

  /** @type {{ variant?: ButtonVariant, size?: ButtonSize, disabled?: boolean, loading?: boolean, type?: 'button' | 'submit' | 'reset', onclick?: (e: MouseEvent) => void, icon?: import('svelte').Snippet, children?: import('svelte').Snippet }} */
  let {
    variant = 'primary',
    size = 'md',
    disabled = false,
    loading = false,
    type = 'button',
    onclick,
    icon,
    children
  } = $props();
</script>

<button
  {type}
  class="btn btn-{variant} btn-{size}"
  class:is-loading={loading}
  disabled={disabled || loading}
  {onclick}
>
  {#if loading}
    <span class="btn-spinner" aria-hidden="true"></span>
  {:else if icon}
    <span class="btn-icon" aria-hidden="true">
      {@render icon()}
    </span>
  {/if}

  {#if children}
    <span class="btn-text">
      {@render children()}
    </span>
  {/if}
</button>

<style>
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    vertical-align: middle;
    gap: var(--space-2);
    font-family: var(--font-family-main);
    font-weight: var(--font-weight-semibold);
    letter-spacing: var(--letter-spacing-wide);
    text-transform: uppercase;
    border-radius: var(--radius-default);
    border: 1px solid transparent;
    cursor: pointer;
    white-space: nowrap;
    user-select: none;
    transition: 
      background-color var(--duration-fast) var(--ease-standard),
      border-color var(--duration-fast) var(--ease-standard),
      box-shadow var(--duration-fast) var(--ease-standard),
      transform var(--duration-instant) var(--ease-spring-snappy);
    outline: none;
    box-sizing: border-box;
  }

  /* Apple Direct Manipulation Press Interaction */
  .btn:active:not(:disabled) {
    transform: var(--active-press-scale);
  }

  /* Icon & Text Perfect Pixel Alignment */
  .btn-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    line-height: 1;
  }

  .btn-icon :global(svg) {
    display: block;
  }

  .btn-text {
    display: inline-flex;
    align-items: center;
    line-height: 1;
    position: relative;
    top: 0.5px; /* Optical center alignment with uppercase typography */
  }

  /* Strict 4px Heights & Paddings */
  .btn-sm {
    height: 32px;
    padding: 0 var(--space-3);
    font-size: var(--font-size-xs);
  }

  .btn-md {
    height: 40px;
    padding: 0 var(--space-4);
    font-size: var(--font-size-ui);
  }

  .btn-lg {
    height: 48px;
    padding: 0 var(--space-6);
    font-size: var(--font-size-base);
  }

  /* Variants */
  .btn-primary {
    background-color: var(--color-amber-primary);
    color: var(--color-text-inverse);
    box-shadow: var(--shadow-sm);
  }
  .btn-primary:hover:not(:disabled) {
    background-color: var(--color-amber-glow);
    box-shadow: var(--glow-amber-subtle);
  }

  .btn-glow {
    background-color: var(--color-amber-primary);
    color: var(--color-text-inverse);
    box-shadow: var(--glow-amber-medium);
  }
  .btn-glow:hover:not(:disabled) {
    background-color: var(--color-amber-glow);
    box-shadow: var(--glow-amber-intense);
  }

  .btn-secondary {
    background-color: var(--color-bg-surface-card);
    color: var(--color-text-main);
    border-color: var(--color-border-subtle);
    box-shadow: var(--shadow-xs);
  }
  .btn-secondary:hover:not(:disabled) {
    background-color: var(--color-bg-surface-elevated);
    border-color: var(--color-border-medium);
  }

  .btn-outline {
    background-color: transparent;
    color: var(--color-text-main);
    border-color: var(--color-border-subtle);
  }
  .btn-outline:hover:not(:disabled) {
    background-color: var(--color-surface-hover);
    border-color: var(--color-amber-primary);
    color: var(--color-amber-primary);
  }

  .btn-ghost {
    background-color: transparent;
    color: var(--color-text-muted);
  }
  .btn-ghost:hover:not(:disabled) {
    background-color: var(--color-surface-hover);
    color: var(--color-text-main);
  }

  .btn-danger {
    background-color: var(--color-functional-error);
    color: var(--color-text-main);
  }
  .btn-danger:hover:not(:disabled) {
    box-shadow: var(--glow-error-subtle);
    filter: brightness(1.1);
  }

  /* Disabled State */
  .btn:disabled {
    opacity: 0.45;
    cursor: not-allowed;
    box-shadow: none !important;
  }

  /* Spinner */
  .btn-spinner {
    width: 14px;
    height: 14px;
    border: 2px solid currentColor;
    border-top-color: transparent;
    border-radius: var(--radius-full);
    animation: btn-spin 0.6s linear infinite;
    flex-shrink: 0;
  }

  @keyframes btn-spin {
    to { transform: rotate(360deg); }
  }
</style>
