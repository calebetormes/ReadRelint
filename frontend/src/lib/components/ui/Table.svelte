<script>
  /**
   * @typedef {{ key: string, label: string, width?: string, align?: 'left' | 'center' | 'right' }} TableColumn
   */

  /** @type {{ columns: TableColumn[], data: any[], emptyMessage?: string, rowSnippet?: import('svelte').Snippet<[any, number]> }} */
  let {
    columns = [],
    data = [],
    emptyMessage = 'Nenhum registro encontrado.',
    rowSnippet
  } = $props();
</script>

<div class="table-container">
  <table class="table">
    <thead>
      <tr class="table-header-row">
        {#each columns as col}
          <th
            style:width={col.width}
            class="th th-align-{col.align || 'left'}"
          >
            {col.label}
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#if data.length === 0}
        <tr>
          <td colspan={columns.length} class="td-empty">
            {emptyMessage}
          </td>
        </tr>
      {:else}
        {#each data as row, idx}
          {#if rowSnippet}
            {@render rowSnippet(row, idx)}
          {:else}
            <tr class="table-row">
              {#each columns as col}
                <td class="td td-align-{col.align || 'left'}">
                  {row[col.key] ?? ''}
                </td>
              {/each}
            </tr>
          {/if}
        {/each}
      {/if}
    </tbody>
  </table>
</div>

<style>
  .table-container {
    width: 100%;
    overflow-x: auto;
    background-color: var(--color-bg-surface-card);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
  }

  .table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-family: var(--font-family-main);
  }

  .table-header-row {
    background-color: var(--color-bg-secondary);
    border-bottom: 1px solid var(--color-border-subtle);
  }

  .th {
    padding: var(--space-3) var(--space-4);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-muted);
    letter-spacing: var(--letter-spacing-wider);
    text-transform: uppercase;
    line-height: var(--line-height-16);
    white-space: nowrap;
  }

  .table-row {
    border-bottom: 1px solid var(--color-border-subtle);
    transition: background-color var(--duration-fast) var(--ease-standard);
  }
  .table-row:last-child {
    border-bottom: none;
  }

  .table-row:hover {
    background-color: var(--color-surface-hover);
  }

  .td {
    padding: var(--space-3) var(--space-4);
    font-size: var(--font-size-ui);
    color: var(--color-text-main);
    line-height: var(--line-height-20);
    vertical-align: middle;
  }

  .td-empty {
    padding: var(--space-8);
    text-align: center;
    color: var(--color-text-muted);
    font-size: var(--font-size-base);
  }

  .th-align-left, .td-align-left { text-align: left; }
  .th-align-center, .td-align-center { text-align: center; }
  .th-align-right, .td-align-right { text-align: right; }
</style>
