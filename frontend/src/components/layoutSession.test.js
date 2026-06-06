import {
  getStoredUser,
  getUserName,
  getUserInitial,
  getRoleInfo,
  isCoordinator,
  isProfessor,
  isStudent,
  formatRole
} from "../layoutSession";

describe("layoutSession", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("retorna nome do usuário", () => {
    expect(getUserName({ nome: "Ana Costa" })).toBe("Ana Costa");
    expect(getUserName({ name: "Maria Souza" })).toBe("Maria Souza");
  });

  it("retorna inicial do usuário", () => {
    expect(getUserInitial({ nome: "Ana Costa" })).toBe("A");
    expect(getUserInitial(null)).toBe("U");
  });

  it("identifica coordenador por texto", () => {
    const user = { papel: "coordenador" };

    expect(isCoordinator(user)).toBe(true);
    expect(formatRole(user)).toBe("Coordenador");
  });

  it("identifica professor por texto", () => {
    const user = { papel: "professor" };

    expect(isProfessor(user)).toBe(true);
    expect(formatRole(user)).toBe("Professor");
  });

  it("identifica aluno por texto", () => {
    const user = { papel: "aluno" };

    expect(isStudent(user)).toBe(true);
    expect(formatRole(user)).toBe("Aluno");
  });

  it("identifica papéis por id", () => {
    expect(isCoordinator({ papel_id: 1 })).toBe(true);
    expect(isProfessor({ papel_id: 2 })).toBe(true);
    expect(isStudent({ papel_id: 3 })).toBe(true);
  });

  it("retorna papel original quando não reconhecido", () => {
    expect(formatRole({ papel: "secretaria" })).toBe("secretaria");
  });

  it("lê usuário salvo no localStorage", () => {
    localStorage.setItem(
      "usuario",
      JSON.stringify({
        nome: "Mirella",
        papel: "aluno"
      })
    );

    const user = getStoredUser();

    expect(user.nome).toBe("Mirella");
    expect(user.papel).toBe("aluno");
  });

  it("retorna null quando usuário salvo está inválido", () => {
    localStorage.setItem("usuario", "{json inválido");

    expect(getStoredUser()).toBeNull();
  });

  it("normaliza texto do papel com acento", () => {
    const info = getRoleInfo({ papel: "Coordenador" });

    expect(info.text).toBe("coordenador");
    expect(info.id).toBe(0);
  });
});