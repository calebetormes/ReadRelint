<script>
	import { onMount, onDestroy } from 'svelte';
	import { createMonitoringStore } from '$lib/stores/monitoring.svelte.js';
	import { Play, Square, FolderSearch, Cpu, Trash2 } from '@lucide/svelte';

	const monitor = createMonitoringStore();

	onMount(() => {
		monitor.connect();
	});

	onDestroy(() => {
		monitor.disconnect();
	});

	let logsContainer;
	let autoScroll = $state(true);

	// Derived state para facilitar leitura
	let status = $derived(monitor.status);

	$effect(() => {
		// Auto-scroll when logs change
		if (status.logs && autoScroll && logsContainer) {
			// setTimeout to allow DOM to update first
			setTimeout(() => {
				logsContainer.scrollTop = logsContainer.scrollHeight;
			}, 10);
		}
	});

	function handleScroll(e) {
		const target = e.target;
		// Se o usuário rolou para cima (não está no fim), desabilita auto-scroll
		const isAtBottom = target.scrollHeight - target.scrollTop <= target.clientHeight + 10;
		autoScroll = isAtBottom;
	}

	function handleBrowse() {
		monitor.browseFolder();
	}

	function handleToggleLlm() {
		monitor.toggleLlm(!status.use_llm);
	}

	function handleStartStop() {
		if (status.is_monitoring) {
			monitor.stop();
		} else {
			monitor.start();
		}
	}
	
	function clearLogs() {
		// Como os logs vêm do servidor, limpar localmente pode não persistir se o servidor mandar a mesma lista
		// Ideal seria uma chamada API para limpar, mas localmente:
		status.logs = [];
	}
	
	function getLogColor(msg) {
		const upper = msg.toUpperCase();
		if (upper.includes('ERROR') || upper.includes('ERRO')) return 'var(--accent-red)';
		if (upper.includes('WARN') || upper.includes('AVISO')) return 'var(--accent-orange)';
		if (upper.includes('INFO') || upper.includes('SUCESSO')) return 'var(--accent-blue)';
		if (upper.includes('LLM') || upper.includes('OLLAMA')) return 'var(--accent-green)';
		return 'var(--ink)';
	}
</script>

