export function createMonitoringStore() {
	let status = $state({
		is_monitoring: false,
		use_llm: false,
		current_filename: '',
		total_files_in_folder: 0,
		skipped_count: 0,
		processed_count: 0,
		total_discovered: 0,
		read_files_in_folder: 0,
		ollama_online: false,
		logs: [],
		monitoring_path: ''
	});

	let eventSource = null;

	function connect() {
		if (eventSource) return;
		eventSource = new EventSource('/api/monitoring/events');
		eventSource.onmessage = (event) => {
			const data = JSON.parse(event.data);
			status.is_monitoring = data.is_monitoring;
			status.use_llm = data.use_llm;
			status.current_filename = data.current_filename;
			status.total_files_in_folder = data.total_files_in_folder;
			status.skipped_count = data.skipped_count;
			status.processed_count = data.processed_count;
			status.total_discovered = data.total_discovered;
			status.read_files_in_folder = data.read_files_in_folder;
			status.ollama_online = data.ollama_online;
			
			// Somente adiciona novos logs para evitar re-render pesado (O backend manda os mais recentes)
			// Para simplificar e bater 1:1, a gente simplesmente atualiza a lista
			status.logs = data.logs;
		};
		
		// Initial fetch to get path
		fetch('/api/monitoring/status').then(r => r.json()).then(data => {
			status.monitoring_path = data.monitoring_path;
		});
	}

	function disconnect() {
		if (eventSource) {
			eventSource.close();
			eventSource = null;
		}
	}

	async function browseFolder() {
		try {
			const res = await fetch('/api/monitoring/browse', { method: 'POST' });
			const data = await res.json();
			if (data.status === 'success') {
				status.monitoring_path = data.path;
			}
		} catch (err) {
			console.error('Erro ao selecionar pasta', err);
		}
	}

	async function setPath(path) {
		try {
			const res = await fetch('/api/monitoring/path', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ path })
			});
			const data = await res.json();
			if (data.status === 'success') {
				status.monitoring_path = path;
			}
		} catch (err) {
			console.error('Erro ao definir pasta', err);
		}
	}

	async function start() {
		try {
			await fetch('/api/monitoring/start', { method: 'POST' });
		} catch (err) {
			console.error('Erro ao iniciar', err);
		}
	}

	async function stop() {
		try {
			await fetch('/api/monitoring/stop', { method: 'POST' });
		} catch (err) {
			console.error('Erro ao parar', err);
		}
	}

	async function toggleLlm(use_llm) {
		try {
			await fetch('/api/monitoring/toggle-llm', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ use_llm })
			});
		} catch (err) {
			console.error('Erro ao alternar IA', err);
		}
	}

	return {
		get status() { return status; },
		connect,
		disconnect,
		browseFolder,
		setPath,
		start,
		stop,
		toggleLlm
	};
}
