/**
 * frequencia.js
 * Lógica dos selects dinâmicos da página de Frequência.
 *
 * Depende de: nenhum service externo (as rotas são públicas no blueprint)
 * Incluir em: templates/pages/frequencia.html
 */

const selAluno   = document.getElementById("sel-aluno");
const selTurma   = document.getElementById("sel-turma");
const selMateria = document.getElementById("sel-materia");
const btnVis     = document.getElementById("btn-visualizar");

// Valores já selecionados (injetados pelo Jinja via data attributes no HTML)
const alunoAtual   = selAluno.dataset.atual   || "";
const turmaAtual   = selTurma.dataset.atual   || "";
const materiaAtual = selMateria.dataset.atual || "";

// ── Helpers ────────────────────────────────────────────────────────────────────

function resetSelect(sel, placeholder) {
    sel.innerHTML = `<option value="" disabled selected>${placeholder}</option>`;
    sel.disabled = true;
}

// ── Carregamento encadeado ─────────────────────────────────────────────────────

async function carregarTurmas(alunoId, turmaParaSelecionar = "") {
    resetSelect(selTurma, "Selecione o período");
    resetSelect(selMateria, "Selecione a matéria");
    btnVis.disabled = true;

    if (!alunoId) return;

    const resp   = await fetch(`/api/frequencia/turmas?aluno_id=${alunoId}`);
    const turmas = await resp.json();

    turmas.forEach(t => {
        const opt = document.createElement("option");
        opt.value       = t.id;
        opt.textContent = `${t.nome} — ${t.periodo}º Período`;
        if (String(t.id) === turmaParaSelecionar) opt.selected = true;
        selTurma.appendChild(opt);
    });

    selTurma.disabled = turmas.length === 0;

    if (turmaParaSelecionar && selTurma.value) {
        await carregarMaterias(turmaParaSelecionar, materiaAtual);
    }
}

async function carregarMaterias(turmaId, materiaParaSelecionar = "") {
    resetSelect(selMateria, "Selecione a matéria");
    btnVis.disabled = true;

    if (!turmaId) return;

    const resp     = await fetch(`/api/frequencia/materias?turma_id=${turmaId}`);
    const materias = await resp.json();

    materias.forEach(m => {
        const opt = document.createElement("option");
        opt.value       = m.id;
        opt.textContent = m.nome;
        if (String(m.id) === materiaParaSelecionar) opt.selected = true;
        selMateria.appendChild(opt);
    });

    selMateria.disabled = materias.length === 0;

    if (selMateria.value) btnVis.disabled = false;
}

// ── Eventos ────────────────────────────────────────────────────────────────────

selAluno.addEventListener("change",   () => carregarTurmas(selAluno.value));
selTurma.addEventListener("change",   () => carregarMaterias(selTurma.value));
selMateria.addEventListener("change", () => { btnVis.disabled = !selMateria.value; });

// ── Restaurar estado após submit do formulário ─────────────────────────────────

if (alunoAtual) {
    carregarTurmas(alunoAtual, turmaAtual);
}
