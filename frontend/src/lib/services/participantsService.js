/**
 * ============================================================================
 * ReadRelint - Serviço de Dados de Participantes (Frontend REST Service)
 * ============================================================================
 * Encapsula todas as chamadas de API para pessoas qualificadas e dossiês:
 * - listagem com busca e filtro de reincidentes
 * - busca detalhada por ID/chave de pessoa
 * - atualização e edição cadastral com persistência no SQLite
 * ============================================================================
 */
import { apiClient } from '$lib/api/client';

/**
 * @typedef {Object} LinkedRelint
 * @property {number} relint_id
 * @property {string} source_file
 * @property {string} subject
 * @property {string} date_of_fact
 * @property {string} participation_type
 * @property {string} municipality
 */

/**
 * @typedef {Object} PersonDossier
 * @property {string} person_id
 * @property {string} name
 * @property {string} nickname
 * @property {string} document
 * @property {string} background
 * @property {string} photo_path
 * @property {string[]} photos
 * @property {number} linked_relints_count
 * @property {LinkedRelint[]} linked_relints
 */

/**
 * Busca a lista de participantes com suporte a busca e filtros
 * @param {Object} [filters]
 * @param {string} [filters.search] - Termo de busca por nome, alcunha ou documento
 * @param {boolean} [filters.recurrent_only] - Filtrar apenas reincidentes (> 1 RELINT)
 * @returns {Promise<PersonDossier[]>}
 */
export async function getParticipants(filters = {}) {
  const queryParams = new URLSearchParams();

  if (filters.search) queryParams.set('search', filters.search);
  if (filters.recurrent_only) queryParams.set('recurrent_only', 'true');

  const queryString = queryParams.toString();
  const endpoint = `/api/v1/participants${queryString ? `?${queryString}` : ''}`;

  return await apiClient.get(endpoint);
}

/**
 * Busca o dossiê detalhado completo de um participante
 * @param {string} personId
 * @returns {Promise<PersonDossier>}
 */
export async function getParticipantById(personId) {
  return await apiClient.get(`/api/v1/participants/${encodeURIComponent(personId)}`);
}

/**
 * Atualiza os dados cadastrais de um participante
 * @param {string} personId
 * @param {Partial<PersonDossier>} payload
 * @returns {Promise<PersonDossier>}
 */
export async function updateParticipant(personId, payload) {
  return await apiClient.put(`/api/v1/participants/${encodeURIComponent(personId)}`, payload);
}
