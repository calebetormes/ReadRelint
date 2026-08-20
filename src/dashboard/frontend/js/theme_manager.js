/**
 * Theme Manager — ReadRelint Web Dashboard
 * Responsável por gerenciar a alternância dinâmica de temas (Design Layer).
 */
const ThemeManager = {
  STORAGE_KEY: 'readrelint_theme',
  DEFAULT_THEME: 'resend-dark',

  AVAILABLE_THEMES: [
    { id: 'resend-dark', name: 'Resend Dark (Padrão)', color: '#000000' },
    { id: 'emerald-dark', name: 'Emerald Dark (Esmeralda)', color: '#040d0a' },
    { id: 'nord-dark', name: 'Nord Slate (Ártico)', color: '#0b0f19' }
  ],

  init() {
    const savedTheme = localStorage.getItem(this.STORAGE_KEY) || this.DEFAULT_THEME;
    this.setTheme(savedTheme);
  },

  setTheme(themeId) {
    const validTheme = this.AVAILABLE_THEMES.find(t => t.id === themeId) ? themeId : this.DEFAULT_THEME;
    document.documentElement.setAttribute('data-theme', validTheme);
    localStorage.setItem(this.STORAGE_KEY, validTheme);
  },

  getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || this.DEFAULT_THEME;
  }
};

// Inicialização automática ao carregar o script
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
}
