<script>
  /**
   * @typedef {'amber' | 'success' | 'warning' | 'error' | 'info' | 'neutral'} BadgeVariant
   * @typedef {'sm' | 'md'} BadgeSize
   */

  /** @type {{ variant?: BadgeVariant, size?: BadgeSize, dot?: boolean, icon?: import('svelte').Snippet, children?: import('svelte').Snippet }} */
  let {
    variant = 'amber',
    size = 'md',
    dot = false,
    icon,
    children
  } = $props();
</script>

<span class="badge badge-{variant} badge-{size}">
  {#if dot}
    <span class="badge-dot" aria-hidden="true"></span>
  {:else if icon}
    <span class="badge-icon" aria-hidden="true">
      {@render icon()}
    </span>
  {/if}
  {#if children}
    <span class="badge-label">
      {@render children()}
    </span>
  {/if}
</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    vertical-align: middle;
    gap: var(--space-1);
    font-family: var(--font-family-main);
    font-weight: var(--font-weight-semibold);
    letter-spacing: var(--letter-spacing-wider);
    text-transform: uppercase;
    border-radius: var(--radius-xs);
    border: 1px solid transparent;
    white-space: nowrap;
    user-select: none;
    box-sizing: border-box;
  }

  /* 4px Pixel-Perfect Heights */
  .badge-sm {
    height: 20px;
    padding: 0 var(--space-2);
    font-size: var(--font-size-xs);
  }

  .badge-md {
    height: 24px;
    padding: 0 var(--space-2);
    font-size: var(--font-size-xs);
  }

  .badge-dot {
    width: 6px;
    height: 6px;
    border-radius: var(--radius-full);
    background-color: currentColor;
    flex-shrink: 0;
  }

  .badge-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    line-height: 1;
  }
  .badge-icon :global(svg) {
    display: block;
  }

  .badge-label {
    display: inline-flex;
    align-items: center;
    line-height: 1;
    position: relative;
    top: 0.5px;
  }

  /* Variants */
  .badge-amber {
    background-color: rgba(224, 159, 62, 0.14);
    color: var(--color-amber-primary);
    border-color: rgba(224, 159, 62, 0.35);
  }

  .badge-success {
    background-color: rgba(16, 185, 129, 0.14);
    color: var(--color-functional-success);
    border-color: rgba(16, 185, 129, 0.35);
  }

  .badge-warning {
    background-color: rgba(245, 158, 11, 0.14);
    color: var(--color-functional-warning);
    border-color: rgba(245, 158, 11, 0.35);
  }

  .badge-error {
    background-color: rgba(239, 68, 68, 0.14);
    color: var(--color-functional-error);
    border-color: rgba(239, 68, 68, 0.35);
  }

  .badge-info {
    background-color: rgba(59, 130, 246, 0.14);
    color: var(--color-functional-info);
    border-color: rgba(59, 130, 246, 0.35);
  }

  .badge-neutral {
    background-color: rgba(255, 255, 255, 0.06);
    color: var(--color-text-muted);
    border-color: var(--color-border-subtle);
  }
</style>
