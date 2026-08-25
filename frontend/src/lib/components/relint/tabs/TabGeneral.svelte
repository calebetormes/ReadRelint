<script>
  import Input from '$lib/components/ui/Input.svelte';
  import { Sparkle, FileText, CalendarBlank, Hash, Buildings } from 'phosphor-svelte';

  /** @type {{ relint: any, disabled?: boolean, onUpdate?: (relint: any) => void }} */
  let { relint, disabled = false, onUpdate } = $props();

  // Se disabled = true, estamos em MODO LEITURA. Se disabled = false, estamos em MODO EDIÇÃO.
  let isEditing = $derived(!disabled);
</script>

<div class="tab-general">
  <!-- 1. BLOCO PRINCIPAL: SÍNTESE (Com destaque e tipografia ampliada) -->
  <div class="synthesis-section">
    <div class="section-header">
      <Sparkle size={16} weight="fill" class="synthesis-icon" />
      <h3 class="section-title">SÍNTESE DO FATO</h3>
    </div>

    {#if isEditing}
      <textarea 
        id="relint-summary"
        class="custom-textarea" 
        rows="6" 
        placeholder="Descreva a síntese do fato..."
        bind:value={relint.summary}
      ></textarea>
    {:else}
      <div class="synthesis-card">
        {#if relint.summary}
          <p class="synthesis-text">{relint.summary}</p>
        {:else}
          <p class="synthesis-empty">Nenhuma síntese registrada para este boletim.</p>
        {/if}
      </div>
    {/if}
  </div>

  <!-- 2. BLOCO DE METADADOS DO FATO (Abaixo da Síntese) -->
  <div class="metadata-section">
    <div class="section-header">
      <FileText size={15} weight="bold" class="meta-section-icon" />
      <h4 class="section-subtitle">DADOS DO REGISTRO</h4>
    </div>

    {#if isEditing}
      <!-- Modo Edição: Inputs estruturados -->
      <div class="form-grid">
        <div class="form-group full-width">
          <Input 
            label="ASSUNTO" 
            bind:value={relint.subject}
          />
        </div>

        <div class="form-group">
          <Input 
            label="DATA DO FATO" 
            type="date"
            bind:value={relint.date_of_fact}
          />
        </div>

        <div class="form-group">
          <Input 
            label="NÚMERO DE REGISTRO" 
            bind:value={relint.registry_number}
            placeholder="ex: 10293/2026"
          />
        </div>

        <div class="form-group">
          <Input 
            label="ÓRGÃO REGISTRADOR" 
            bind:value={relint.police_unit}
            placeholder="ex: 1ª DP de Homicídios"
          />
        </div>

        <div class="form-group">
          <Input 
            label="ANO DO REGISTRO" 
            type="number"
            bind:value={relint.registry_year}
          />
        </div>
      </div>
    {:else}
      <!-- Modo Leitura: Exibição como texto puro em cards/linhas minimalistas -->
      <div class="reading-grid">
        <div class="reading-field full-width">
          <span class="field-label">ASSUNTO</span>
          <span class="field-value highlight">{relint.subject || 'Não especificado'}</span>
        </div>

        <div class="reading-field">
          <span class="field-label">DATA DO FATO</span>
          <span class="field-value font-mono">{relint.date_of_fact || 'Não informada'}</span>
        </div>

        <div class="reading-field">
          <span class="field-label">NÚMERO DE REGISTRO</span>
          <span class="field-value font-mono">{relint.registry_number || 'N/I'}</span>
        </div>

        <div class="reading-field">
          <span class="field-label">ÓRGÃO REGISTRADOR</span>
          <span class="field-value">{relint.police_unit || 'Não informado'}</span>
        </div>

        <div class="reading-field">
          <span class="field-label">ANO DO REGISTRO</span>
          <span class="field-value font-mono">{relint.registry_year || 'N/I'}</span>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .tab-general {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
    padding: var(--space-4) 0;
  }

  /* Seção da Síntese */
  .synthesis-section {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 2px;
  }

  :global(.synthesis-icon) {
    color: var(--color-amber-primary);
  }

  :global(.meta-section-icon) {
    color: var(--color-text-muted);
  }

  .section-title {
    font-size: 13px;
    font-weight: var(--font-weight-bold);
    color: var(--color-amber-primary);
    letter-spacing: 0.5px;
    margin: 0;
    text-transform: uppercase;
  }

  .section-subtitle {
    font-size: 11px;
    font-weight: var(--font-weight-bold);
    color: var(--color-text-muted);
    letter-spacing: 0.5px;
    margin: 0;
    text-transform: uppercase;
  }

  .synthesis-card {
    background-color: #121212;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 3px solid var(--color-amber-primary);
    border-radius: var(--radius-default);
    padding: var(--space-4) var(--space-5);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  }

  .synthesis-text {
    font-size: 15px;
    line-height: 1.65;
    color: #e4e4e7;
    margin: 0;
    white-space: pre-wrap;
    letter-spacing: 0.15px;
  }

  .synthesis-empty {
    font-size: 14px;
    color: var(--color-text-disabled);
    font-style: italic;
    margin: 0;
  }

  .custom-textarea {
    width: 100%;
    background-color: var(--color-bg-primary);
    border: 1px solid var(--color-border-medium);
    border-radius: var(--radius-sm);
    color: var(--color-text-main);
    font-family: var(--font-family-main);
    font-size: 14px;
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

  /* Seção de Metadados */
  .metadata-section {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding-top: var(--space-4);
    border-top: 1px solid rgba(255, 255, 255, 0.06);
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }

  .reading-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }

  .full-width {
    grid-column: span 2;
  }

  .reading-field {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 8px 12px;
    background-color: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: var(--radius-sm);
  }

  .field-label {
    font-size: 10px;
    font-weight: var(--font-weight-bold);
    color: var(--color-text-disabled);
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }

  .field-value {
    font-size: 13px;
    font-weight: var(--font-weight-medium);
    color: var(--color-text-main);
  }

  .field-value.highlight {
    color: #ffffff;
    font-weight: var(--font-weight-semibold);
  }

  .font-mono {
    font-family: var(--font-family-mono);
  }

  @media (max-width: 768px) {
    .form-grid, .reading-grid {
      grid-template-columns: 1fr;
    }
    .full-width {
      grid-column: span 1;
    }
  }
</style>

