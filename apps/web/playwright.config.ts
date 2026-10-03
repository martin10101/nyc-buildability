import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright human-journey configuration (task M2-T001, scenarios S1–S8).
 *
 * Three real servers are started:
 *  1. The RECORDED-OFFICIAL-FIXTURE API harness (e2e/harness/fixture_api.py)
 *     — the real FastAPI app over committed official PLUTO captures via the
 *     accepted fetcher-dependency seam. NOT a frontend mock.
 *  2. The production Next.js build (`next start` on :3000; `next build` must run
 *     first — CI does this in the web-e2e job). Flag-off; the `chromium` project.
 *  3. A second `next start` on :3001 with INTERNAL_LOT_SITE_SETUP_ENABLED=1 for the
 *     flag-ON lot-&-site-setup journey (D-1 slice 2), plus the hidden-issues and parity
 *     window UI flags (Lane D D-12 / D-15 slice 2); the `chromium-flag-on` project.
 *     Reuses the one build, so there is no second `next build`.
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
      // Flag-OFF journeys against the default :3000 server. Every spec under e2e/
      // EXCEPT the *.flag-on.spec.ts specs, which need the flag-on :3001 server
      // (below). So the flag-off lot-site-setup spec keeps proving the production
      // default and is unaffected by the flag-on journey.
      name: "chromium",
      testIgnore: /\.flag-on\.spec\.ts$/,
      use: { ...devices["Desktop Chrome"] },
    },
    {
      // D-1 slice 2: the flag-ON lot-&-site-setup journey. Runs ONLY the
      // *.flag-on.spec.ts specs (lane D writes lot-site-setup.flag-on.spec.ts)
      // against the SECOND `next start` on :3001, which sets
      // INTERNAL_LOT_SITE_SETUP_ENABLED=1. A distinct project + baseURL keeps the
      // flag off for every other spec, so turning it on cannot break the flag-off
      // spec. baseURL points this project's page.goto() at the flag-on server.
      name: "chromium-flag-on",
      testMatch: /\.flag-on\.spec\.ts$/,
      use: { ...devices["Desktop Chrome"], baseURL: "http://127.0.0.1:3001" },
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
      // M2-T016: also enable the internal survey-review screens so the
      // human-journey walkthrough (G3) can exercise /survey/review in a real
      // browser. Non-public runtime flag, read server-side, never inlined into
      // the client bundle; unset in production so the route 404s by default.
      env: {
        INTERNAL_RULE_EVAL_ENABLED: "1",
        // D-01 (D-090): the proposal editor is set aside behind this default-off flag;
        // the e2e server turns it on so proposal-editor specs keep exercising it.
        INTERNAL_PROPOSAL_EDITOR_ENABLED: "1",
        INTERNAL_OWNER_DASHBOARD_ENABLED: "1",
        INTERNAL_SURVEY_REVIEW_ENABLED: "1",
        // INTERNAL_LOT_SITE_SETUP_ENABLED is deliberately NOT set here: this :3000
        // server stays flag-OFF so lot-site-setup.spec.ts keeps proving the default.
      },
    },
    {
      // D-1 slice 2: a SECOND `next start` on :3001 for the flag-ON lot-&-site-setup
      // journey. It reuses the one production build (`next build` already ran for the
      // :3000 server — no second build), so the only added CI cost is one more Next
      // server process and its boot. It sets INTERNAL_LOT_SITE_SETUP_ENABLED=1 on top
      // of the same runtime flags as the :3000 server; the chromium-flag-on project
      // (baseURL :3001) is the only one that talks to it. Both Next servers share the
      // one recorded-fixture API harness on :8000.
      command: "npm run start -- -p 3001",
      url: "http://127.0.0.1:3001",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        INTERNAL_RULE_EVAL_ENABLED: "1",
        INTERNAL_PROPOSAL_EDITOR_ENABLED: "1",
        INTERNAL_OWNER_DASHBOARD_ENABLED: "1",
        INTERNAL_SURVEY_REVIEW_ENABLED: "1",
        INTERNAL_LOT_SITE_SETUP_ENABLED: "1",
        // Lane D D-12 / D-15 flag-ON journeys: the hidden-issues and parity windows are
        // behind these two server-read, default-off UI flags (distinct from the API
        // read-route flags INTERNAL_*_READ_ENABLED, which the fixture harness turns on
        // for itself). Set ONLY on this :3001 server; the :3000 server stays flag-OFF so
        // the default (both windows hidden, no fetch) keeps being proven.
        INTERNAL_HIDDEN_ISSUE_FLAGS_UI_ENABLED: "1",
        INTERNAL_PARITY_UI_ENABLED: "1",
      },
    },
  ],
});
