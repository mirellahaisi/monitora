const passwordInput = document.querySelector("#password");
const togglePasswordButton = document.querySelector("[data-toggle-password]");
const loginForm = document.querySelector(".login-form");
const loginButton = document.querySelector(".login-button");

function decodeJwtPayload(token) {
  try {
    const payload = token.split(".")[1];
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const decoded = atob(normalized);
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

function showMessage(options) {
  if (window.Swal && typeof window.Swal.fire === "function") {
    return window.Swal.fire(options);
  }

  const title = options.title ? `${options.title}\n\n` : "";
  window.alert(`${title}${options.text || ""}`);
  return Promise.resolve();
}

if (togglePasswordButton && passwordInput) {
  togglePasswordButton.addEventListener("click", () => {
    const showingPassword = passwordInput.type === "text";
    passwordInput.type = showingPassword ? "password" : "text";
    togglePasswordButton.setAttribute("aria-pressed", String(!showingPassword));
    togglePasswordButton.setAttribute(
      "aria-label",
      showingPassword ? "Mostrar senha" : "Ocultar senha"
    );
  });
}

if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(loginForm);
    const matricula = String(formData.get("matricula") || "").trim();
    const senha = String(formData.get("senha") || "").trim();

    if (!matricula || !senha) {
      showMessage({
        icon: "warning",
        title: "Campos obrigatórios",
        text: "Preencha matrícula e senha para continuar.",
        confirmButtonColor: "#4caebe"
      });
      return;
    }

    if (loginButton) {
      loginButton.disabled = true;
    }

    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ matricula, senha })
      });

      const raw = await response.text();
      const data = raw ? JSON.parse(raw) : {};

      if (!response.ok) {
        throw new Error(data.message || "Não foi possível autenticar.");
      }

      localStorage.setItem("monitoraToken", data.token);
      localStorage.setItem("token", data.token);
      localStorage.setItem("monitoraUsuario", JSON.stringify(data.usuario));

      loginForm.reset();

      const tokenPayload = decodeJwtPayload(data.token);

      console.log("JWT recebido:", data.token);
      console.log("Payload do JWT:", tokenPayload);
      console.log("Usuário autenticado:", data.usuario);
      window.monitoraAuth = {
        token: data.token,
        payload: tokenPayload,
        usuario: data.usuario
      };

      await showMessage({
        icon: "success",
        title: "Login realizado",
        text: data.message,
        confirmButtonColor: "#4caebe"
      });
    } catch (error) {
      localStorage.removeItem("monitoraToken");
      localStorage.removeItem("token");
      localStorage.removeItem("monitoraUsuario");

      console.error("Erro de autenticação:", error);

      showMessage({
        icon: "error",
        title: "Acesso negado",
        text: error.message || "Erro inesperado ao autenticar.",
        confirmButtonColor: "#4caebe"
      });
    } finally {
      if (loginButton) {
        loginButton.disabled = false;
      }
    }
  });
}
