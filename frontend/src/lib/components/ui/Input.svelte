<script>
  /** @type {{ value?: string, label?: string, placeholder?: string, type?: string, disabled?: boolean, error?: string, hint?: string, id?: string, prefixIcon?: import('svelte').Snippet, suffixIcon?: import('svelte').Snippet, oninput?: (e: Event) => void, onchange?: (e: Event) => void, onfocus?: (e: FocusEvent) => void, onblur?: (e: FocusEvent) => void }} */
  let {
    value = $bindable(''),
    label = '',
    placeholder = '',
    type = 'text',
    disabled = false,
    error = '',
    hint = '',
    id = `inp-${Math.random().toString(36).substring(2, 9)}`,
    prefixIcon,
    suffixIcon,
    oninput,
    onchange,
    onfocus,
    onblur
  } = $props();
</script>

<div class="input-wrapper" class:has-error={!!error} class:is-disabled={disabled}>
  {#if label}
    <label for={id} class="input-label">
      {label}
    </label>
  {/if}

  <div class="input-box">
    {#if prefixIcon}
      <span class="input-icon-prefix" aria-hidden="true">
        {@render prefixIcon()}
      </span>
    {/if}

    <input
      {id}
      {type}
      {placeholder}
      {disabled}
      bind:value
      {oninput}
      {onchange}
      {onfocus}
      {onblur}
      class="input-element"
    />

    {#if suffixIcon}
      <span class="input-icon-suffix" aria-hidden="true">
        {@render suffixIcon()}
      </span>
    {/if}
  </div>

  {#if error}
    <span class="input-msg msg-error">{error}</span>
  {:else if hint}
    <span class="input-msg msg-hint">{hint}</span>
  {/if}
</div>

<style>
  .input-wrapper {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    width: 100%;
  }

  .input-label {
    font-family: var(--font-family-main);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-muted);
    letter-spacing: var(--letter-spacing-wide);
    text-transform: uppercase;
    line-height: var(--line-height-16);
  }

  .input-box {
    position: relative;
    display: flex;
    align-items: center;
    width: 100%;
    background-color: var(--color-bg-tertiary);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-default);
    height: 40px;
    padding: 0 var(--space-3);
    box-sizing: border-box;
    transition: 
      border-color var(--duration-fast) var(--ease-standard),
      box-shadow var(--duration-fast) var(--ease-standard),
      background-color var(--duration-fast) var(--ease-standard);
  }

  .input-box:focus-within {
    border-color: var(--color-border-focus);
    background-color: var(--color-bg-surface-card);
    box-shadow: 0 0 0 3px rgba(224, 159, 62, 0.2), var(--glow-amber-subtle);
  }

  .has-error .input-box {
    border-color: var(--color-functional-error);
  }
  .has-error .input-box:focus-within {
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2), var(--glow-error-subtle);
  }

  .input-element {
    flex: 1;
    width: 100%;
    height: 100%;
    border: none;
    outline: none;
    background: transparent;
    font-family: var(--font-family-main);
    font-size: var(--font-size-base);
    color: var(--color-text-main);
    line-height: 1;
  }

  .input-element::placeholder {
    color: var(--color-text-disabled);
  }

  .input-icon-prefix, .input-icon-suffix {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--color-text-muted);
    flex-shrink: 0;
    line-height: 1;
  }
  .input-icon-prefix :global(svg), .input-icon-suffix :global(svg) {
    display: block;
  }

  .input-icon-prefix {
    margin-right: var(--space-2);
  }
  .input-icon-suffix {
    margin-left: var(--space-2);
  }

  .input-msg {
    font-family: var(--font-family-main);
    font-size: var(--font-size-xs);
    line-height: var(--line-height-16);
  }

  .msg-error {
    color: var(--color-functional-error);
  }

  .msg-hint {
    color: var(--color-text-muted);
  }

  .is-disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .is-disabled .input-box {
    pointer-events: none;
  }
</style>
