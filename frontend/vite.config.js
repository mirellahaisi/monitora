import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  define: {
    "process.env.NODE_ENV": JSON.stringify("production")
  },
  build: {
    outDir: "../static/react/assets",
    emptyOutDir: true,
    sourcemap: false,
    lib: {
      entry: "src/main.jsx",
      name: "MonitoraLayoutReact",
      formats: ["iife"],
      fileName: () => "main.js"
    },
    rollupOptions: {
      output: {
        inlineDynamicImports: true
      }
    }
  }
});
