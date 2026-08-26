/**
 * ============================================================================
 * ReadRelint - Serviço de Eventos em Tempo Real (WebSockets Bidirecional)
 * ============================================================================
 * Gerencia a conexão persistente com o endpoint WebSocket do FastAPI (/api/v1/events)
 * fornecendo auto-reconexão inteligente e distribuição de eventos reativos para
 * as páginas e componentes do SvelteKit.
 * ============================================================================
 */

import { browser } from '$app/environment';

const API_BASE_PATH = '/api/v1/events';

class RealtimeEventsService {
  constructor() {
    /** @type {WebSocket | null} */
    this.ws = null;
    /** @type {Map<string, Set<Function>>} */
    this.listeners = new Map();
    this.reconnectTimer = null;
    this.isConnected = false;
  }

  /**
   * Inicializa a conexão WebSocket no navegador
   */
  connect() {
    if (!browser || (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING))) return;

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}${API_BASE_PATH}`;

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.isConnected = true;
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const eventType = payload.event || 'message';
          const eventData = payload.data || {};
          
          this._emit(eventType, eventData);
        } catch (e) {
          console.error('Erro ao interpretar mensagem do WebSocket:', e);
        }
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.ws = null;
        
        // Tenta reconectar em 3 segundos
        if (!this.reconnectTimer) {
          this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;
            this.connect();
          }, 3000);
        }
      };

      this.ws.onerror = (error) => {
        console.error('Erro na conexão WebSocket:', error);
        // O onclose será disparado em seguida, cuidando da reconexão
      };

    } catch (err) {
      console.error('Falha ao abrir WebSocket:', err);
    }
  }

  /**
   * Envia uma mensagem para o servidor via WebSocket
   * @param {string} eventName 
   * @param {any} data 
   */
  send(eventName, data = {}) {
    if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
      const payload = JSON.stringify({ event: eventName, data: data });
      this.ws.send(payload);
    } else {
      console.warn('Não foi possível enviar a mensagem, WebSocket não está conectado.');
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
    if (browser && !this.ws) {
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
