import { getStoredUser, isCoordinator, isProfessor, isStudent } from "../layoutSession.js";

function IconHome() {
  return (
    <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  );
}

function IconMonitor() {
  return (
    <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="2" y="3" width="20" height="14" rx="2" />
      <line x1="8" y1="21" x2="16" y2="21" />
      <line x1="12" y1="17" x2="12" y2="21" />
    </svg>
  );
}

function IconDocument() {
  return (
    <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  );
}

function IconUsers() {
  return (
    <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function IconCalendar() {
  return (
    <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  );
}

function IconBell() {
  return (
    <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  );
}

function IconCheck() {
  return (
    <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="9 11 12 14 22 4" />
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
    </svg>
  );
}

function IconUserPlus() {
  return (
    <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      <line x1="19" y1="8" x2="19" y2="14" />
      <line x1="22" y1="11" x2="16" y2="11" />
    </svg>
  );
}

function IconLayers() {
  return (
    <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 3L2 9l10 6 10-6-10-6z" />
      <path d="M2 17l10 6 10-6" />
      <path d="M2 13l10 6 10-6" />
    </svg>
  );
}

function IconPulse() {
  return (
    <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  );
}

function IconLogout() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  );
}

function LaptopArt() {
  return (
    <svg viewBox="0 0 80 60" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="10" y="6" width="60" height="38" rx="4" fill="rgba(255,255,255,0.25)" stroke="rgba(255,255,255,0.6)" strokeWidth="2" />
      <rect x="15" y="11" width="50" height="28" rx="2" fill="rgba(30,80,100,0.35)" />
      <rect x="4" y="47" width="72" height="6" rx="3" fill="rgba(255,255,255,0.35)" stroke="rgba(255,255,255,0.5)" strokeWidth="1.5" />
      <rect x="30" y="44" width="20" height="3" rx="1.5" fill="rgba(255,255,255,0.2)" />
    </svg>
  );
}

function SidebarLink({ activePage, page, href, id, children, icon }) {
  const active = activePage === page;

  return (
    <a href={href} id={id} className={`sidebar-link${active ? " active" : ""}`}>
      {icon}
      {children}
    </a>
  );
}

export default function Sidebar({ activePage = "" }) {
  const user = getStoredUser();
  const student = isStudent(user);
  const professor = isProfessor(user);
  const coordinator = isCoordinator(user);

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <img src="/static/images/logomonitora.png" alt="Logo Monitora+" className="sidebar-logo" />
        <h1>
          Monitora<span>+</span>
        </h1>
      </div>

      <nav className="sidebar-menu">
        <SidebarLink activePage={activePage} page="inicio" href="/inicio" icon={<IconHome />}>
          {"Página Inicial"}
        </SidebarLink>

        <SidebarLink activePage={activePage} page="turmas" href="/turmas" id="linkTurmas" icon={<IconMonitor />}>
          <span id="labelLinkTurmas">{student ? "Minha Turma" : "Turmas"}</span>
        </SidebarLink>

        <SidebarLink activePage={activePage} page="notas" href="/notas" icon={<IconDocument />}>
          Notas
        </SidebarLink>

        {professor && (
          <SidebarLink activePage={activePage} page="presenca" href="/presenca" id="linkPresenca" icon={<IconUsers />}>
            {"Presença"}
          </SidebarLink>
        )}

        <SidebarLink activePage={activePage} page="calendario" href="/calendario" icon={<IconCalendar />}>
          {"Calendário"}
        </SidebarLink>

        <SidebarLink activePage={activePage} page="mensagens" href="/mensagens" icon={<IconBell />}>
          Mensagens
        </SidebarLink>

        <SidebarLink activePage={activePage} page="frequencia" href="/frequencia" icon={<IconCheck />}>
          {"Frequência"}
        </SidebarLink>

        {coordinator && (
          <>
            <SidebarLink activePage={activePage} page="gestao_usuarios" href="/gestao-usuarios" id="linkGestaoUsuarios" icon={<IconUserPlus />}>
              {"Gestão de Usuários"}
            </SidebarLink>

            <SidebarLink activePage={activePage} page="cursos" href="/cursos" id="linkCursos" icon={<IconLayers />}>
              Cursos
            </SidebarLink>

            <SidebarLink activePage={activePage} page="materias" href="/materias" id="linkMaterias" icon={<IconDocument />}>
              {"Matérias"}
            </SidebarLink>
          </>
        )}

        <SidebarLink activePage={activePage} page="desempenho" href="#" icon={<IconPulse />}>
          Desempenho
        </SidebarLink>
      </nav>

      <div className="sidebar-bottom">
        <div className="sidebar-laptop">
          <LaptopArt />
        </div>

        <button className="logout-button" id="btnSair" type="button">
          <IconLogout />
          Sair
        </button>
      </div>
    </aside>
  );
}
