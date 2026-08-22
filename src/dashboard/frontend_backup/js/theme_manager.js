/**
 * Theme Manager — ReadRelint Web Dashboard & Design System
 * Responsável por gerenciar a alternância dinâmica de temas, tokens e ciclo de vida de efeitos JS/HTML.
 */
const ThemeManager = {
  STORAGE_KEY: 'readrelint_theme',
  DEFAULT_THEME: 'resend-dark',

  AVAILABLE_THEMES: [
    { id: 'resend-dark', name: 'Resend Dark (Padrão)', color: '#000000', isDark: true },
    { id: 'resend-light', name: 'Resend Light (White Mode)', color: '#fbfbfd', isDark: false },
    { id: 'emerald-dark', name: 'Emerald Dark (Esmeralda)', color: '#040d0a', isDark: true },
    { id: 'nord-dark', name: 'Nord Slate (Ártico)', color: '#0b0f19', isDark: true }
  ],

  _activeEffect: null,

  init() {
    const savedTheme = localStorage.getItem(this.STORAGE_KEY) || this.DEFAULT_THEME;
    this.setTheme(savedTheme);
  },

  setTheme(themeId) {
    const validThemeObj = this.AVAILABLE_THEMES.find(t => t.id === themeId) || this.AVAILABLE_THEMES[0];
    const validTheme = validThemeObj.id;

    // Desmonta efeitos do tema anterior se existirem
    if (this._activeEffect && typeof this._activeEffect.unmount === 'function') {
      try {
        this._activeEffect.unmount();
      } catch (err) {
        console.warn('Erro ao desmontar efeito do tema:', err);
      }
    }

    // Aplica o atributo data-theme na tag raiz
    document.documentElement.setAttribute('data-theme', validTheme);
    localStorage.setItem(this.STORAGE_KEY, validTheme);

    // Sincroniza todos os selects de tema na página
    const selectors = document.querySelectorAll('#theme-selector, select[data-theme-selector]');
    selectors.forEach(sel => {
      if (sel.value !== validTheme) {
        sel.value = validTheme;
      }
    });

    // Procura por módulo de efeitos correspondente no window (ex: ResendDarkEffects, ResendLightEffects)
    const effectKey = this._getEffectKey(validTheme);
    if (typeof window !== 'undefined' && window[effectKey]) {
      this._activeEffect = window[effectKey];
      if (typeof this._activeEffect.mount === 'function') {
        const themeLayer = document.getElementById('theme-background-layer');
        this._activeEffect.mount(themeLayer);
      }
    } else {
      this._activeEffect = null;
    }
  },

  getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || this.DEFAULT_THEME;
  },

  _getEffectKey(themeId) {
    const map = {
      'resend-dark': 'ResendDarkEffects',
      'resend-light': 'ResendLightEffects'
    };
    return map[themeId] || null;
  }
};

// Inicialização automática ao carregar o DOM
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
}
