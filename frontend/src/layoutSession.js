function decodeJwtPayload(token) {
  try {
    const part = token.split(".")[1];
    if (!part) return null;

    const base64 = part.replace(/-/g, "+").replace(/_/g, "/");
    const padding = "=".repeat((4 - (base64.length % 4)) % 4);
    return JSON.parse(window.atob(base64 + padding));
  } catch (error) {
    return null;
  }
}

function readJsonStorage(key) {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch (error) {
    return null;
  }
}

function normalizeText(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();
}

export function getStoredUser() {
  try {
    const tokenPayload = decodeJwtPayload(window.localStorage.getItem("token") || "");
    const storedUser = readJsonStorage("usuario");
    return tokenPayload || storedUser ? { ...(tokenPayload || {}), ...(storedUser || {}) } : null;
  } catch (error) {
    return null;
  }
}

export function getUserName(user) {
  return String(user?.nome || user?.name || "").trim();
}

export function getUserInitial(user) {
  const name = getUserName(user);
  return name ? name.charAt(0).toUpperCase() : "U";
}

export function getRoleInfo(user) {
  const rawRole = user?.papel;
  const numericRole = Number(rawRole);
  const roleId = Number(user?.papel_id || user?.fk_papel_id || (Number.isFinite(numericRole) ? numericRole : ""));

  return {
    text: normalizeText(rawRole),
    id: Number.isFinite(roleId) ? roleId : 0
  };
}

export function isCoordinator(user) {
  const role = getRoleInfo(user);
  return ["admin", "adm", "coordenador"].includes(role.text) || role.id === 1;
}

export function isProfessor(user) {
  const role = getRoleInfo(user);
  return role.text === "professor" || role.id === 2;
}

export function isStudent(user) {
  const role = getRoleInfo(user);
  return role.text === "aluno" || role.id === 3;
}

export function formatRole(user) {
  if (!user) return "";
  if (isCoordinator(user)) return "Coordenador";
  if (isProfessor(user)) return "Professor";
  if (isStudent(user)) return "Aluno";
  return String(user.papel || "");
}
