<script>
  import { FileText, Copy, Check, MapPin, Users } from 'phosphor-svelte';
  import Badge from '$lib/components/ui/Badge.svelte';

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

  /** @param {string} str */
  function escapeHtml(str) {
    return str.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  /** @param {string} role */
  function participantHighlightClass(role) {
    if (role === 'Autor/Suspeito') return 'entity-suspect';
    if (role === 'Vítima') return 'entity-victim';
    if (role === 'Testemunha') return 'entity-witness';
    return 'entity-neutral';
  }

  const COORD_PATTERN = /-?\d{1,2}\.\d{3,}\s*,\s*-?\d{1,2}\.\d{3,}/g;

  /**
   * Localiza, no texto bruto, as ocorrências de coordenadas geográficas e de nomes/alcunhas
   * de participantes já cadastrados neste RELINT, resolvendo sobreposições (mantém a primeira
   * ocorrência mais longa).
   * @param {string} text
   * @param {any[]} participants
   */
  function findHighlightSpans(text, participants) {
    /** @type {{start: number, end: number, cls: string}[]} */
    const spans = [];

    let match;
    COORD_PATTERN.lastIndex = 0;
    while ((match = COORD_PATTERN.exec(text))) {
      spans.push({ start: match.index, end: match.index + match[0].length, cls: 'entity-coord' });
    }

    const names = (participants || [])
      .flatMap((p) => {
        const role = p.participation_type || p.role;
        return [[p.name, role], [p.nickname || p.alias, role]];
      })
      .filter(([name]) => name && String(name).trim().length > 2)
      .sort((a, b) => String(b[0]).length - String(a[0]).length);

    for (const [name, role] of names) {
      const escapedForRegex = String(name).trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const nameRegex = new RegExp(`\\b${escapedForRegex}\\b`, 'gi');
      let nameMatch;
      while ((nameMatch = nameRegex.exec(text))) {
        spans.push({ start: nameMatch.index, end: nameMatch.index + nameMatch[0].length, cls: participantHighlightClass(role) });
      }
    }

    spans.sort((a, b) => a.start - b.start || (b.end - b.start) - (a.end - a.start));

    const resolved = [];
    let lastEnd = -1;
    for (const span of spans) {
      if (span.start >= lastEnd) {
        resolved.push(span);
        lastEnd = span.end;
      }
    }
    return resolved;
  }

  /**
   * @param {string} text
   * @param {any[]} participants
   */
  function renderHighlightedText(text, participants) {
    if (!text) return '';
    const spans = findHighlightSpans(text, participants);

    let html = '';
    let cursor = 0;
    for (const span of spans) {
      html += escapeHtml(text.slice(cursor, span.start));
      html += `<mark class="${span.cls}">${escapeHtml(text.slice(span.start, span.end))}</mark>`;
      cursor = span.end;
    }
    html += escapeHtml(text.slice(cursor));
    return html;
  }

  const highlightedText = $derived(renderHighlightedText(relint.raw_text || '', relint.participants || []));
  const hasCoordinateMatch = $derived(COORD_PATTERN.test(relint.raw_text || ''));
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

  <div class="highlight-legend">
    {#if hasCoordinateMatch}
      <Badge variant="success" size="sm">
        {#snippet icon()}<MapPin size={12} weight="fill" />{/snippet}
        Coordenada
      </Badge>
    {/if}
    {#if relint.participants?.length}
      <Badge variant="error" size="sm">Autor/Suspeito</Badge>
      <Badge variant="warning" size="sm">Vítima</Badge>
      <Badge variant="info" size="sm">Testemunha</Badge>
      <span class="legend-hint">
        <Users size={13} weight="bold" />
        {relint.participants.length} participante{relint.participants.length === 1 ? '' : 's'} realçado{relint.participants.length === 1 ? '' : 's'} no texto
      </span>
    {/if}
  </div>

  <div class="text-viewer-container">
    <pre class="transcription-text">{@html highlightedText || 'Sem texto bruto extraído para este documento.'}</pre>
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

  .highlight-legend {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--space-2);
  }

  .legend-hint {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
    margin-left: var(--space-1);
  }

  .text-viewer-container {
    background-color: var(--color-bg-primary);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-default);
    padding: var(--space-4);
    max-height: 480px;
    overflow-y: auto;
  }

  /* Corpo de leitura longa: typography.body-large (16px / 24px) do design system,
     em vez de fonte monoespaçada compacta — leitura mais confortável para textos extensos. */
  .transcription-text {
    font-family: var(--font-family-main);
    font-size: var(--font-size-md);
    line-height: var(--line-height-24);
    color: var(--color-text-main);
    white-space: pre-wrap;
    word-break: break-word;
    margin: 0;
  }

  .transcription-text :global(mark) {
    padding: 0 var(--space-1);
    border-radius: var(--radius-xs);
    font-weight: var(--font-weight-semibold);
    color: inherit;
  }

  .transcription-text :global(mark.entity-coord) {
    background-color: var(--color-functional-success-bg);
    color: var(--color-functional-success);
  }

  .transcription-text :global(mark.entity-victim) {
    background-color: var(--color-functional-warning-bg);
    color: var(--color-functional-warning);
  }

  .transcription-text :global(mark.entity-witness) {
    background-color: var(--color-functional-info-bg);
    color: var(--color-functional-info);
  }

  .transcription-text :global(mark.entity-suspect) {
    background-color: var(--color-functional-error-bg);
    color: var(--color-functional-error);
  }

  .transcription-text :global(mark.entity-neutral) {
    background-color: rgba(255, 255, 255, 0.08);
    color: var(--color-text-muted);
  }
</style>
