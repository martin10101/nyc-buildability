import { fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

/**
 * Unit/component test runner (task M2-T001). Vitest was chosen over Jest
 * for Next 15 / React 19 compatibility with a minimal dependency tree (no
 * Babel chain; esbuild-native TypeScript). Runs in CI only — the owner's
 * PC never installs node_modules (docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md).
 */
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    include: ["src/**/*.test.{ts,tsx}"],
  },
});
