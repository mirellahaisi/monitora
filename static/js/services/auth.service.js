/**
 * auth.service.js
 * Centraliza todas as chamadas de API relacionadas a autenticação e sessão.
 *
 * Incluir em TODAS as páginas protegidas, antes do script da página:
 *   <script src="/static/js/services/auth.service.js"></script>
 */

const AuthService = (() => {

    // ── Sessão (localStorage) ──────────────────────────────────────────────────

    function getToken() {
        return localStorage.getItem("token");
    }

    function getUsuario() {
        try { return JSON.parse(localStorage.getItem("usuario")) || null; }
        catch { return null; }
    }

    function salvarSessao(token, usuario, expiracao) {
        localStorage.setItem("token",            token);
        localStorage.setItem("usuario",          JSON.stringify(usuario));
        localStorage.setItem("sessaoExpiracao",  String(expiracao));
    }

    function limparSessao() {
        localStorage.removeItem("token");
        localStorage.removeItem("usuario");
        localStorage.removeItem("sessaoExpiracao");
    }

    function tokenExpirado() {
        const exp = localStorage.getItem("sessaoExpiracao");
        if (!exp) return true;
        return Number(exp) < Math.floor(Date.now() / 1000);
    }

    function sessaoValida() {
        return !!getToken() && !tokenExpirado();
    }

    /** Redireciona para "/" se não houver sessão válida. Retorna false se redirecionou. */
    function redirecionarSeNaoLogado() {
        if (!sessaoValida()) {
            limparSessao();
            window.location.href = "/";
            return false;
        }
        return true;
    }

    // ── Helpers de header ──────────────────────────────────────────────────────

    function headersAuth() {
        return { "Authorization": `Bearer ${getToken()}` };
    }

    function headersJson() {
        return { "Content-Type": "application/json", "Authorization": `Bearer ${getToken()}` };
    }

    // ── Chamadas de API ────────────────────────────────────────────────────────

    async function login(email, senha) {
        const resp  = await fetch("/api/login", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ email, senha }),
        });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    async function logout() {
        try {
            await fetch("/api/logout", {
                method:  "POST",
                headers: headersAuth(),
            });
        } catch (_) {
            // ignora falhas de rede no logout
        } finally {
            limparSessao();
        }
    }

    async function getUsuarioLogado() {
        const resp  = await fetch("/api/usuario-logado", { headers: headersAuth() });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    async function getPerfil() {
        const resp  = await fetch("/api/perfil", { headers: headersAuth() });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    async function atualizarPerfil(payload) {
        const resp  = await fetch("/api/perfil", {
            method:  "PUT",
            headers: headersJson(),
            body:    JSON.stringify(payload),
        });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    // ── API pública ────────────────────────────────────────────────────────────

    return {
        // sessão
        getToken,
        getUsuario,
        salvarSessao,
        limparSessao,
        sessaoValida,
        redirecionarSeNaoLogado,
        // helpers reutilizáveis pelos outros services
        headersAuth,
        headersJson,
        // API
        login,
        logout,
        getUsuarioLogado,
        getPerfil,
        atualizarPerfil,
    };

})();