<div class="monitoring-container">
	<!-- Left Side: Controls (60%) -->
	<div class="controls-pane">
		
		<!-- Pasta -->
		<div class="card">
			<h2 class="card-title" style="padding-left: 12px; margin-bottom: 16px;">
				<FolderSearch size={20} style="margin-right: 8px; color: var(--mute);" />
				Seleção de Pasta
			</h2>
			
			<div style="display: flex; gap: 12px; align-items: center;">
				<input 
					type="text" 
					class="form-control" 
					style="flex: 1;" 
					value={status.monitoring_path} 
					readonly 
					placeholder="Nenhuma pasta selecionada..."
				/>
				<button class="btn btn-secondary" onclick={handleBrowse}>
					Procurar no PC
				</button>
			</div>
		</div>

		<!-- IA e Motor -->
		<div class="card">
			<h2 class="card-title" style="padding-left: 12px; margin-bottom: 16px;">
				<Cpu size={20} style="margin-right: 8px; color: var(--mute);" />
				Controle do Motor
			</h2>
			
			<div style="display: flex; gap: 24px; align-items: center; margin-bottom: 24px;">
				<button 
					class="btn {status.is_monitoring ? 'btn-danger' : 'btn-primary'}" 
					onclick={handleStartStop}
					style="flex: 1; justify-content: center; font-size: 14px; padding: 12px;"
					disabled={!status.monitoring_path}
				>
					{#if status.is_monitoring}
						<Square size={18} style="margin-right: 8px;" />
						Pausar Leitura
					{:else}
						<Play size={18} style="margin-right: 8px;" />
						Iniciar Leitura da Pasta
					{/if}
				</button>

				<div class="switch-container" style="display: flex; align-items: center; gap: 12px; flex: 1;">
					<label class="switch" style="position: relative; display: inline-block; width: 44px; height: 24px;">
						<input type="checkbox" checked={status.use_llm} onchange={handleToggleLlm} style="opacity: 0; width: 0; height: 0;">
						<span class="slider" style="position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: {status.use_llm ? 'var(--accent-green)' : 'var(--surface-deep)'}; transition: .4s; border-radius: 34px; border: 1px solid var(--hairline-strong);">
							<span style="position: absolute; content: ''; height: 16px; width: 16px; left: 4px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; transform: {status.use_llm ? 'translateX(20px)' : 'translateX(0)'};"></span>
						</span>
					</label>
					<div style="display: flex; flex-direction: column;">
						<span style="font-size: 14px; font-weight: 500; color: var(--ink);">Ativação de IA</span>
						<span style="font-size: 11px; color: {status.ollama_online ? 'var(--accent-green)' : 'var(--mute)'};">
							{status.ollama_online ? 'Ollama Online' : 'Ollama Offline / Regex Mode'}
						</span>
					</div>
				</div>
			</div>

			<!-- Progresso -->
			<div style="display: flex; flex-direction: column; gap: 16px;">
				<div>
					<div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">
						<span style="color: var(--ash);">Arquivos na Pasta: {status.total_files_in_folder}</span>
						<span style="color: var(--ink); font-weight: 500;">{(status.total_files_in_folder > 0 ? ((status.read_files_in_folder / status.total_files_in_folder) * 100).toFixed(1) : 0)}%</span>
					</div>
					<div class="progress-bg" style="width: 100%; height: 8px; background: var(--surface-deep); border-radius: 4px; overflow: hidden; border: 1px solid var(--hairline);">
						<div class="progress-bar" style="height: 100%; background: var(--accent-blue); width: {status.total_files_in_folder > 0 ? (status.read_files_in_folder / status.total_files_in_folder) * 100 : 0}%; transition: width 0.3s ease;"></div>
					</div>
				</div>
				
				<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 8px;">
					<div style="background: var(--surface-deep); padding: 12px; border-radius: 8px; border: 1px solid var(--hairline);">
						<div style="font-size: 11px; color: var(--ash); text-transform: uppercase;">Lidos c/ Sucesso</div>
						<div style="font-size: 20px; font-weight: 700; color: var(--accent-green);">{status.processed_count}</div>
					</div>
					<div style="background: var(--surface-deep); padding: 12px; border-radius: 8px; border: 1px solid var(--hairline);">
						<div style="font-size: 11px; color: var(--ash); text-transform: uppercase;">Ignorados (Não RELINT)</div>
						<div style="font-size: 20px; font-weight: 700; color: var(--accent-orange);">{status.skipped_count}</div>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Right Side: Terminal (40%) -->
	<div class="terminal-pane">
		<div class="terminal-header">
			<span style="font-family: var(--font-mono); font-size: 12px; color: var(--ash);">>_ Console de Logs</span>
			<button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick={clearLogs} title="Limpar Console">
				<Trash2 size={14} />
			</button>
		</div>
		<div class="terminal-body" bind:this={logsContainer} onscroll={handleScroll}>
			{#if status.logs && status.logs.length > 0}
				{#each status.logs as log}
					<div class="log-line" style="color: {getLogColor(log)};">
						{log}
					</div>
				{/each}
			{:else}
				<div class="log-line" style="color: var(--mute);">Aguardando logs...</div>
			{/if}
		</div>
	</div>
</div>

<style>
	.monitoring-container {
		display: grid;
		grid-template-columns: 3fr 2fr;
		gap: 24px;
		height: calc(100vh - 80px);
		padding: 24px;
		box-sizing: border-box;
	}

	.controls-pane {
		display: flex;
		flex-direction: column;
		gap: 0;
	}

	.terminal-pane {
		background-color: #050505; /* Fundo terminal escuro puro */
		border: 1px solid var(--hairline-strong);
		border-radius: var(--r-lg);
		display: flex;
		flex-direction: column;
		overflow: hidden;
		box-shadow: inset 0 4px 12px rgba(0,0,0,0.5);
	}

	.terminal-header {
		background-color: var(--surface-card);
		border-bottom: 1px solid var(--hairline-strong);
		padding: 8px 16px;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.terminal-body {
		flex: 1;
		padding: 16px;
		overflow-y: auto;
		font-family: var(--font-mono);
		font-size: 12px;
		line-height: 1.5;
	}

	.log-line {
		margin-bottom: 4px;
		word-break: break-all;
		border-bottom: 1px solid rgba(255,255,255,0.02);
		padding-bottom: 2px;
	}

	/* Form Controls based on standard main.css */
	.form-control {
		background-color: var(--surface-deep);
		border: 1px solid var(--hairline-strong);
		color: var(--ink);
		padding: 8px 12px;
		border-radius: var(--r-md);
		outline: none;
		font-family: var(--font-ui);
		font-size: 14px;
	}
	
	.form-control:focus {
		border-color: var(--accent-blue);
	}

	.btn {
		display: inline-flex;
		align-items: center;
		padding: 8px 16px;
		border-radius: var(--r-md);
		border: 1px solid transparent;
		cursor: pointer;
		font-weight: 500;
		transition: all 0.2s;
		font-family: var(--font-ui);
		font-size: 13px;
	}

	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-primary {
		background-color: var(--ink);
		color: var(--canvas);
	}

	.btn-primary:hover:not(:disabled) {
		background-color: var(--charcoal);
	}

	.btn-secondary {
		background-color: var(--surface-elevated);
		border-color: var(--hairline-strong);
		color: var(--ink);
	}

	.btn-secondary:hover:not(:disabled) {
		background-color: var(--surface-raised);
		border-color: var(--hairline);
	}
	
	.btn-danger {
		background-color: rgba(239, 68, 68, 0.1);
		border-color: rgba(239, 68, 68, 0.3);
		color: #ef4444;
	}
	
	.btn-danger:hover:not(:disabled) {
		background-color: rgba(239, 68, 68, 0.2);
	}

	@media (max-width: 992px) {
		.monitoring-container {
			grid-template-columns: 1fr;
			height: auto;
		}
		
		.terminal-pane {
			height: 400px;
		}
	}
</style>
