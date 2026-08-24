<script>
  import { page } from '$app/stores';
  import { List, Palette } from 'phosphor-svelte';
  import Badge from '$lib/components/ui/Badge.svelte';

  /** @type {{ title?: string, onMobileToggle?: () => void }} */
  let {
    title = '',
    onMobileToggle
  } = $props();

  // Mapear rota atual para título, caso nenhum título seja fornecido
  let currentTitle = $derived(() => {
    if (title) return title;
    const path = /** @type {string} */ ($page.url.pathname);
    if (path === '/') return 'Visão Geral';
    if (path === '/relints') return 'Gerenciamento de RELINTs';
    if (path === '/homicidios') return 'Dossiês de Homicídios';
    if (path === '/participantes') return 'Participantes & Vínculos';
    if (path === '/estatisticas') return 'Estatísticas & Analytics';
    if (path === '/banco-dados') return 'Banco de Dados';
    if (path === '/configuracoes') return 'Configurações do Sistema';
    if (path === '/design-system') return 'Design System Library';
    return 'ReadRelint';
  });
</script>

<header class="top-header">
  <div class="header-left">
    <button class="mobile-toggle" onclick={onMobileToggle} aria-label="Abrir menu mobile">
      <List size={24} weight="bold" />
    </button>
    <h1 class="page-title">{currentTitle()}</h1>
  </div>

  <div class="header-right">
    <!-- Placeholder para o seletor de temas (ThemeManager) futuro -->
    <div class="theme-selector" role="button" tabindex="0">
      <Palette size={18} weight="fill" color="var(--color-text-muted)" />
      <span class="theme-text">Dark Theme</span>
      <Badge variant="amber" size="sm">Padrão</Badge>
    </div>
  </div>
</header>

<style>
  .top-header {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 var(--space-6);
    background-color: rgba(13, 13, 13, 0.8);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--color-border-subtle);
    position: sticky;
    top: 0;
    z-index: 40;
    box-sizing: border-box;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: var(--space-4);
  }

  .mobile-toggle {
    display: none;
    background: transparent;
    border: none;
    color: var(--color-text-main);
    cursor: pointer;
    padding: var(--space-1);
    border-radius: var(--radius-sm);
  }

  .mobile-toggle:hover {
    background-color: var(--color-surface-hover);
  }

  .page-title {
    font-family: var(--font-family-main);
    font-size: 20px;
    font-weight: var(--font-weight-bold);
    color: var(--color-text-main);
    letter-spacing: var(--letter-spacing-tight);
    margin: 0;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: var(--space-4);
  }

  .theme-selector {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background-color: var(--color-bg-surface-card);
    border: 1px solid var(--color-border-medium);
    border-radius: var(--radius-default);
    cursor: pointer;
    transition: 
      background-color var(--duration-fast) var(--ease-standard),
      border-color var(--duration-fast) var(--ease-standard);
  }

  .theme-selector:hover {
    background-color: var(--color-bg-surface-elevated);
    border-color: var(--color-amber-primary);
  }

  .theme-text {
    font-family: var(--font-family-main);
    font-size: var(--font-size-ui);
    color: var(--color-text-main);
  }

  /* Responsividade básica */
  @media (max-width: 768px) {
    .mobile-toggle {
      display: flex;
    }
    
    .top-header {
      padding: 0 var(--space-4);
    }
  }
</style>
