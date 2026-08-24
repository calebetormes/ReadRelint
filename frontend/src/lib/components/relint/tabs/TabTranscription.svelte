<script>
  import { FileText, Copy, Check } from 'phosphor-svelte';

  /** @type {{ relint: any }} */
  let { relint } = $props();

  let copied = $state(false);

  function copyText() {
    if (relint.raw_text) {
      navigator.clipboard.writeText(relint.raw_text);
      copied = true;
      setTimeout(() => copied = false, 2000);
    }
  }
</script>

<div class="tab-transcription">
  <div class="transcription-header">
    <div class="header-info">
      <FileText size={20} weight="fill" color="var(--color-amber-primary)" />
      <span class="info-title">Transcrição Literal do Boletim ({relint.source_file || 'RELINT.pdf'})</span>
    </div>

    <button class="copy-btn" onclick={copyText}>
      {#if copied}
        <Check size={16} weight="bold" color="var(--color-functional-success)" />
        <span>COPIADO!</span>
      {:else}
        <Copy size={16} weight="bold" />
        <span>COPIAR TEXTO</span>
      {/if}
    </button>
  </div>

  <div class="text-viewer-container">
    <pre class="transcription-text">{relint.raw_text || 'Sem texto bruto extraído para este documento.'}</pre>
  </div>
</div>

<style>
  .tab-transcription {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-4) 0;
  }

  .transcription-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: var(--color-bg-primary);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border-subtle);
  }

  .header-info {
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }

  .info-title {
    font-size: var(--font-size-ui);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-main);
  }

  .copy-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    background: transparent;
    border: 1px solid var(--color-border-medium);
    border-radius: var(--radius-sm);
    color: var(--color-text-muted);
    font-family: var(--font-family-main);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
    padding: var(--space-2) var(--space-3);
    cursor: pointer;
    transition: 
      border-color var(--duration-fast) var(--ease-standard),
      color var(--duration-fast) var(--ease-standard);
  }

  .copy-btn:hover {
    border-color: var(--color-amber-primary);
    color: var(--color-text-main);
  }

  .text-viewer-container {
    background-color: var(--color-bg-primary);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-default);
    padding: var(--space-4);
    max-height: 480px;
    overflow-y: auto;
  }

  .transcription-text {
    font-family: var(--font-family-mono);
    font-size: var(--font-size-sm);
    line-height: var(--line-height-160);
    color: var(--color-text-main);
    white-space: pre-wrap;
    word-break: break-word;
    margin: 0;
  }
</style>
