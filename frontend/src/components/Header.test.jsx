import { render, screen, fireEvent } from "@testing-library/react";
import Header from "./Header";

describe("Header", () => {
  beforeEach(() => {
    localStorage.clear();
    window.history.pushState({}, "", "/");
  });

  it("renderiza nome, papel e inicial do usuário", () => {
    localStorage.setItem(
      "usuario",
      JSON.stringify({
        nome: "Marina Silva",
        papel: "professor"
      })
    );

    render(<Header />);

    expect(screen.getByText("Marina Silva")).toBeInTheDocument();
    expect(screen.getByText("Professor")).toBeInTheDocument();
    expect(screen.getByText("M")).toBeInTheDocument();
  });

  it("abre o menu do usuário ao clicar", () => {
    render(<Header />);

    const botao = document.getElementById("botaoMenuUsuario");
    fireEvent.click(botao);

    expect(document.getElementById("menuUsuario")).toHaveClass("show");
    });

  it("redireciona para perfil ao clicar em editar perfil", () => {
    render(<Header />);

    fireEvent.click(document.getElementById("botaoMenuUsuario"));
    fireEvent.click(screen.getByText("Editar perfil"));

    expect(window.location.pathname).toBe("/perfil");
  });
});