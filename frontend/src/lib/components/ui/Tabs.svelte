<script>
  /**
   * @typedef {{ id: string, label: string, badge?: string | number, icon?: import('svelte').Snippet }} TabItem
   */

  /** @type {{ tabs: TabItem[], activeTab?: string, onchange?: (id: string) => void }} */
  let {
    tabs = [],
    activeTab = $bindable(tabs[0]?.id || ''),
    onchange
  } = $props();

  /** @param {string} id */
  function selectTab(id) {
    activeTab = id;
    if (onchange) onchange(id);
  }
</script>

<div class="tabs-container" role="tablist">
  {#each tabs as tab}
    <button
      type="button"
      role="tab"
      aria-selected={activeTab === tab.id}
      class="tab-button"
      class:is-active={activeTab === tab.id}
      onclick={() => selectTab(tab.id)}
    >
      {#if tab.icon}
        <span class="tab-icon" aria-hidden="true">
          {@render tab.icon()}
        </span>
      {/if}
      <span class="tab-label">{tab.label}</span>
      {#if tab.badge}
        <span class="tab-badge">{tab.badge}</span>
      {/if}
    </button>
  {/each}
</div>

<style>
  .tabs-container {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    background-color: var(--color-bg-secondary);
    padding: var(--space-1);
    border-radius: var(--radius-default);
    border: 1px solid var(--color-border-subtle);
    user-select: none;
    box-sizing: border-box;
  }

  .tab-button {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    vertical-align: middle;
    gap: var(--space-2);
    height: 32px;
    padding: 0 var(--space-3);
    background: transparent;
    border: none;
    border-radius: var(--radius-xs);
    font-family: var(--font-family-main);
    font-size: var(--font-size-ui);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-muted);
    cursor: pointer;
    line-height: 1;
    transition: 
      color var(--duration-fast) var(--ease-standard),
      background-color var(--duration-fast) var(--ease-standard),
      transform var(--duration-instant) var(--ease-spring-snappy);
    outline: none;
    box-sizing: border-box;
  }

  .tab-button:hover:not(.is-active) {
    color: var(--color-text-main);
    background-color: var(--color-surface-hover);
  }

  .tab-button:active {
    transform: scale(0.98);
  }

  .tab-button.is-active {
    background-color: var(--color-bg-surface-card);
    color: var(--color-amber-primary);
    font-weight: var(--font-weight-semibold);
    box-shadow: var(--shadow-sm);
  }

  .tab-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    line-height: 1;
  }
  .tab-icon :global(svg) {
    display: block;
  }

  .tab-label {
    display: inline-flex;
    align-items: center;
    line-height: 1;
    position: relative;
    top: 0.5px;
  }

  .tab-badge {
    font-family: var(--font-family-mono);
    font-size: var(--font-size-xs);
    background-color: rgba(224, 159, 62, 0.15);
    color: var(--color-amber-primary);
    padding: 2px var(--space-1);
    border-radius: var(--radius-xs);
    line-height: 1;
    display: inline-flex;
    align-items: center;
  }
</style>
