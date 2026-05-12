/**
 * notas.service.js
 * Centraliza todas as chamadas de API relacionadas ao lançamento de notas.
 *
 * Depende de: auth.service.js (deve ser incluído antes)
 * Incluir em: templates/pages/notas.html
 */

const NotasService = (() => {

    // ── Selects dinâmicos ──────────────────────────────────────────────────────

    async function listarMaterias() {
        const resp  = await fetch("/api/notas/materias", { headers: AuthService.headersAuth() });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    async function listarTurmasPorMateria(materiaId) {
        const resp  = await fetch(`/api/notas/turmas?materia_id=${materiaId}`, { headers: AuthService.headersAuth() });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    async function listarAlunosDaTurma(materiaId, turmaId) {
        const resp  = await fetch(`/api/notas/alunos?materia_id=${materiaId}&turma_id=${turmaId}`, { headers: AuthService.headersAuth() });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    // ── Persistência ───────────────────────────────────────────────────────────

    async function salvarNotas(materiaId, turmaId, alunos) {
        const resp  = await fetch("/api/notas/salvar", {
            method:  "POST",
            headers: AuthService.headersJson(),
            body:    JSON.stringify({ materia_id: materiaId, turma_id: turmaId, alunos }),
        });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    // ── API pública ────────────────────────────────────────────────────────────

    return {
        listarMaterias,
        listarTurmasPorMateria,
        listarAlunosDaTurma,
        salvarNotas,
    };

})();
