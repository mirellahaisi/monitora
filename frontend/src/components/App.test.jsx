import { render, screen } from "@testing-library/react";
import App from "../App";

describe("App", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renderiza Header quando type é header", () => {
    localStorage.setItem(
      "usuario",
      JSON.stringify({
        nome: "Marina Silva",
        papel: "professor"
      })
    );

    render(<App type="header" />);

    expect(screen.getByText("Marina Silva")).toBeInTheDocument();
  });

  it("renderiza Sidebar quando type é sidebar", () => {
    render(<App type="sidebar" activePage="notas" />);

    expect(screen.getByText("Notas")).toBeInTheDocument();
  });

  it("não renderiza nada quando type é inválido", () => {
    const { container } = render(<App type="invalido" />);

    expect(container).toBeEmptyDOMElement();
  });
});