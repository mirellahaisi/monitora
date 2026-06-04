(function () {
  const STORAGE_KEY = "tema";
  const DARK_CLASS = "dark";
  const STYLE_ID = "dark-mode-dinamico";
  const TOGGLE_SELECTOR = "#btnDarkMode, [data-theme-toggle]";
  const ICON_SELECTOR = "#iconeDarkMode, [data-theme-icon]";

  const estilosDark = `
    body.dark {
      --text: #c8dde8;
      --accent: #7de8d0;
      --card: rgba(23, 36, 51, 0.92);
      --teal: #57dbbd;
      --teal-light: #6fc9d6;
      --dark: #e8faff;
      --mid: #d0e4ee;
      --muted: #8faebe;
      --bg: #101923;
      --white: #172433;
      --grad: linear-gradient(135deg, #315f72 0%, #1d705f 55%, #236d7a 100%);
      background: #101923 !important;
      color: #c8dde8 !important;
      color-scheme: dark;
    }

    body.dark.index-page nav,
    body.dark.auth-page nav {
      background: rgba(16, 25, 35, 0.9) !important;
      border-bottom-color: rgba(125, 232, 208, 0.16) !important;
      box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22) !important;
    }

    body.dark .inicio-main,
    body.dark .right-panel,
    body.dark .features,
    body.dark .team,
    body.dark .report-page,
    body.dark .report-shell {
      background: var(--bg) !important;
      color: var(--text) !important;
    }

    body.dark .left-panel {
      background: linear-gradient(145deg, #142638 0%, #13362f 55%, #143241 100%) !important;
    }

    body.dark .stats,
    body.dark .cta-section,
    body.dark footer {
      background: #0b141d !important;
    }

    body.dark .sidebar {
      background: linear-gradient(180deg, #1f3d47, #1a4a3f) !important;
      box-shadow: 2px 0 20px rgba(0, 0, 0, 0.26) !important;
    }

    body.dark .sidebar-link {
      color: rgba(215, 240, 244, 0.86) !important;
    }

    body.dark .sidebar-link.active,
    body.dark .sidebar-link:hover {
      background: rgba(255, 255, 255, 0.12) !important;
      color: var(--accent) !important;
    }

    body.dark .logout-button {
      color: rgba(215, 240, 244, 0.72) !important;
    }

    body.dark .logout-button:hover {
      background: rgba(255, 255, 255, 0.1) !important;
      color: var(--accent) !important;
    }

    body.dark .btn-dark-mode,
    body.dark .nav-theme-toggle {
      background: rgba(125, 232, 208, 0.1) !important;
      color: var(--accent) !important;
    }

    body.dark .btn-dark-mode:hover,
    body.dark .nav-theme-toggle:hover {
      background: rgba(125, 232, 208, 0.18) !important;
    }

    body.dark .login-card,
    body.dark .user-menu-button,
    body.dark .user-dropdown,
    body.dark .notas-filtros,
    body.dark .coord-filtros,
    body.dark .notas-card,
    body.dark .coord-card,
    body.dark .coord-vazio,
    body.dark .presenca-filtros,
    body.dark .presenca-card,
    body.dark .aviso-card,
    body.dark .cal-wrapper,
    body.dark .month-picker-dropdown,
    body.dark .modal-box,
    body.dark .modal-content,
    body.dark .tabs,
    body.dark .mensagem-card,
    body.dark .envio-card,
    body.dark .turma-card,
    body.dark .aluno-card,
    body.dark .gestao-card,
    body.dark .perfil-card,
    body.dark .table-card,
    body.dark .dashboard-mockup,
    body.dark .feature-card,
    body.dark .team-card,
    body.dark .dv-card,
    body.dark .dv-stat,
    body.dark .report-card,
    body.dark .swal2-popup {
      background: var(--white) !important;
      color: var(--text) !important;
      border-color: rgba(125, 232, 208, 0.16) !important;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.24) !important;
    }

    body.dark input,
    body.dark textarea,
    body.dark select,
    body.dark .field,
    body.dark .form-select,
    body.dark .form-input,
    body.dark .form-textarea,
    body.dark .nota-input,
    body.dark .observacao-presenca,
    body.dark .search-box input,
    body.dark .swal2-input,
    body.dark .swal2-textarea,
    body.dark .swal2-select {
      background: #1a2f40 !important;
      color: var(--text) !important;
      border-color: rgba(125, 232, 208, 0.18) !important;
    }

    body.dark input:focus,
    body.dark textarea:focus,
    body.dark select:focus,
    body.dark .field:focus,
    body.dark .form-select:focus,
    body.dark .form-input:focus,
    body.dark .form-textarea:focus,
    body.dark .nota-input:focus,
    body.dark .observacao-presenca:focus,
    body.dark .search-box input:focus,
    body.dark .swal2-input:focus,
    body.dark .swal2-textarea:focus,
    body.dark .swal2-select:focus {
      background: #203548 !important;
      border-color: rgba(125, 232, 208, 0.4) !important;
      box-shadow: 0 0 0 3px rgba(125, 232, 208, 0.14) !important;
    }

    body.dark input[readonly],
    body.dark .perfil-field input[readonly] {
      background: #142434 !important;
      color: var(--muted) !important;
      border-color: rgba(125, 232, 208, 0.12) !important;
    }

    body.dark input::placeholder,
    body.dark textarea::placeholder,
    body.dark .search-box input::placeholder,
    body.dark .swal2-input::placeholder,
    body.dark .swal2-textarea::placeholder {
      color: #7193a5 !important;
    }

    body.dark table,
    body.dark thead,
    body.dark tbody,
    body.dark tr,
    body.dark td {
      background: #162535 !important;
      color: var(--text) !important;
      border-color: rgba(125, 232, 208, 0.12) !important;
    }

    body.dark th {
      background: #1a3a50 !important;
      color: var(--accent) !important;
      border-color: rgba(125, 232, 208, 0.16) !important;
    }

    body.dark .cal-day-cell,
    body.dark .cal-day-header,
    body.dark .mock-main,
    body.dark .mock-card,
    body.dark .dv-ev {
      background-color: #142232 !important;
      border-color: rgba(125, 232, 208, 0.12) !important;
    }

    body.dark .cal-day-cell:hover,
    body.dark tbody tr:hover,
    body.dark .mensagem-card:hover,
    body.dark .team-card:hover,
    body.dark .feature-card:hover {
      background: #1a2f40 !important;
    }

    body.dark .tab-btn:not(.active) {
      background: #172433 !important;
      color: var(--mid) !important;
      border-color: rgba(125, 232, 208, 0.16) !important;
    }

    body.dark .tab-btn:not(.active):hover {
      background: rgba(125, 232, 208, 0.08) !important;
      color: var(--accent) !important;
      border-color: rgba(125, 232, 208, 0.28) !important;
    }

    body.dark .btn-limpar {
      background: #1a2f40 !important;
      color: var(--mid) !important;
      border: 1.5px solid rgba(125, 232, 208, 0.18) !important;
    }

    body.dark .btn-limpar:hover {
      background: rgba(125, 232, 208, 0.08) !important;
      color: var(--accent) !important;
      border-color: rgba(125, 232, 208, 0.28) !important;
    }

    body.dark .dv-card-head,
    body.dark .coord-card-header,
    body.dark .aluno-materia-header {
      background: rgba(255, 255, 255, 0.02) !important;
      border-color: rgba(125, 232, 208, 0.12) !important;
    }

    body.dark .coord-rodape,
    body.dark .perfil-actions,
    body.dark .perfil-divider,
    body.dark .modal-actions,
    body.dark .dv-metric {
      border-color: rgba(125, 232, 208, 0.12) !important;
    }

    body.dark .dv-day,
    body.dark .dv-msg,
    body.dark .nota-bloco {
      background: #1a2a3b !important;
      border-color: rgba(125, 232, 208, 0.12) !important;
    }

    body.dark .dv-day.today {
      background: rgba(87, 219, 189, 0.14) !important;
      border-color: rgba(125, 232, 208, 0.3) !important;
    }

    body.dark .dv-day.today .dv-dayname {
      color: var(--accent) !important;
    }

    body.dark .dv-day.today .dv-daynum {
      color: var(--dark) !important;
    }

    body.dark .dv-msg.unread {
      background: rgba(56, 189, 248, 0.12) !important;
    }

    body.dark .dv-row:hover,
    body.dark .dv-msg:hover {
      background: rgba(125, 232, 208, 0.08) !important;
    }

    body.dark .dv-track {
      background: rgba(143, 174, 190, 0.14) !important;
    }

    body.dark .dv-circle-bg {
      stroke: rgba(143, 174, 190, 0.18) !important;
    }

    body.dark .dv-col-axis {
      background: linear-gradient(
        90deg,
        rgba(143, 174, 190, 0.08),
        rgba(143, 174, 190, 0.2)
      ) !important;
    }

    body.dark .dv-alert-strip.das-warn {
      background: rgba(245, 158, 11, 0.1) !important;
      color: #fcd34d !important;
      border: 1px solid rgba(245, 158, 11, 0.26) !important;
    }

    body.dark .dv-tag,
    body.dark .coord-badge {
      background: rgba(125, 232, 208, 0.12) !important;
      color: var(--accent) !important;
      border-color: rgba(125, 232, 208, 0.18) !important;
    }

    body.dark .dv-pill.dp-neu {
      background: rgba(143, 174, 190, 0.14) !important;
      color: var(--mid) !important;
    }

    body.dark .dv-pill.dp-up {
      background: rgba(34, 197, 94, 0.16) !important;
      color: #86efac !important;
    }

    body.dark .dv-pill.dp-warn {
      background: rgba(245, 158, 11, 0.16) !important;
      color: #fcd34d !important;
    }

    body.dark .dv-pill.dp-bad {
      background: rgba(239, 68, 68, 0.16) !important;
      color: #fca5a5 !important;
    }

    body.dark .db-green {
      background: rgba(34, 197, 94, 0.16) !important;
      color: #86efac !important;
    }

    body.dark .db-yellow {
      background: rgba(245, 158, 11, 0.16) !important;
      color: #fcd34d !important;
    }

    body.dark .db-red {
      background: rgba(239, 68, 68, 0.16) !important;
      color: #fca5a5 !important;
    }

    body.dark .db-blue {
      background: rgba(59, 130, 246, 0.16) !important;
      color: #93c5fd !important;
    }

    body.dark .db-purple {
      background: rgba(139, 92, 246, 0.16) !important;
      color: #c4b5fd !important;
    }

    body.dark .db-gray {
      background: rgba(148, 163, 184, 0.14) !important;
      color: #cbd5e1 !important;
    }

    body.dark .db-orange {
      background: rgba(249, 115, 22, 0.16) !important;
      color: #fdba74 !important;
    }

    body.dark .swal2-title {
      color: var(--dark) !important;
    }

    body.dark .swal2-html-container,
    body.dark .swal2-input-label,
    body.dark .swal2-validation-message {
      color: var(--text) !important;
    }

    body.dark .swal2-icon.swal2-question {
      border-color: #6fc9d6 !important;
      color: #6fc9d6 !important;
    }

    body.dark .swal2-confirm,
    body.dark .swal2-styled.swal2-confirm {
      background: var(--grad) !important;
      color: #ffffff !important;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18) !important;
    }

    body.dark .swal2-cancel,
    body.dark .swal2-styled.swal2-cancel {
      background: #223548 !important;
      color: var(--dark) !important;
      border: 1px solid rgba(125, 232, 208, 0.18) !important;
    }

    body.dark .swal2-actions button:focus {
      box-shadow: 0 0 0 3px rgba(125, 232, 208, 0.16) !important;
    }

    body.dark h1,
    body.dark h2,
    body.dark h3,
    body.dark h4,
    body.dark .brand__title,
    body.dark .nav-title,
    body.dark .page-heading h2,
    body.dark .feature-title,
    body.dark .team-name,
    body.dark .mensagem-titulo,
    body.dark .modal-titulo,
    body.dark .turma-nome,
    body.dark .dv-name,
    body.dark .dv-card-title,
    body.dark .dv-stat-val,
    body.dark .dv-prog-hd,
    body.dark .dv-daynum,
    body.dark .dv-ev-t,
    body.dark .dv-msg-title,
    body.dark .dv-donut-pct,
    body.dark .dv-metric-nm,
    body.dark .dv-metric-vl,
    body.dark .dv-col-val,
    body.dark .row-nome-label,
    body.dark .aluno-resumo-valor,
    body.dark .aluno-materia-nome,
    body.dark .nota-bloco-valor,
    body.dark .coord-card-titulo,
    body.dark .coord-aluno-nome {
      color: var(--dark) !important;
    }

    body.dark .feature-desc,
    body.dark .section-desc,
    body.dark .mensagem-descricao,
    body.dark .modal-body,
    body.dark .page-heading p,
    body.dark .report-card p,
    body.dark .perfil-field span,
    body.dark .perfil-section-label,
    body.dark .campo-grupo label,
    body.dark .filtro-group label,
    body.dark .aluno-resumo-label,
    body.dark .aluno-materia-prof,
    body.dark .nota-bloco-label,
    body.dark .coord-card-subtitulo,
    body.dark .coord-num,
    body.dark .coord-rodape,
    body.dark .coord-vazio,
    body.dark .dv-card-link,
    body.dark .dv-sub,
    body.dark .dv-stat-lbl,
    body.dark .dv-donut-sub2,
    body.dark .dv-donut-meta,
    body.dark .dv-prog-sub,
    body.dark .dv-dayname,
    body.dark .dv-ev-h,
    body.dark .dv-msg-meta,
    body.dark .dv-col-lbl,
    body.dark .dv-empty,
    body.dark .dv-ag-empty {
      color: var(--muted) !important;
    }

    body.dark .dv-card-link:hover,
    body.dark .user-text strong {
      color: var(--dark) !important;
    }

    body.dark .login-button,
    body.dark .nav-cta,
    body.dark .btn-primary,
    body.dark .cta-btn,
    body.dark .btn-novo-evento,
    body.dark .btn-enviar,
    body.dark .btn-publicar {
      color: #ffffff !important;
    }
  `;

  function temaSalvo() {
    try {
      return localStorage.getItem(STORAGE_KEY) === "dark";
    } catch (erro) {
      return false;
    }
  }

  function salvarTema(darkAtivo) {
    try {
      localStorage.setItem(STORAGE_KEY, darkAtivo ? "dark" : "light");
    } catch (erro) {
      console.warn("Não foi possível salvar o tema.", erro);
    }
  }

  function garantirEstilos() {
    if (document.getElementById(STYLE_ID)) return;

    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = estilosDark;
    document.head.appendChild(style);
  }

  function removerEstilos() {
    document.getElementById(STYLE_ID)?.remove();
  }

  function atualizarControles(darkAtivo) {
    document.querySelectorAll(TOGGLE_SELECTOR).forEach((botao) => {
      botao.setAttribute("aria-pressed", String(darkAtivo));
      botao.setAttribute("aria-label", darkAtivo ? "Desativar modo escuro" : "Ativar modo escuro");
      botao.title = darkAtivo ? "Desativar modo escuro" : "Ativar modo escuro";
    });

    document.querySelectorAll(ICON_SELECTOR).forEach((icone) => {
      icone.classList.toggle("ph-moon", !darkAtivo);
      icone.classList.toggle("ph-sun", darkAtivo);

      if (icone.hasAttribute("data-theme-icon-text")) {
        icone.textContent = darkAtivo ? "☀️" : "🌙";
      }
    });
  }

  function aplicarTema(darkAtivo) {
    document.body.classList.toggle(DARK_CLASS, darkAtivo);
    document.documentElement.dataset.theme = darkAtivo ? "dark" : "light";
    document.documentElement.style.colorScheme = darkAtivo ? "dark" : "light";

    if (darkAtivo) {
      garantirEstilos();
    } else {
      removerEstilos();
    }

    atualizarControles(darkAtivo);
  }

  function iniciarDarkMode() {
    aplicarTema(temaSalvo());

    document.addEventListener("click", (evento) => {
      if (!(evento.target instanceof Element)) return;

      const botao = evento.target.closest(TOGGLE_SELECTOR);
      if (!botao) return;

      const darkAtivo = !document.body.classList.contains(DARK_CLASS);
      salvarTema(darkAtivo);
      aplicarTema(darkAtivo);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciarDarkMode, { once: true });
  } else {
    iniciarDarkMode();
  }
})();
