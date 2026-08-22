<script>
	import '../app.css';
	import { page } from '$app/stores';
	import {
		FileText,
		Crosshair,
		Users,
		MapPin,
		BarChart3,
		Image as ImageIcon,
		Cpu,
		Info,
		Menu,
		ChevronLeft,
		ChevronRight
	} from '@lucide/svelte';

	let { children } = $props();

	let sidebarCollapsed = $state(false);
	let currentTheme = $state('resend-dark');

	function toggleSidebar() {
		sidebarCollapsed = !sidebarCollapsed;
	}

	function setTheme(event) {
		currentTheme = event.target.value;
		document.documentElement.setAttribute('data-theme', currentTheme);
	}

	const navItems = [
		{ id: 'relints', path: '/', title: 'RELINTs', icon: FileText },
		{ id: 'homicides', path: '/homicides', title: 'Especialidades', icon: Crosshair },
		{ id: 'participants', path: '/participants', title: 'Participantes', icon: Users },
		{ id: 'municipalities', path: '/municipalities', title: 'Municípios', icon: MapPin },
		{ id: 'crimes', path: '/crimes', title: 'Estatísticas', icon: BarChart3 },
		{ id: 'gallery', path: '/gallery', title: 'Anexos & Fotos', icon: ImageIcon },
		{ id: 'monitoring', path: '/monitoring', title: 'Monitoramento & IA', icon: Cpu },
		{ id: 'about', path: '/about', title: 'Sobre', icon: Info }
	];

	let currentTitle = $derived(navItems.find((item) => item.path === $page.url.pathname)?.title || 'ReadRelint');
</script>

<div id="app-container">
	<div class="sidebar-overlay" id="sidebar-overlay"></div>

	<!-- Sidebar Navigation -->
	<aside class="sidebar" class:collapsed={sidebarCollapsed} id="sidebar">
		<button class="sidebar-toggle-btn" id="sidebar-toggle" title="Recolher/Expandir Menu Lateral" onclick={toggleSidebar}>
			<svg class="sidebar-toggle-svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="transform: {sidebarCollapsed ? 'rotate(180deg)' : 'rotate(0deg)'}; transition: transform 0.3s ease;">
				<polyline points="15 18 9 12 15 6"></polyline>
			</svg>
		</button>

		<div>
			<div class="sidebar-header">
				<div class="sidebar-title">ReadRelint</div>
			</div>

			<ul class="nav-list">
				{#each navItems as item}
					<a href={item.path} style="text-decoration: none; color: inherit;">
						<li class="nav-item" class:active={$page.url.pathname === item.path} title={item.title}>
							<svelte:component this={item.icon} size={20} />
							<span>{item.title}</span>
						</li>
					</a>
				{/each}
			</ul>
		</div>

		<div class="sidebar-footer">
			<div class="status-indicator" title="Motor Local Offline">
				<span class="dot"></span>
				{#if !sidebarCollapsed}
					<span>Motor Local Offline</span>
				{/if}
			</div>
			{#if !sidebarCollapsed}
				<div class="sidebar-footer-text">v2.0.0 (SvelteKit)</div>
			{/if}
		</div>
	</aside>

	<!-- Content Workspace -->
	<main class="content-area">
		<!-- Top Bar -->
		<header class="top-header" style="display: flex; justify-content: space-between; align-items: center;">
			<div style="display: flex; align-items: center; gap: 12px;">
				<button type="button" class="mobile-menu-btn" id="mobile-menu-btn" title="Abrir Menu">
					<Menu size={24} />
				</button>
				<h1 class="page-title" id="page-title">{currentTitle}</h1>
			</div>
			<div style="display: flex; align-items: center; gap: 8px;">
				<span style="font-size: 12px; color: var(--mute); font-weight: 500;">🎨 Tema:</span>
				<select id="theme-selector" onchange={setTheme} value={currentTheme} style="background: var(--surface-card); color: var(--ink); border: 1px solid var(--hairline-strong); padding: 4px 10px; border-radius: var(--r-sm); font-size: 12px; cursor: pointer; outline: none;">
					<option value="resend-dark">Resend Dark</option>
					<option value="resend-light">Resend Light</option>
					<option value="emerald-dark">Emerald Dark</option>
					<option value="nord-dark">Nord Slate</option>
				</select>
			</div>
		</header>

		<!-- Tab Content Area -->
		<section class="tab-content active" style="display: block;">
			{@render children()}
		</section>
	</main>
</div>

<style>
	/* Any Svelte specific component styles can go here, but most are in main.css */
	:global(body) {
		margin: 0;
		padding: 0;
	}
	
	.nav-item {
		display: flex;
		align-items: center;
		gap: 12px;
	}
</style>
