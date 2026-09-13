# G5 SECURITY/PRIVACY GATE REPORT — M5-T024

> Preservation note: saved VERBATIM by the orchestrator from the reviewer's agent-return channel
> (transport entity-decoding only). Reviewer: independent security-reviewer agent.

**Task:** M5-T024 — "D-043 internal web deploy: owner-executed Render service settings + env-var checklist"
**Reviewed content identity:** material commit `0002ddb7`; verified `git diff 0002ddb7..HEAD --stat` = only control-plane lifecycle files (`project-control/state.json`, `project-control/tasks/M5-T024.json`) — deliverable content is byte-identical to the frozen SHA.
**Reviewer:** independent G5 (security/privacy), read-only. Producer was cloud-architect.
**Gate:** G5

## VERDICT: PASS (one ADVISORY, non-blocking; zero BLOCKING corrections)

The deliverable is a docs-only checklist (`docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md`) plus producer report and orchestrator-assembled evidence map. I re-derived every security/privacy requirement from source rather than trusting the producer's conclusions. All six scope items pass.

---

## Per-item findings (each personally verified)

### 1. Secret/URL leakage (D-043-R002, gate-fatal) — PASS
- I ran my own greps over all three files. The ONLY URL literal in the checklist is `http://127.0.0.1` (`docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md:127`), the documented local/CI default — verified as the genuine code default at `apps/web/src/lib/api.ts:152-153` (`process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000"`). Producer report and evidence map contain only the same `127.0.0.1` literal (`M5-T024-producer-report.md:41,52`; `M5-T024-evidence-map.json:12`).
- Zero `onrender.com` hosts, zero keys/tokens/JWTs/PEM blocks/bearer values. The one `service-role` hit (checklist:140) is a prohibition ("never a service-role key"), not a value; the `onrender`/`secret` hits in the report/map are the grep transcript and the negative privacy assertions.
- The private API address appears only as `<owner-pastes-private-API-URL>` and the web origin only as `<new-web-service-origin>` (placeholder table checklist:42-46).
- No instruction would cause the owner to leak the URL: §0 placeholder table and §2 step 2 (checklist:135) both say paste "in the dashboard only — never in a repo file, commit, or chat"; §5 ops-log note (checklist:190-191) says record the variable **name + environment (never the value)**. D-043-R002 satisfied.

### 2. Exposure honesty — PASS
- Verified the API has no auth: `services/api/app/main.py:6-11` ("DEPLOYMENT STATUS: INTERNAL/DEV ONLY — authentication is NOT enabled ... must NOT be publicly exposed until the auth/organization layer lands"). Checklist §0 and §6 cite these exact lines.
- The checklist states the exposure plainly: §6 (checklist:200-210) — "the flag is a feature toggle, **not** an access control"; "**Unlisted is not secret** ... it does **not** protect the endpoints from anyone the URL reaches"; "Real access control arrives with the auth layer (blocked on B-001), not with this deploy." It does NOT imply an unlisted URL is an access control — it explicitly denies that.
- Ordering: the exposure-critical step is §5 step 2 (turn the flag on for `nycdf-api`). The core exposure fact is front-loaded in §0 "read first" ("Honest privacy meaning ... API has **no authentication** ... See §6 before turning the internal flag on for the API," checklist:30-33), and §5 step 2 carries an explicit inline "**Read §6 before you set this**" (checklist:186), with §6's own heading "read before §5 step 2." A reasonable owner following the checklist as written is told the real exposure before flipping the API flag.

### 3. CORS correctness as a security surface — PASS
- Verified against `services/api/app/main.py`: `_parse_allowed_origins` (lines 66-82) raises `RuntimeError` on any entry containing `*`; `allow_credentials=True` (line 104); unset/empty → empty list → no cross-origin access (lines 18-19, 74). The checklist §5 step 1 (checklist:169-180) requires exact origins, comma-separated, **no wildcard, no trailing slash**, and states misconfiguration deliberately fails startup/health — matching the code exactly (cites lines 66-82, 18-19, 74).
- The checklist cannot produce an over-broad allowlist and never suggests loosening CORS to debug: §9 step 2 (checklist:250-253) directs the owner to *fix the exact origin match* (scheme/trailing-slash), not to widen the allowlist. Consistent with render.yaml:128-135.

