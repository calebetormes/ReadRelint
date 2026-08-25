/**
 * ============================================================================
 * ReadRelint - Gerenciamento de Sessão & Autenticação do Operador
 * ============================================================================
 * Armazena as informações do policial/analista logado no sistema localmente
 * utilizando o localStorage, permitindo troca rápida de plantão e perfil.
 * ============================================================================
 */
import { writable } from 'svelte/store';

const STORAGE_KEY = 'readrelint_auth_operator';

/**
 * @typedef {Object} OperatorUser
 * @property {string} name
 * @property {string} badge
 * @property {string} role
 * @property {string} unit
 * @property {string} status
 * @property {boolean} isAuthenticated
 */

/** @type {OperatorUser} */
const defaultUser = {
  name: 'Capitão Silva',
  badge: 'BM-84920',
  role: 'Analista Chefe de Inteligência',
  unit: '2º BPM / P2',
  status: 'Em Serviço',
  isAuthenticated: true
};

function createAuthStore() {
  let initial = defaultUser;

  if (typeof window !== 'undefined') {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        initial = { ...defaultUser, ...JSON.parse(saved) };
      } else {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultUser));
      }
    } catch {
      initial = defaultUser;
    }
  }

  const { subscribe, set, update } = writable(initial);

  return {
    subscribe,
    /**
     * Atualiza os dados do operador logado
     * @param {Partial<OperatorUser>} data
     */
    login: (data) => {
      update((curr) => {
        const next = { ...curr, ...data, isAuthenticated: true };
        if (typeof window !== 'undefined') {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
        }
        return next;
      });
    },
    /**
     * Encerra a sessão ou limpa os dados
     */
    logout: () => {
      update((curr) => {
        const next = { ...curr, isAuthenticated: false };
        if (typeof window !== 'undefined') {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
        }
        return next;
      });
    },
    /**
     * Alterna o status operacional (ex: 'Em Serviço', 'Intervalo', 'Plantão Fechado')
     * @param {string} status
     */
    setStatus: (status) => {
      update((curr) => {
        const next = { ...curr, status };
        if (typeof window !== 'undefined') {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
        }
        return next;
      });
    }
  };
}

export const authStore = createAuthStore();
