// ESLint flat config for the NYC Buildability web app.
//
// Replaces the former `eslint-config-next` (next/core-web-vitals + next/typescript,
// loaded through @eslint/eslintrc FlatCompat). `eslint-config-next` was removed to
// drop the dev-only advisory chain
//   eslint-config-next -> @next/eslint-plugin-next -> fast-glob 3.3.1
//   -> micromatch 4.0.8 -> braces 3.0.3   (GHSA-vfj7-8cjw-p6xm, high, NO patch).
// Every 15.x/16.x @next/eslint-plugin-next pins fast-glob 3.3.1 and the 14.2.35
// downgrade carries glob 10.3.10 (GHSA-5j98-mcp5-4vw2), so neither an upgrade nor a
// downgrade is admissible — the config itself had to be replaced.
//
// The full old->new rule-set mapping, the Next-specific rules intentionally lost,
// and the registry/age/advisory evidence for every admitted package are recorded in
// project-control/reports/M0-T180-producer-report.md and -registry-research.md.
//
// Admitted rule sets (each exact-pinned, registry-verified, advisory-free, >= 7 days):
//   @eslint/js recommended        9.39.5   core JS correctness rules
//   typescript-eslint recommended 8.70.1   TS correctness rules (scoped to TS files)
//   eslint-plugin-react-hooks     7.1.1    rules-of-hooks (error) + exhaustive-deps (warn)
//   globals                       17.12.0  Node/browser globals for plain .mjs tooling files

import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";

export default tseslint.config(
  {
    // Global ignores — unchanged from the previous config (same six entries).
    ignores: [
      "node_modules/**",
      ".next/**",
      "out/**",
      "next-env.d.ts",
      "playwright-report/**",
      "test-results/**",
    ],
  },
  {
    // First-party JavaScript tooling files (this config + scripts/*.mjs).
    // `public/**` holds vendored, minified third-party bundles (maplibre-gl) that
    // are not first-party source and must not be subject to source-code rules. The
    // previous config left them unflagged only because it never enabled
    // eslint:recommended; @eslint/js recommended WOULD flag minified code, so this
    // object scopes them out. This is a per-object scope exclusion, NOT a change to
    // the global `ignores` list above.
    files: ["**/*.{js,mjs,cjs}"],
    ignores: ["public/**"],
    ...js.configs.recommended,
    languageOptions: {
      ecmaVersion: 2024,
      sourceType: "module",
      // Mirror the former `env: { browser: true, node: true }` so core `no-undef`
      // does not fire on Node/browser globals the tooling scripts use.
      globals: { ...globals.node, ...globals.browser },
    },
  },
  {
    // TypeScript / TSX source. typescript-eslint's `base` config sets the TS parser
    // and plugin with NO `files` restriction, so it is scoped here to TS files only;
    // otherwise its parser and rules would also run over the vendored `.mjs` bundles
    // under public/. @eslint/js recommended is applied here too (the official
    // typescript-eslint pattern); typescript-eslint's bundled eslint-recommended
    // compat layer turns off the core rules TypeScript already covers (no-undef,
    // no-redeclare, no-unreachable, core no-unused-vars, ...).
    files: ["**/*.{ts,tsx,mts,cts}"],
    extends: [js.configs.recommended, tseslint.configs.recommended],
    rules: {
      // Preserve the exact severities the former `next/typescript` set (warn, not
      // the recommended preset's error) so code the previous config tolerated as a
      // warning is not newly failed. This mirrors prior behavior; it is not a disable.
      "@typescript-eslint/no-unused-vars": "warn",
      "@typescript-eslint/no-unused-expressions": "warn",
    },
  },
  {
    // React hooks correctness — exactly the two rules the former next/core-web-vitals
    // enforced via react-hooks ^5 recommended. eslint-plugin-react-hooks 7.1.1's
    // `configs.flat.recommended` ALSO bundles experimental React Compiler rules
    // (set-state-in-effect, immutability, purity, refs, use-memo, ... all `error`)
    // that were never active before; enabling them would change program-logic
    // expectations across existing components. Only the two stable rules are enabled,
    // matching both prior behavior and this task's definition of react-hooks recommended.
    files: ["**/*.{ts,tsx,js,jsx}"],
    ignores: ["public/**"],
    plugins: { "react-hooks": reactHooks },
    rules: {
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
    },
  },
);
