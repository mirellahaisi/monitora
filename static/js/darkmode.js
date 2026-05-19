(function () {
  const btn = document.getElementById("btnDarkMode");
  const icone = document.getElementById("iconeDarkMode");

  // Aplica o tema salvo ao carregar a página
  if (localStorage.getItem("tema") === "dark") {
    document.body.classList.add("dark");
    if (icone) {
      icone.classList.remove("ph-moon");
      icone.classList.add("ph-sun");
    }
  }

  if (btn) {
    btn.addEventListener("click", function () {
      document.body.classList.toggle("dark");

      const darkAtivo = document.body.classList.contains("dark");
      localStorage.setItem("tema", darkAtivo ? "dark" : "light");

      if (icone) {
        icone.classList.toggle("ph-moon", !darkAtivo);
        icone.classList.toggle("ph-sun", darkAtivo);
      }
    });
  }
})();