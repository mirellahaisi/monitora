/**
 * usuarios.service.js
 * Centraliza todas as chamadas de API relacionadas à gestão de usuários.
 *
 * Depende de: auth.service.js (deve ser incluído antes)
 * Incluir em: templates/pages/gestao_usuarios.html
 */

const UsuariosService = (() => {

    // ── Listagem ───────────────────────────────────────────────────────────────

    async function listarAlunos() {
        const resp  = await fetch("/api/usuarios/alunos", { headers: AuthService.headersAuth() });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    async function listarProfessores() {
        const resp  = await fetch("/api/usuarios/professores", { headers: AuthService.headersAuth() });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    async function listarCoordenacao() {
        const resp  = await fetch("/api/usuarios/coordenacao", { headers: AuthService.headersAuth() });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    async function buscarUsuario(id) {
        const resp  = await fetch(`/api/usuarios/${id}`, { headers: AuthService.headersAuth() });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    // ── Criação ────────────────────────────────────────────────────────────────

    async function criarAluno(payload) {
        const resp  = await fetch("/api/usuarios/alunos", {
            method:  "POST",
            headers: AuthService.headersJson(),
            body:    JSON.stringify(payload),
        });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    async function criarProfessor(payload) {
        const resp  = await fetch("/api/usuarios/professores", {
            method:  "POST",
            headers: AuthService.headersJson(),
            body:    JSON.stringify(payload),
        });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    async function criarCoordenador(payload) {
        const resp  = await fetch("/api/usuarios/coordenacao", {
            method:  "POST",
            headers: AuthService.headersJson(),
            body:    JSON.stringify(payload),
        });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    // ── Atualização / Remoção ──────────────────────────────────────────────────

    async function atualizarUsuario(id, payload) {
        const resp  = await fetch(`/api/usuarios/${id}`, {
            method:  "PUT",
            headers: AuthService.headersJson(),
            body:    JSON.stringify(payload),
        });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    async function deletarUsuario(id) {
        const resp  = await fetch(`/api/usuarios/${id}`, {
            method:  "DELETE",
            headers: AuthService.headersAuth(),
        });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    // ── API pública ────────────────────────────────────────────────────────────

    return {
        listarAlunos,
        listarProfessores,
        listarCoordenacao,
        buscarUsuario,
        criarAluno,
        criarProfessor,
        criarCoordenador,
        atualizarUsuario,
        deletarUsuario,
    };

})();
