import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
export default defineConfig({
  base: "/igfb/",
  plugins: [react(), tailwindcss()],
  define: { __BUILD_TIME__: JSON.stringify(new Date().toISOString()) },
  build: { target: "es2022", sourcemap: false },
  test: {
    environment: "jsdom",
    include: ["src/**/*.test.{ts,tsx}"],
    setupFiles: ["./src/test-setup.ts"],
  },
});
