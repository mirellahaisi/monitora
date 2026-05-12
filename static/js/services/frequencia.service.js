/**
 * frequencia.service.js
 * Centraliza todas as chamadas de API relacionadas à frequência.
 *
 * Depende de: auth.service.js (deve ser incluído antes)
 * Incluir em: templates/pages/frequencia.html (se precisar de rotas autenticadas)
 *
 * Nota: as rotas /api/frequencia/turmas e /api/frequencia/materias atualmente
 * não exigem token, mas o service já os envia por consistência e segurança futura.
 */

const FrequenciaService = (() => {

    async function listarTurmasPorAluno(alunoId) {
        const resp  = await fetch(`/api/frequencia/turmas?aluno_id=${alunoId}`, { headers: AuthService.headersAuth() });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    async function listarMateriasPorTurma(turmaId) {
        const resp  = await fetch(`/api/frequencia/materias?turma_id=${turmaId}`, { headers: AuthService.headersAuth() });
        const dados = await resp.json();
        return { ok: resp.ok, dados };
    }

    return {
        listarTurmasPorAluno,
        listarMateriasPorTurma,
    };

})();
