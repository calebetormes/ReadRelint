/**
 * ============================================================================
 * ReadRelint - Serviço de Eventos em Tempo Real (SSE - Server-Sent Events)
 * ============================================================================
 * Gerencia a conexão persistente com o endpoint SSE do FastAPI (/api/v1/events)
 * fornecendo auto-reconexão inteligente e distribuição de eventos reativos para
 * as páginas e componentes do SvelteKit.
 * ============================================================================
 */

import { browser } from '$app/environment';

const API_BASE_URL = '/api/v1';

class RealtimeEventsService {
  constructor() {
    /** @type {EventSource | null} */
    this.eventSource = null;
    /** @type {Map<string, Set<Function>>} */
    this.listeners = new Map();
    this.reconnectTimer = null;
    this.isConnected = false;
  }

  /**
   * Inicializa a conexão SSE no navegador
   */
  connect() {
    if (!browser || this.eventSource) return;

    try {
      this.eventSource = new EventSource(`${API_BASE_URL}/events`);

      this.eventSource.onopen = () => {
        this.isConnected = true;
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };

      this.eventSource.onerror = () => {
        this.isConnected = false;
        if (this.eventSource) {
          this.eventSource.close();
          this.eventSource = null;
        }
        // Tenta reconectar em 3 segundos
        if (!this.reconnectTimer) {
          this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;
            this.connect();
          }, 3000);
        }
      };

      // Escuta eventos do tipo 'relint_created'
      this.eventSource.addEventListener('relint_created', (event) => {
        try {
          const data = JSON.parse(event.data);
          this._emit('relint_created', data);
        } catch (e) {
          console.error('Erro ao interpretar evento relint_created:', e);
        }
      });

      // Escuta eventos gerais de log/status se enviados
      this.eventSource.addEventListener('log', (event) => {
        try {
          const data = JSON.parse(event.data);
          this._emit('log', data);
        } catch (e) {
          console.error('Erro ao interpretar evento de log:', e);
        }
      });
    } catch (err) {
      console.error('Falha ao abrir EventSource:', err);
    }
  }

  /**
   * Registra um callback para um tipo de evento
   * @param {string} eventName 
   * @param {Function} callback 
   * @returns {() => void} Função de desinscrição (cleanup)
   */
  subscribe(eventName, callback) {
    if (!this.listeners.has(eventName)) {
      this.listeners.set(eventName, new Set());
    }
    this.listeners.get(eventName)?.add(callback);

    // Garante que a conexão está ativa ao assinar
    if (browser && !this.eventSource) {
      this.connect();
    }

    return () => {
      this.listeners.get(eventName)?.delete(callback);
    };
  }

  /**
   * Dispara o evento para todos os ouvintes inscritos
   * @private
   * @param {string} eventName 
   * @param {any} data 
   */
  _emit(eventName, data) {
    const callbacks = this.listeners.get(eventName);
    if (callbacks) {
      callbacks.forEach((cb) => {
        try {
          cb(data);
        } catch (err) {
          console.error(`Erro no listener de ${eventName}:`, err);
        }
      });
    }
  }
}

export const realtimeService = new RealtimeEventsService();
