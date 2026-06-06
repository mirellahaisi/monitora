import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";

const mountedRoots = new WeakMap();

function mountLayout() {
  document.querySelectorAll("[data-react-layout]").forEach((element) => {
    if (mountedRoots.has(element)) return;

    const root = createRoot(element);
    mountedRoots.set(element, root);

    root.render(
      <App
        type={element.dataset.reactLayout || ""}
        activePage={element.dataset.activePage || ""}
      />
    );
  });
}

mountLayout();

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", mountLayout, { once: true });
}

window.MonitoraLayoutReact = {
  mount: mountLayout
};
