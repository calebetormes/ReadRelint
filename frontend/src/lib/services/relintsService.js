/**
 * ============================================================================
 * ReadRelint - Serviço de Dados de RELINTs (Frontend REST Service)
 * ============================================================================
 * Este arquivo encapsula todas as chamadas de API relacionadas aos relatórios
 * de inteligência (RELINTs), incluindo listagem com filtros, busca de dossiê
 * completo por ID e atualização de campos com registro de curadoria humana.
 * ============================================================================
 */

import { apiClient } from '$lib/api/client';

/**
 * @typedef {Object} RelintSummary
 * @property {string} id
 * @property {string} source_file
 * @property {string} subject
 * @property {string} date_of_fact
 * @property {string} time_of_fact
 * @property {string} bm_group
 * @property {string} relint_type
 * @property {string} municipality
 * @property {string} neighborhood
 * @property {string} police_unit
 * @property {string} summary
 * @property {string} extraction_method
 * @property {any[]} participants
 * @property {number} participants_count
 * @property {number} images_count
 * @property {boolean} user_edited
 * @property {string} [code]
 */

/**
 * @typedef {Object} RelintDetail
 * @property {string} id
 * @property {string} source_file
 * @property {string} subject
 * @property {string} date_of_fact
 * @property {string} time_of_fact
 * @property {string} bm_group
 * @property {string} relint_type
 * @property {string} municipality
 * @property {string} neighborhood
 * @property {string} address
 * @property {string} police_unit
 * @property {string} [coordinates]
 * @property {string} [map_url]
 * @property {string} [precision_level]
 * @property {string} [precision_label]
 * @property {string} summary
 * @property {string} [content]
 * @property {string} [raw_text]
 * @property {string} [registry_number]
 * @property {string} [registry_agency]
 * @property {number|string} [registry_year]
 * @property {boolean} user_edited
 * @property {any[]} images
 * @property {any[]} participants
 * @property {any} [homicide_details]
 * @property {string} [code]
 */

/**
 * Busca a lista de RELINTs cadastrados com suporte a busca, filtros e paginação
 * @param {Object} [filters]
 * @param {string} [filters.search] - Termo de busca livre
 * @param {string} [filters.bm_group] - Filtro de especialidade / grupo BM
 * @param {string} [filters.relint_type] - Filtro de tipo de boletim
 * @param {string} [filters.municipality] - Filtro por cidade/município
 * @param {number} [filters.limit] - Limite de registros
 * @param {number} [filters.offset] - Deslocamento inicial
 * @returns {Promise<RelintSummary[]>}
 */
export async function getRelints(filters = {}) {

  const queryParams = new URLSearchParams();

  if (filters.search) queryParams.set('search', filters.search);
  if (filters.bm_group && filters.bm_group !== 'Todos') queryParams.set('bm_group', filters.bm_group);
  if (filters.relint_type && filters.relint_type !== 'Todos') queryParams.set('relint_type', filters.relint_type);
  if (filters.municipality && filters.municipality !== 'Todos') queryParams.set('municipality', filters.municipality);
  if (filters.limit !== undefined) queryParams.set('limit', String(filters.limit));
  if (filters.offset !== undefined) queryParams.set('offset', String(filters.offset));

  const queryString = queryParams.toString();
  const endpoint = `/api/v1/relints${queryString ? `?${queryString}` : ''}`;


  const data = await apiClient.get(endpoint);
  
  // Adiciona o código de exibição amigável (ex: RELINT-001) caso venha apenas o ID numérico
  return (data || []).map((/** @type {any} */ item) => ({
    ...item,
    code: item.code || (item.source_file ? item.source_file.replace(/\.pdf$/i, '') : `RELINT-${item.id}`)
  }));
}

/**
 * Busca o dossiê detalhado completo de um RELINT específico pelo ID
 * @param {string} reportId - ID ou doc_id do relatório
 * @returns {Promise<RelintDetail>}
 */
export async function getRelintById(reportId) {
  const data = await apiClient.get(`/api/v1/relints/${encodeURIComponent(reportId)}`);
  return {
    ...data,
    code: data.code || (data.source_file ? data.source_file.replace(/\.pdf$/i, '') : `RELINT-${data.id}`),
    raw_text: data.raw_text || data.content || ''
  };
}

/**
 * Atualiza os dados de um RELINT e marca a flag de curadoria humana (user_edited: true)
 * @param {string} reportId - ID do relatório
 * @param {Partial<RelintDetail>} payload - Dados atualizados
 * @returns {Promise<RelintDetail>}
 */
export async function updateRelint(reportId, payload) {
  const data = await apiClient.put(`/api/v1/relints/${encodeURIComponent(reportId)}`, payload);
  return {
    ...data,
    code: data.code || (data.source_file ? data.source_file.replace(/\.pdf$/i, '') : `RELINT-${data.id}`),
    raw_text: data.raw_text || data.content || ''
  };
}

/**
 * Retorna as estatísticas consolidadas para os KPI Cards do Dashboard em alta performance
 * @returns {Promise<{ totalRelints: number, totalPersons: number, homicideCount: number, llmRate: number, recentRelints: RelintSummary[] }>}
 */
export async function getDashboardStats() {
  try {
    // Busca métricas agregadas instantâneas em paralelo com os últimos 5 relatórios
    const [metricsData, recentRelints] = await Promise.all([
      apiClient.get('/api/v1/relints/stats').catch(() => null),
      getRelints({ limit: 5 }).catch(() => [])
    ]);

    if (metricsData) {
      return {
        totalRelints: metricsData.total_relints || 0,
        totalPersons: metricsData.total_persons || 0,
        homicideCount: metricsData.homicide_count || 0,
        llmRate: metricsData.llm_rate !== undefined ? metricsData.llm_rate : 100,
        recentRelints: (recentRelints || []).slice(0, 5)
      };
    }
  } catch (err) {
    console.warn('Fallback para cálculo de estatísticas:', err);
  }

  // Fallback de contingência caso a rota /stats não responda
  const relintsList = await getRelints();
  const totalRelints = relintsList.length;
  let totalPersons = 0;
  let homicideCount = 0;
  let llmCount = 0;

  for (const r of relintsList) {
    totalPersons += (r.participants_count || (r.participants ? r.participants.length : 0));
    if (r.bm_group === 'Homicídio') {
      homicideCount++;
    }
    const method = String(r.extraction_method || '').toLowerCase();
    const isLlm = (method.includes('ollama') || method.includes('llama') || method.includes('deepseek')) ||
      (method.includes('ia') && !method.includes('sem ia') && !method.includes('regex'));
    if (isLlm) {
      llmCount++;
    }
  }

  const llmRate = totalRelints > 0 ? Number(((llmCount / totalRelints) * 100).toFixed(1)) : 100;

  return {
    totalRelints,
    totalPersons,
    homicideCount,
    llmRate,
    recentRelints: relintsList.slice(0, 5)
  };
}

