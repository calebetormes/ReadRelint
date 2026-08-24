<script>
  import Input from '$lib/components/ui/Input.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import { Crosshair, Info } from 'phosphor-svelte';

  /** @type {{ relint: any, onUpdate?: (relint: any) => void }} */
  let { relint, onUpdate } = $props();

  let isHomicide = $derived(relint.bm_group === 'Homicídio');
</script>

<div class="tab-specialty">
  {#if isHomicide}
    <div class="specialty-header">
      <Crosshair size={20} weight="fill" color="var(--color-functional-error)" />
      <span class="specialty-title">Campos Especializados de Homicídio & Crimes Contra a Vida</span>
      <Badge variant="error" size="sm">Homicídio</Badge>
    </div>

    <div class="form-grid">
      <div class="form-group">
        <Input 
          label="TIPO DE FATO" 
          bind:value={relint.homicide_details.fact_type}
        />
      </div>

      <div class="form-group">
        <Input 
          label="MOTIVAÇÃO PRESUMIDA" 
          bind:value={relint.homicide_details.motivation}
        />
      </div>

      <div class="form-group">
        <Input 
          label="MEIO EMPREGADO" 
          bind:value={relint.homicide_details.means_used}
        />
      </div>

      <div class="form-group">
        <Input 
          label="DELEGACIA RESPONSÁVEL" 
          bind:value={relint.homicide_details.police_dept}
        />
      </div>
    </div>
  {:else}
    <div class="empty-specialty">
      <Info size={24} weight="fill" color="var(--color-text-muted)" />
      <p class="empty-text">Este RELINT possui especialidade padrão (<strong>{relint.bm_group || 'Geral'}</strong>) sem formulários adicionais estendidos.</p>
    </div>
  {/if}
</div>

<style>
  .tab-specialty {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-4) 0;
  }

  .specialty-header {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    background-color: var(--color-bg-primary);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border-subtle);
  }

  .specialty-title {
    font-size: var(--font-size-ui);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-main);
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }

  .empty-specialty {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-6);
    background-color: var(--color-bg-primary);
    border: 1px dashed var(--color-border-medium);
    border-radius: var(--radius-default);
  }

  .empty-text {
    font-size: var(--font-size-ui);
    color: var(--color-text-muted);
    margin: 0;
  }
</style>
