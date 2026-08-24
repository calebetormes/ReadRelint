<script>
  import Input from '$lib/components/ui/Input.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import { MapPin } from 'phosphor-svelte';

  /** @type {{ relint: any, disabled?: boolean, onUpdate?: (relint: any) => void }} */
  let { relint, disabled = false, onUpdate } = $props();
</script>

<div class="tab-location">
  <div class="location-header">
    <div class="geo-badge-box">
      <MapPin size={20} weight="fill" color="var(--color-amber-primary)" />
      <span class="geo-label">Nível de Precisão Geográfica:</span>
      <Badge variant="amber" size="sm">Endereço Estruturado (Fallback)</Badge>
    </div>
  </div>

  <div class="form-grid">
    <div class="form-group full-width">
      <Input 
        label="ENDEREÇO DO FATO / LOGRADOURO" 
        bind:value={relint.address} 
        placeholder="ex: Av. Borges de Medeiros, 1500"
        {disabled}
      />
    </div>

    <div class="form-group">
      <Input 
        label="BAIRRO" 
        bind:value={relint.neighborhood} 
        placeholder="ex: Praia de Belas"
        {disabled}
      />
    </div>

    <div class="form-group">
      <Input 
        label="MUNICÍPIO / CIDADE" 
        bind:value={relint.municipality} 
        placeholder="ex: Porto Alegre"
        {disabled}
      />
    </div>
  </div>
</div>

<style>
  .tab-location {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-4) 0;
  }

  .location-header {
    background-color: var(--color-bg-primary);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border-subtle);
  }

  .geo-badge-box {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .geo-label {
    font-size: var(--font-size-ui);
    color: var(--color-text-muted);
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }

  .full-width {
    grid-column: span 2;
  }
</style>
