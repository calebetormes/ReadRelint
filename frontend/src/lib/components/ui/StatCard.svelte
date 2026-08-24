<script>
  /** @type {{ label: string, value: string | number, trend?: string, trendType?: 'positive' | 'negative' | 'neutral', description?: string, icon?: import('svelte').Snippet }} */
  let {
    label,
    value,
    trend = '',
    trendType = 'positive',
    description = '',
    icon
  } = $props();
</script>

<div class="stat-card">
  <div class="stat-header">
    <span class="stat-label">{label}</span>
    {#if icon}
      <span class="stat-icon">
        {@render icon()}
      </span>
    {/if}
  </div>

  <div class="stat-value-group">
    <span class="stat-value">{value}</span>
    {#if trend}
      <span class="stat-trend trend-{trendType}">
        {trend}
      </span>
    {/if}
  </div>

  {#if description}
    <p class="stat-description">{description}</p>
  {/if}
</div>

<style>
  .stat-card {
    background-color: var(--color-bg-surface-card);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-md);
    padding: var(--space-4) var(--space-5);
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    box-shadow: var(--shadow-sm);
    transition: 
      background-color var(--duration-fast) var(--ease-standard),
      border-color var(--duration-fast) var(--ease-standard),
      box-shadow var(--duration-fast) var(--ease-standard);
  }

  .stat-card:hover {
    background-color: var(--color-bg-surface-elevated);
    border-color: var(--color-border-medium);
    box-shadow: var(--shadow-md);
  }

  .stat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
  }

  .stat-label {
    font-family: var(--font-family-main);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-muted);
    letter-spacing: var(--letter-spacing-wider);
    text-transform: uppercase;
    line-height: var(--line-height-16);
  }

  .stat-icon {
    color: var(--color-amber-primary);
    display: flex;
    align-items: center;
  }

  .stat-value-group {
    display: flex;
    align-items: baseline;
    gap: var(--space-3);
  }

  .stat-value {
    font-family: var(--font-family-main);
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-amber-primary);
    line-height: var(--line-height-40);
    letter-spacing: var(--letter-spacing-tight);
  }

  .stat-trend {
    font-family: var(--font-family-mono);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    padding: 0 var(--space-1);
    border-radius: var(--radius-xs);
    line-height: var(--line-height-16);
  }

  .trend-positive {
    background-color: rgba(16, 185, 129, 0.15);
    color: var(--color-functional-success);
  }

  .trend-negative {
    background-color: rgba(239, 68, 68, 0.15);
    color: var(--color-functional-error);
  }

  .trend-neutral {
    background-color: rgba(255, 255, 255, 0.08);
    color: var(--color-text-muted);
  }

  .stat-description {
    font-family: var(--font-family-main);
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
    line-height: var(--line-height-16);
  }
</style>
