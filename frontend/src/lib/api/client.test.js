/**
 * ============================================================================
 * Testes Unitários: Client HTTP Base (client.js)
 * ============================================================================
 * Valida o comportamento do cliente REST:
 *  - Tratamento de status 200/204 e parsing seguro de JSON
 *  - Tratamento de erros HTTP sem leitura duplicada de stream de resposta
 *  - Lançamento correto da classe ApiError
 * ============================================================================
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { request, apiClient, ApiError } from '$lib/api/client';

describe('HTTP API Client (client.js)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('deve realizar requisição GET com sucesso e retornar JSON parseado', async () => {
    const mockData = { id: '1', subject: 'Homicídio Qualificado' };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockData
    });

    const result = await apiClient.get('/api/v1/relints/1');
    expect(result).toEqual(mockData);
    expect(globalThis.fetch).toHaveBeenCalledWith('/api/v1/relints/1', expect.objectContaining({
      method: 'GET'
    }));
  });

  it('deve retornar null em respostas 204 No Content', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 204
    });

    const result = await apiClient.delete('/api/v1/relints/1');
    expect(result).toBeNull();
  });

  it('deve lidar com erro 404 sem erro de body stream already read', async () => {
    const errorJson = JSON.stringify({ detail: 'RELINT not found' });

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      text: async () => errorJson
    });

    await expect(apiClient.get('/api/v1/relints/999')).rejects.toThrow(ApiError);
    await expect(apiClient.get('/api/v1/relints/999')).rejects.toMatchObject({
      status: 404,
      message: 'RELINT not found'
    });
  });

  it('deve detectar e formatar mensagem amigável quando o backend estiver offline (Status 502 Bad Gateway)', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      text: async () => 'Bad Gateway'
    });

    await expect(apiClient.get('/api/v1/relints')).rejects.toMatchObject({
      status: 502,
      message: expect.stringContaining('O servidor backend FastAPI (porta 8000) está offline')
    });
  });

  it('deve formatar requisições POST/PUT enviando payload JSON', async () => {
    const payload = { subject: 'Novo Assunto', user_edited: true };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ id: '123', ...payload })
    });

    const result = await apiClient.put('/api/v1/relints/123', payload);
    expect(result.subject).toBe('Novo Assunto');
    expect(globalThis.fetch).toHaveBeenCalledWith(
      '/api/v1/relints/123',
      expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify(payload)
      })
    );
  });
});
