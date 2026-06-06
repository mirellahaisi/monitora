import Header from "./components/Header.jsx";
import Sidebar from "./components/Sidebar.jsx";

export default function App({ type, activePage }) {
  if (type === "header") return <Header />;
  if (type === "sidebar") return <Sidebar activePage={activePage} />;
  return null;
}
