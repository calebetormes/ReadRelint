<script>
  /** @type {{ checked?: boolean, label?: string, disabled?: boolean, id?: string, onchange?: (checked: boolean) => void }} */
  let {
    checked = $bindable(false),
    label = '',
    disabled = false,
    id = `sw-${Math.random().toString(36).substring(2, 9)}`,
    onchange
  } = $props();

  function toggle() {
    if (disabled) return;
    checked = !checked;
    if (onchange) onchange(checked);
  }
</script>

<label for={id} class="switch-wrapper" class:is-disabled={disabled}>
  <button
    {id}
    type="button"
    role="switch"
    aria-checked={checked}
    aria-label={label || 'Alternar interruptor'}
    {disabled}
    onclick={toggle}
    class="switch-track"
    class:is-checked={checked}
  >
    <span class="switch-thumb"></span>
  </button>

  {#if label}
    <span class="switch-label">{label}</span>
  {/if}
</label>

<style>
  .switch-wrapper {
    display: inline-flex;
    align-items: center;
    gap: var(--space-3);
    cursor: pointer;
    user-select: none;
  }

  .switch-track {
    position: relative;
    width: 44px;
    height: 24px;
    background-color: var(--color-border-subtle);
    border-radius: var(--radius-full);
    border: none;
    padding: 2px;
    cursor: pointer;
    transition: 
      background-color var(--duration-fast) var(--ease-standard),
      box-shadow var(--duration-fast) var(--ease-standard);
    outline: none;
  }

  .switch-track:focus-visible {
    box-shadow: 0 0 0 3px rgba(224, 159, 62, 0.3);
  }

  .switch-track.is-checked {
    background-color: var(--color-amber-primary);
    box-shadow: var(--glow-amber-subtle);
  }

  .switch-thumb {
    display: block;
    width: 20px;
    height: 20px;
    background-color: #FFFFFF;
    border-radius: var(--radius-full);
    box-shadow: var(--shadow-sm);
    transition: transform var(--duration-normal) var(--ease-spring-smooth);
    transform: translateX(0);
  }

  .switch-track.is-checked .switch-thumb {
    transform: translateX(20px);
  }

  .switch-label {
    font-family: var(--font-family-main);
    font-size: var(--font-size-base);
    color: var(--color-text-main);
    line-height: var(--line-height-20);
  }

  .is-disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .is-disabled .switch-track {
    cursor: not-allowed;
  }
</style>
