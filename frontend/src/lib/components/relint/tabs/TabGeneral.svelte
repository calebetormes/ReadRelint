<script>
  import Input from '$lib/components/ui/Input.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';

  /** @type {{ relint: any, disabled?: boolean, onUpdate?: (relint: any) => void }} */
  let { relint, disabled = false, onUpdate } = $props();
</script>

<div class="tab-general">
  <div class="form-grid">
    <div class="form-group full-width">
      <Input 
        label="ASSUNTO DO RELINT" 
        bind:value={relint.subject}
        {disabled}
      />
    </div>

    <div class="form-group">
      <Input 
        label="DATA DO FATO" 
        type="date"
        bind:value={relint.date_of_fact}
        {disabled}
      />
    </div>

    <div class="form-group">
      <Input 
        label="NÚMERO DE REGISTRO POLICIAL" 
        bind:value={relint.registry_number}
        placeholder="ex: 10293/2026"
        {disabled}
      />
    </div>

    <div class="form-group">
      <Input 
        label="ÓRGÃO REGISTRADOR" 
        bind:value={relint.police_unit}
        placeholder="ex: 1ª DP de Homicídios"
        {disabled}
      />
    </div>

    <div class="form-group">
      <Input 
        label="ANO DO REGISTRO" 
        type="number"
        bind:value={relint.registry_year}
        {disabled}
      />
    </div>

    <div class="form-group full-width">
      <label class="field-label" for="relint-summary">RESUMO COGNITIVO EXTRAÍDO (SÍNTESE DA IA)</label>
      <textarea 
        id="relint-summary"
        class="custom-textarea" 
        rows="5" 
        bind:value={relint.summary}
        {disabled}
      ></textarea>
    </div>
  </div>
</div>

<style>
  .tab-general {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-4) 0;
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }

  .full-width {
    grid-column: span 2;
  }

  .field-label {
    font-family: var(--font-family-main);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-muted);
    letter-spacing: var(--letter-spacing-wide);
    display: block;
    margin-bottom: var(--space-2);
  }

  .custom-textarea {
    width: 100%;
    background-color: var(--color-bg-primary);
    border: 1px solid var(--color-border-medium);
    border-radius: var(--radius-sm);
    color: var(--color-text-main);
    font-family: var(--font-family-main);
    font-size: var(--font-size-ui);
    line-height: var(--line-height-150);
    padding: var(--space-3);
    resize: vertical;
    box-sizing: border-box;
    transition: border-color var(--duration-fast) var(--ease-standard);
  }

  .custom-textarea:focus {
    outline: none;
    border-color: var(--color-amber-primary);
    box-shadow: 0 0 0 2px var(--color-amber-alpha-20);
  }
</style>