### 4. Secrets-policy consistency — PASS
- render.yaml S1 (lines 16-19): all sensitive vars `sync: false`, dashboard-prompted, no literal secrets in-file. The checklist has every env var entered by the owner in the dashboard — consistent.
- `apps/web/.env.example:6-8` (NEXT_PUBLIC_* compiled into public bundle) → checklist §2 step 2 states build-time inlining and the rebuild-on-change rule.
- `apps/web/.env.example:12-16` and render.yaml:118-119 (service-role key never in frontend) → checklist §2 step 3 (checklist:140): only publishable values, "never a service-role key."
- NEXT_PUBLIC_SUPABASE_* left blank per B-001 → checklist §2 step 3 (checklist:136-140) says "leave blank." Consistent.

### 5. Scope prohibitions (D-043-R004 + standing) — PASS
- No public-launch affordance: "public launch"/"listing"/"marketing"/"indexing" appear only in the negative (checklist:28, 95). No robots/sitemap/SEO/search-engine steps (grep: none as actions).
- No render.yaml change: §8 (checklist:225-238) records the restoration debt + duplicate-service caution as "recorded, NOT done here"; explicitly "render.yaml is read-only for this task." Verified render.yaml is untouched (material commit changed only the two docs files + evidence map).
- No dependency change (docs-only). No PR #241 reference (grep: zero hits). Nothing weakens the internal/dev posture — §0/§6 reinforce it; §7 (Auto Sync = No) + §8 prevent a later silent duplicate-service collision.

### 6. Tier D / Section 20 owner boundary — PASS
- Every dashboard action is owner-performed (§0 preamble checklist:5-9; reinforced per step). No agent touches Render. Credentials/URLs enter only via the dashboard, never chat/repo (§0 placeholder table, §2 step 2, §5 ops-log note). Consistent with D-043-R003 and Section 20.

---

## Directive requirement re-derivation (D-043 ALL)
- **D-043-R001** (internal deploy checklist, unified flag on both services, NEXT_PUBLIC_API_BASE_URL→private API, internal/dev labeling): satisfied — checklist §1–§5, §9; owner live-URL confirmation correctly left as an OWNER return item (owner-side per R003), not agent-claimed.
- **D-043-R002** (privacy preserved): satisfied by construction — see item 1.
- **D-043-R003** (owner-action boundary; credentials never in repo/chat): satisfied — see item 6.
- **D-043-R004** (not a public launch): satisfied — see item 5.

---

## Advisory (non-blocking)
- **A1 — physical ordering of the exposure note.** §6 (honest exposure note) is physically positioned after §5, where the exposure-critical API flag is set. This is mitigated by (a) §0 "read first" front-loading the no-auth exposure with a forward pointer to §6, and (b) an explicit inline "Read §6 before you set this" at §5 step 2. For strict linear-reader safety, consider relocating/renumbering the exposure note to precede the API flag step (e.g. as §4.5 or an inline block within §5 step 2). Not blocking — the content is present and the forward-references are explicit and unambiguous.

## Notes (informational, not defects)
- The producer correctly flagged that `docs/DEPLOYMENT_AND_ROLLBACK.md` has no "§0.1" at the base SHA and cited the real §1.3 ("Env var changes are deploys," verified at `docs/DEPLOYMENT_AND_ROLLBACK.md:40`) instead of guessing. Good discipline.
- `project-control/reports/M5-T024-evidence-map.json` is not in the task's `allowed_paths` but is orchestrator-assembled (`assembled_by: orchestrator`); this is not a producer scope violation and it is clean of secrets.
- Modularity: N/A — docs-only change (two files). No handwritten production source altered.

## Reproduction commands used
- `git -C <repo> diff 0002ddb7..HEAD --stat` → control-plane files only.
- `git -C <repo> show --stat 0002ddb7` → exactly the two allowed docs + evidence map.
- Grep `https?://[a-zA-Z0-9.-]+` over checklist + report + evidence map → only `http://127.0.0.1`.
- Grep `onrender|sk-|Bearer|-----BEGIN|eyJ|password|secret[_-]?key|service[_-]?role` (case-insensitive) → no leaked values (only prohibitions/transcript).
- Read-verified against source: `services/api/app/main.py:6-11,66-82,104`; `apps/web/src/lib/rule-evaluation.ts:79,83,54-73,96-103`; `apps/web/.env.example:6-16,21-35`; `apps/web/src/lib/api.ts:146-154`; `render.yaml:16-19,118-119,128-135,156-168`; `docs/DEPLOYMENT_AND_ROLLBACK.md:40`.

**Recommendation to orchestrator:** record G5 = PASS. Advisory A1 is optional polish, not a blocking condition for acceptance.
