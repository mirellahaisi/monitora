import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => ({
  plugins: [react()],

  define: {
    "process.env.NODE_ENV": JSON.stringify(mode === "test" ? "test" : "production")
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
  },

  test: {
    globals: true,
    environment: "happy-dom",
    setupFiles: "./src/setupTests.js",
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      include: ["src/**/*.{js,jsx}"],
      exclude: ["src/main.jsx"]
    }
  }
}));