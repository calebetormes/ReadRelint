<script>
  import { page } from '$app/stores';
  import {
    SquaresFour,
    FileText,
    Crosshair,
    Users,
    ChartBar,
    Database,
    GearSix,
    CaretRight,
    CaretLeft,
    ShieldCheck
  } from 'phosphor-svelte';

  /** @type {{ expanded?: boolean, onToggle?: (expanded: boolean) => void }} */
  let {
    expanded = $bindable(false),
    onToggle
  } = $props();

  function toggleSidebar() {
    expanded = !expanded;
    if (onToggle) onToggle(expanded);
  }

  const navItems = [
    { id: 'geral', path: '/', label: 'Visão Geral', icon: SquaresFour },
    { id: 'relints', path: '/relints', label: 'Boletins RELINT', icon: FileText },
    { id: 'homicidios', path: '/homicidios', label: 'Homicídios', icon: Crosshair },
    { id: 'participantes', path: '/participantes', label: 'Participantes', icon: Users },
    { id: 'estatisticas', path: '/estatisticas', label: 'Estatísticas', icon: ChartBar },
    { id: 'banco-dados', path: '/banco-dados', label: 'Banco de Dados', icon: Database },
    { id: 'configuracoes', path: '/configuracoes', label: 'Configurações', icon: GearSix },
  ];
</script>

<aside class="sidebar" class:is-expanded={expanded}>
  <div class="sidebar-header">
    <div class="brand-icon">
      <ShieldCheck size={28} weight="fill" color="var(--color-amber-primary)" />
    </div>
    {#if expanded}
      <span class="brand-text">ReadRelint</span>
    {/if}
  </div>

  <nav class="sidebar-nav">
    {#each navItems as item}
      {@const Icon = item.icon}
      {@const isActive = $page.url.pathname === item.path}
      <a 
        href={item.path} 
        class="nav-item" 
        class:is-active={isActive}
        title={!expanded ? item.label : undefined}
      >
        <div class="nav-icon">
          <Icon size={24} weight="fill" />
        </div>
        {#if expanded}
          <span class="nav-label">{item.label}</span>
        {/if}
      </a>
    {/each}
  </nav>

  <div class="sidebar-footer">
    <div class="status-indicator" title="Ollama AI Status: Online">
      <span class="status-dot"></span>
    </div>
    {#if expanded}
      <span class="version-text">v2.0.0</span>
    {/if}
  </div>

  <button 
    class="sidebar-toggle-btn" 
    onclick={toggleSidebar}
    aria-label={expanded ? 'Recolher menu' : 'Expandir menu'}
  >
    {#if expanded}
      <CaretLeft size={16} weight="bold" />
    {:else}
      <CaretRight size={16} weight="bold" />
    {/if}
  </button>
</aside>

<style>
  .sidebar {
    position: relative;
    width: 64px;
    height: 100vh;
    background-color: var(--color-bg-surface-card);
    border-right: 1px solid var(--color-border-subtle);
    display: flex;
    flex-direction: column;
    transition: width var(--duration-normal) var(--ease-spring-snappy);
    z-index: 50;
    box-sizing: border-box;
  }

  .sidebar.is-expanded {
    width: 240px;
  }

  .sidebar-header {
    height: 64px;
    display: flex;
    align-items: center;
    padding: 0 var(--space-4);
    border-bottom: 1px solid var(--color-border-subtle);
    overflow: hidden;
    gap: var(--space-3);
  }

  .brand-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    flex-shrink: 0;
  }

  .brand-text {
    font-family: var(--font-family-main);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-main);
    white-space: nowrap;
    letter-spacing: var(--letter-spacing-tight);
  }

  .sidebar-nav {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: var(--space-4) var(--space-2);
    gap: var(--space-1);
    overflow-y: auto;
    overflow-x: hidden;
  }

  .nav-item {
    display: flex;
    align-items: center;
    height: 44px;
    padding: 0 var(--space-3);
    border-radius: var(--radius-sm);
    color: var(--color-text-muted);
    text-decoration: none;
    transition: 
      background-color var(--duration-fast) var(--ease-standard),
      color var(--duration-fast) var(--ease-standard);
    overflow: hidden;
    gap: var(--space-3);
  }

  .nav-item:hover {
    background-color: var(--color-surface-hover);
    color: var(--color-text-main);
  }

  .nav-item.is-active {
    background-color: rgba(224, 159, 62, 0.1);
    color: var(--color-amber-primary);
  }

  .nav-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    flex-shrink: 0;
  }

  .nav-label {
    font-family: var(--font-family-main);
    font-size: var(--font-size-ui);
    font-weight: var(--font-weight-medium);
    white-space: nowrap;
  }

  .sidebar-footer {
    height: 56px;
    display: flex;
    align-items: center;
    padding: 0 var(--space-4);
    border-top: 1px solid var(--color-border-subtle);
    gap: var(--space-3);
    overflow: hidden;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    flex-shrink: 0;
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: var(--radius-full);
    background-color: var(--color-functional-success);
    box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
  }

  .version-text {
    font-family: var(--font-family-mono);
    font-size: var(--font-size-xs);
    color: var(--color-text-muted);
    white-space: nowrap;
  }

  .sidebar-toggle-btn {
    position: absolute;
    right: -12px;
    top: 20px;
    width: 24px;
    height: 24px;
    border-radius: var(--radius-full);
    background-color: var(--color-bg-surface-elevated);
    border: 1px solid var(--color-border-medium);
    color: var(--color-text-muted);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 100;
    transition: 
      background-color var(--duration-fast) var(--ease-standard),
      color var(--duration-fast) var(--ease-standard),
      transform var(--duration-instant) var(--ease-spring-snappy);
    outline: none;
    padding: 0;
  }

  .sidebar-toggle-btn:hover {
    background-color: var(--color-surface-hover);
    color: var(--color-text-main);
    border-color: var(--color-amber-primary);
  }
  
  .sidebar-toggle-btn:active {
    transform: scale(0.9);
  }
</style>
