import { render, screen, fireEvent } from "@testing-library/react";
import Sidebar from "./Sidebar";

describe("Sidebar", () => {
  beforeEach(() => {
    localStorage.clear();
    document.body.className = "";
    window.confirm = vi.fn(() => true);
    global.fetch = vi.fn(() => Promise.resolve({ ok: true }));
  });

  it("renderiza links básicos do menu", () => {
    localStorage.setItem(
      "usuario",
      JSON.stringify({
        nome: "Ana Costa",
        papel: "aluno"
      })
    );

    render(<Sidebar activePage="notas" />);

    expect(screen.getByText("Página Inicial")).toBeInTheDocument();
    expect(screen.getByText("Minha Turma")).toBeInTheDocument();
    expect(screen.getByText("Notas")).toBeInTheDocument();
    expect(screen.getByText("Calendário")).toBeInTheDocument();
    expect(screen.getByText("Mensagens")).toBeInTheDocument();
    expect(screen.getByText("Frequência")).toBeInTheDocument();
  });

  it("mostra Presença para professor", () => {
    localStorage.setItem(
      "usuario",
      JSON.stringify({
        nome: "Professor João",
        papel: "professor"
      })
    );

    render(<Sidebar />);

    expect(screen.getByText("Presença")).toBeInTheDocument();
    expect(screen.getByText("Turmas")).toBeInTheDocument();
  });

  it("mostra gestão, cursos e matérias para coordenador", () => {
    localStorage.setItem(
      "usuario",
      JSON.stringify({
        nome: "Coordenação",
        papel: "coordenador"
      })
    );

    render(<Sidebar />);

    expect(screen.getByText("Gestão de Usuários")).toBeInTheDocument();
    expect(screen.getByText("Cursos")).toBeInTheDocument();
    expect(screen.getByText("Matérias")).toBeInTheDocument();
  });

  it("alterna o menu entre expandido e minimizado", () => {
    render(<Sidebar />);

    const botao = screen.getByRole("button", { name: /minimizar menu/i });

    fireEvent.click(botao);

    expect(document.body).toHaveClass("sidebar-collapsed");
    expect(localStorage.getItem("sidebarCollapsed")).toBe("1");
  });

  it("faz logout limpando a sessão", async () => {
    localStorage.setItem("token", "abc123");
    localStorage.setItem("usuario", JSON.stringify({ nome: "Ana" }));
    localStorage.setItem("sessaoExpiracao", "123");

    render(<Sidebar />);

    fireEvent.click(screen.getByRole("button", { name: /sair/i }));

    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(localStorage.getItem("token")).toBeNull();
    expect(localStorage.getItem("usuario")).toBeNull();
    expect(localStorage.getItem("sessaoExpiracao")).toBeNull();
  });
});