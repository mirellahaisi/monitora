(function () {
  const btn = document.getElementById("btnDarkMode");
  const icone = document.getElementById("iconeDarkMode");

  const estilosDinamicos = document.createElement("style");
  estilosDinamicos.id = "dark-mode-dinamico";
  estilosDinamicos.textContent = `
    #tabelaNotas tr, #tabelaPresenca tr {
      background: #162535 !important;
    }
    #tabelaNotas td, #tabelaPresenca td {
      background: #162535 !important;
      color: #c8dde8 !important;
      border-color: #1a2f40 !important;
    }
    .nota-input {
      background: #1a2f40 !important;
      color: #c8dde8 !important;
      border-color: #1e3448 !important;
    }
    body.dark .notas-card,
    body.dark .notas-table,
    body.dark .notas-table tbody,
    body.dark .notas-table tbody tr,
    body.dark .notas-table tbody td {
      background: #162535 !important;
    }
    body.dark .notas-table thead,
    body.dark .notas-table thead tr,
    body.dark .notas-table thead th {
      background: #1a3a50 !important;
      border-color: #1e3448 !important;
      color: #7de8d0 !important;
    }
    body.dark .notas-table {
      border-color: #1e3448 !important;
    }
    body.dark .presenca-card,
    body.dark .presenca-table,
    body.dark .presenca-table tbody,
    body.dark .presenca-table tbody tr,
    body.dark .presenca-table tbody td {
      background: #162535 !important;
      color: #c8dde8 !important;
      border-color: #1a2f40 !important;
    }
    body.dark .presenca-table thead,
    body.dark .presenca-table thead tr,
    body.dark .presenca-table thead th {
      background: #1a3a50 !important;
      border-color: #1e3448 !important;
      color: #7de8d0 !important;
    }
    body.dark .observacao-presenca {
      background: #162535 !important;
      color: #c8dde8 !important;
      border-color: #1e3448 !important;
    }
    body.dark .presenca-filtros {
      background: #162535 !important;
      border-color: #1e3448 !important;
    }
    body.dark .presenca-filtros select,
    body.dark .presenca-filtros input[type="date"] {
      background: #1a2f40 !important;
      color: #c8dde8 !important;
      border-color: #1e3448 !important;
    }
  `;

  function aplicarTema(dark) {
    if (dark) {
      document.body.classList.add("dark");
      document.head.appendChild(estilosDinamicos);
      if (icone) {
        icone.classList.remove("ph-moon");
        icone.classList.add("ph-sun");
      }
    } else {
      document.body.classList.remove("dark");
      const existente = document.getElementById("dark-mode-dinamico");
      if (existente) existente.remove();
      if (icone) {
        icone.classList.remove("ph-sun");
        icone.classList.add("ph-moon");
      }
    }
  }

  aplicarTema(localStorage.getItem("tema") === "dark");

  if (btn) {
    btn.addEventListener("click", function () {
      const darkAtivo = !document.body.classList.contains("dark");
      localStorage.setItem("tema", darkAtivo ? "dark" : "light");
      aplicarTema(darkAtivo);
    });
  }

})();