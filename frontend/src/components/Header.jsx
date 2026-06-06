import { useEffect } from "react";
import { formatRole, getStoredUser, getUserInitial, getUserName } from "../layoutSession.js";

export default function Header() {
  const user = getStoredUser();
  const name = getUserName(user);
  const role = formatRole(user);

  useEffect(() => {
    const button = document.getElementById("botaoMenuUsuario");
    const menu = document.getElementById("menuUsuario");
    const editButton = document.getElementById("btnEditarPerfil");

    if (!button || !menu) return undefined;

    const toggleMenu = (event) => {
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation?.();
      menu.classList.toggle("show");
    };

    const closeMenu = (event) => {
      if (!(event.target instanceof Element)) return;
      if (!event.target.closest(".user-menu")) menu.classList.remove("show");
    };

    const editProfile = (event) => {
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation?.();
      menu.classList.remove("show");
      window.location.href = "/perfil";
    };

    button.addEventListener("click", toggleMenu, true);
    document.addEventListener("click", closeMenu, true);
    editButton?.addEventListener("click", editProfile, true);

    return () => {
      button.removeEventListener("click", toggleMenu, true);
      document.removeEventListener("click", closeMenu, true);
      editButton?.removeEventListener("click", editProfile, true);
    };
  }, []);

  return (
    <header className="inicio-header">
      <button
        className="btn-dark-mode nav-theme-toggle"
        id="btnDarkMode"
        type="button"
        title="Alternar tema"
        aria-label="Ativar modo escuro"
        aria-pressed="false"
      >
        <span id="iconeDarkMode" data-theme-icon-text aria-hidden="true">
          &#127769;
        </span>
      </button>

      <div className="user-menu">
        <button className="user-menu-button" id="botaoMenuUsuario" type="button">
          <div className="user-avatar" id="avatarUsuario">
            {getUserInitial(user)}
          </div>
          <div className="user-text">
            <span id="papelUsuario">{role}</span>
            <strong id="nomeUsuarioTopo">{name}</strong>
          </div>
          <span className="user-arrow">&#9662;</span>
        </button>

        <div className="user-dropdown" id="menuUsuario">
          <button type="button" id="btnEditarPerfil">
            Editar perfil
          </button>
        </div>
      </div>
    </header>
  );
}
