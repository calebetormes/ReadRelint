/**
 * ============================================================================
 * ReadRelint - HTTP API Client Base
 * ============================================================================
 * Este arquivo fornece um cliente HTTP centralizado para comunicação com a
 * API REST do FastAPI local (:8000). Trata parsing automático de JSON, headers
 * e lançamentos de erro consistentes para a camada de serviços da aplicação.
 * ============================================================================
 */

const BASE_URL = ''; // Vazio para usar o proxy relativo do Vite (/api/v1/...)

/**
 * Custom error class for API failures
 */
export class ApiError extends Error {
  /**
   * @param {string} message
   * @param {number} status
   * @param {any} [data]
   */
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Executa uma requisição HTTP tipada com fallback e tratamento de erros
 * @template T
 * @param {string} endpoint - Caminho relativo da API (ex: '/api/v1/relints')
 * @param {RequestInit} [options] - Opções padrão do fetch
 * @returns {Promise<T>}
 */
export async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...(options.headers || {})
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers
    });

    if (!response.ok) {
      let errorData = null;
      let rawText = '';
      try {
        rawText = await response.text();
        errorData = rawText ? JSON.parse(rawText) : null;
      } catch {
        errorData = rawText;
      }
      
      let errorMsg = '';
      if (response.status === 502 || response.status === 503 || response.status === 504) {
        errorMsg = `O servidor backend FastAPI (porta 8000) está offline ou indisponível (Status ${response.status}). Inicie o servidor para carregar os dados.`;
      } else if (errorData && typeof errorData === 'object' && errorData.detail) {
        errorMsg = errorData.detail;
      } else {
        errorMsg = rawText || `Request failed with status ${response.status}`;
      }

      throw new ApiError(errorMsg, response.status, errorData);
    }

    // Se for status 204 No Content, retorna null
    if (response.status === 204) {
      return /** @type {T} */ (null);
    }

    return /** @type {T} */ (await response.json());
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }
    // Erros de rede ou conexão recusada
    throw new ApiError(
      err instanceof Error ? err.message : 'Falha na conexão com o servidor local FastAPI.',
      0,
      err
    );
  }
}

/**
 * Métodos auxiliares de conveniência
 */
export const apiClient = {
  /**
   * @template T
   * @param {string} endpoint
   * @param {RequestInit} [options]
   */
  get: (endpoint, options = {}) => request(endpoint, { ...options, method: 'GET' }),

  /**
   * @template T
   * @param {string} endpoint
   * @param {any} [body]
   * @param {RequestInit} [options]
   */
  post: (endpoint, body, options = {}) =>
    request(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined
    }),

  /**
   * @template T
   * @param {string} endpoint
   * @param {any} [body]
   * @param {RequestInit} [options]
   */
  put: (endpoint, body, options = {}) =>
    request(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined
    }),

  /**
   * @template T
   * @param {string} endpoint
   * @param {RequestInit} [options]
   */
  delete: (endpoint, options = {}) => request(endpoint, { ...options, method: 'DELETE' })
};
