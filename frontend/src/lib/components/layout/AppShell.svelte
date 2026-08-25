<script>
  import Sidebar from './Sidebar.svelte';
  import Header from './Header.svelte';

  /** @type {{ children?: import('svelte').Snippet }} */
  let { children } = $props();

  let sidebarExpanded = $state(false);
  let mobileMenuOpen = $state(false);
</script>


<div class="app-layout">
  <!-- Sidebar Container -->
  <div class="app-sidebar" class:mobile-open={mobileMenuOpen}>
    <Sidebar bind:expanded={sidebarExpanded} />
  </div>

  <!-- Main Content Area -->
  <div class="app-main">
    <Header onMobileToggle={() => mobileMenuOpen = !mobileMenuOpen} />
    
    <main class="app-content">
      {#if children}
        {@render children()}
      {/if}
    </main>
  </div>


  <!-- Mobile Overlay -->
  {#if mobileMenuOpen}
    <div 
      class="mobile-overlay"
      role="button"
      tabindex="0"
      aria-label="Fechar menu"
      onclick={() => mobileMenuOpen = false}
      onkeydown={(e) => e.key === 'Enter' && (mobileMenuOpen = false)}
    ></div>
  {/if}
</div>

<style>
  .app-layout {
    display: flex;
    width: 100%;
    min-height: 100vh;
    background-color: var(--color-bg-primary);
    overflow: hidden;
  }

  .app-sidebar {
    flex-shrink: 0;
    z-index: 50;
  }

  .app-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
    height: 100vh;
    overflow-y: auto;
    overflow-x: hidden;
    position: relative;
  }

  .app-content {
    flex: 1;
    padding: var(--space-6);
    box-sizing: border-box;
    width: 100%;
    position: relative;
  }

  .mobile-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    z-index: 40;
  }

  @media (max-width: 768px) {
    .app-sidebar {
      position: fixed;
      top: 0;
      bottom: 0;
      left: 0;
      transform: translateX(-100%);
      transition: transform var(--duration-normal) var(--ease-spring-snappy);
    }
    
    .app-sidebar.mobile-open {
      transform: translateX(0);
    }

    .mobile-overlay {
      display: block;
    }
    
    .app-content {
      padding: var(--space-4);
    }
  }
</style>
