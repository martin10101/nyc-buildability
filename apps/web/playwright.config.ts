import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright human-journey configuration (task M2-T001, scenarios S1–S8).
 *
 * Two real servers are started:
 *  1. The RECORDED-OFFICIAL-FIXTURE API harness (e2e/harness/fixture_api.py)
 *     — the real FastAPI app over committed official PLUTO captures via the
 *     accepted fetcher-dependency seam. NOT a frontend mock.
 *  2. The production Next.js build (`next start`; `next build` must run
 *     first — CI does this in the web-e2e job).
 *
 * Runs in CI only; the owner's PC never installs browsers or node_modules
 * (docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md).
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "on",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: [
    {
      command: "python e2e/harness/fixture_api.py",
      url: "http://127.0.0.1:8000/api/v1/health",
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
    {
      command: "npm run start",
      url: "http://127.0.0.1:3000",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      // M4-T005: enable the FRONTEND rule-evaluation flag for this test server.
      // The variable is non-public (never inlined into the client bundle) and
      // is read at RUNTIME by the Server Component, so `next start` picks it up
      // here without needing a rebuild. The surface still renders ONLY on
      // requests that also opt in with `?ruleeval=on`, so unrelated journeys are
      // unaffected and the no-call spec (no opt-in) proves the browser is silent.
      // M0-T022: also enable the internal owner dashboard for this test server so
      // the human-journey walkthrough (G4) can exercise /dashboard in a real
      // browser. Non-public runtime flag, read server-side, never inlined into the
      // client bundle; unset in production so the route 404s by default.
      env: { INTERNAL_RULE_EVAL_UI: "1", INTERNAL_OWNER_DASHBOARD_ENABLED: "1" },
    },
  ],
});
