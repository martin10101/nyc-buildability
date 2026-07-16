# Gate Report

- Gate ID: G3 (independent human-style walkthrough)
- Task ID: M0-T005-R1 (secret scanner + contracts validator hardening)
- Reviewer: code-reviewer (independent; did not produce the work)
- Producer: backend-engineer
- Result: **PASS** (all 11 packet items genuinely fixed and re-verified by live execution; 5 residual defects recorded, none of equal severity to the defects this task closed, none gate-blocking)
- Environment: producer worktree `.claude/worktrees/M0-T005-R1`, branch `task/M0-T005-R1-scanner-hardening`, commit `1caa972`; plus a throwaway 2.2 MB clone in `%LOCALAPPDATA%\Temp\g3r-clone` and a temp venv with jsonschema 4.10.3 for the CI-live legacy path — both deleted after the review (final `git status --short` empty; temp glob `g3r*` empty). Every command below was re-run by this reviewer; no stored producer output was trusted. Producer report read LAST, after independent execution.
- Fixtures: all planted values were this reviewer's own (different bytes from the producer's), created and removed within the session.

## Acceptance criteria reviewed

`project-control/tasks/M0-T005-R1.json` — 11-item objective + scenarios S1–S6; original defect reproductions from `project-control/reports/M0-T005-G3-review.md` (D1–D7) and `M0-T005-G5-security-review.md` (F1 + required-rework items 1–9); every hunk of `git show 1caa972` for the three implementation files reviewed line by line.

## Per-item verification (all 11 packet items)

| # | Item | Method | Result |
|---|---|---|---|
| 1 | Compound-prefix generic regex (D1) | Live: `MY_DB_PASSWORD = "<23-char>"` → `generic-credential-assignment`. Desk: `AUTH_TOKEN="…"` and the exact original G3 repro `allowed_token = "Zq7pL9mXv2Rt8Kn3Jd6Ws1"` both now match (probes I, J) | **FIXED** | <!-- secretscan:allow historical G3 repro string, fake test value, gate-report evidence --> |
| 2 | Inventory-name class (D2) | Live: `GEOCLIENT_SUBSCRIPTION_KEY=<32-hex>` and `RENDER_DEPLOY_HOOK_URL_API=<url>` → `inventory-secret-name-assignment`, exit 1. Desk: YAML `NAME: value` form also matches (probe H) | **FIXED** (residuals R1-D1/D2 below) |
| 3 | Postgres-URI class (D2) | Live: `postgres://appuser:S3cr...zQxT@db.internal:5432/prod` (reviewer's fake demo value; defanged post-merge after the hardened scanner flagged the verbatim form on main — itself proof the class works) → `postgres-uri-with-password`, password-only masked `S3cr...zQxT` | **FIXED** (residuals R1-D1/D3) |
| 4 | Exact-path allowlist + template content scan (D3) | Live: rogue `g3r_dir/.env.example` with `SUPABASE_DB_PASSWORD=<value>` → finding, exit 1 (no basename skip). End-to-end in temp clone: value appended to `services/api/.env.example` → BOTH `inventory-secret-name-assignment` and `env-template-nonempty-value` at line 45, exit 1. Desk: 1-char value flagged; empty value and comments pass | **FIXED** |
| 5 | Empty pragma justification exits 1 (D4) | Live: justified pragma → `ALLOWLISTED LINE g3r_pragma.txt:1 -- justification: …`, exit 0; bare `# secretscan:allow` → `EMPTY PRAGMA` notice + finding + exit 1 | **FIXED** |
| 6 | UTF-16 BOM detection (D6) | Live: file created via real PowerShell 5.1 (`5.1.26100.8655`) `>` redirection, BOM `ff fe` verified; planted `rnd_` key inside detected `[render-api-key] rnd_...2345` | **FIXED** |
| 7 | Output sanitization (G5 F1) | Grep: the ONLY `print(` in either script is inside `emit()`. Live: pragma justification containing raw ESC+BEL emitted as `evil?]0;owned?` on one line. Desk: `sanitize_for_log("a\n::add-mask::SECRET\r::notice…")` → single line, `\n`/`\r` → `?` (workflow commands require `::` at line start — impossible after sanitization) | **FIXED** |
| 8 | Exit codes + visible skips (D5/D7) | Live: run from non-git `%TEMP%` → clear ERROR, exit 2 (distinct from findings=1). Desk: `list_files` monkeypatched to raise `CalledProcessError` → `main()` returns 2. Live (temp clone): planted 2,000,100-byte file and NUL-byte binary → `SKIPPED … oversized` / `SKIPPED … binary` notices printed | **FIXED** |
| 9 | Re-fixtured S2 / visible pragma notice | The G3-adjudicated evidence gap is closed: `ALLOWLISTED LINE` observed in real scanner output in this review (item 5) and in producer S2 line 19 | **FIXED** |
| 10 | RefResolver fail-closed guard | **Verified under REAL jsonschema 4.10.3** (temp venv; stronger than the producer's 4.26-poisoning simulation — closes their disclosed assumption 5): legacy `NOTE:` printed, 25 OK / 0 FAIL, exit 0, OK/FAIL lines byte-identical to the 4.26.0 run. Guard test: `$ref` to a non-store URI with `socket.create_connection`, `urllib.request.urlopen`, AND `jsonschema.validators.urlopen` all instrumented → `RefResolutionError` whose `str()` contains `REMOTE_REF_BLOCK_MSG`, **zero network attempts recorded**; marker-in-`str(exc)` confirms the fixture-loop detection at validate_contracts.py:490 fires (exception surfaces during `iter_errors`, is wrapped by 4.10.3's `resolve_from_url`, and the marker survives the wrap) | **FIXED** |
| 11 | Shared sanitize helper both scripts | Programmatic comparison: the `_CONTROL_CHARS_RE`…`emit()` blocks in the two scripts are textually identical; all output paths in validate_contracts.py routed through `emit` (grep-verified); `UnicodeDecodeError` added at all three `load_json` handlers (optional tail adopted) | **FIXED** |

## Scenario walkthrough (reviewer-executed, reviewer's own fixtures)

| Scenario | Case type | Input | Expected | Actual | Result |
|---|---|---|---|---|---|
| S1 | normal | clean tree, `python .github/scripts/secret_scan.py` | exit 0; exactly 3 path-exact notices; < 60 s | exit 0; `scanned 246 files in 0.55s`; exactly 3 `ALLOWLISTED PATH` notices (package-lock full-skip + 2 templates marked content-scanned) | **PASS** |
| S2 | invalid-input | reviewer's own 4-line UTF-8 fixture + UTF-16LE-BOM file (PS 5.1 redirection) | every line detected, correct class, masked; UTF-16 scanned | exit 1; 5/5: `generic` (compound `MY_DB_PASSWORD`), `inventory` (hex key), `postgres-uri` (password-only mask), `inventory` (deploy-hook URL), `render-api-key` inside the UTF-16 file; all first/last-4 masked | **PASS** |
| S3 | boundary | pragma with vs without justification | suppress WITH visible notice / exit 1 | `ALLOWLISTED LINE …:1 -- justification: G3-R1 reviewer fixture…` + exit 0; `EMPTY PRAGMA` + finding + exit 1 | **PASS** |
| S4 | ambiguous | rogue `.env.example` outside approved paths; approved template with value (temp clone) | both flagged | rogue: `[inventory-secret-name-assignment]`, exit 1; approved path: 2 findings (inventory + env-template classes) at `services/api/.env.example:45`, exit 1, with the content-scan notice still printed | **PASS** |
| S5 | failure | non-git dir; injection via pragma justification (ESC/BEL live, `\n::add-mask::` desk); ls-files failure | exit 2 distinct; sanitized single-line output | exit 2 with clear ERROR; control chars → `?`, output stays one line; monkeypatched ls-files failure → return 2 | **PASS** |
| S6 | regression | reviewer-replanted 9 original M0-T005 classes | identical classes/masks vs `M0-T005-G2-evidence.md` | 9/9, class labels and mask shapes byte-identical to baseline (`rnd_...1234`, `sbp_...4567`, `eyJh...3456`, `fake...2345`, `----...----`, `AKIA...FAKE`, `ghp_...0123`, `xoxb...oken`, `Zq7p...6Ws1`); commit touches no workflow files; package-lock still allowlisted | **PASS** |
| VC | regression | `validate_contracts.py` normal (4.26.0) / degraded stdlib-only / legacy 4.10.3 | identical verdicts in all modes | exit 0, 25 OK / 0 FAIL in all three modes; OK/FAIL lines diff-identical across modes | **PASS** |

Scope check: `git show --stat 1caa972` = exactly the 3 implementation files + producer report; all inside `allowed_paths`; no workflow, task, or gate files touched.

## Defects (residual; none gate-blocking)

1. **R1-D1 [low-medium] Pre-existing placeholder hints `$`, `<`, `{` suppress real secrets in the NEW classes' wider charsets** — `secret_scan.py:68-71` hints are applied to inventory values (`:189-193`) and the full postgres match (`:194-199`), whose charsets — unlike the generic class's — permit those characters. A real password containing `$`/`<`/`{` evades. Repro: `scan_line('SUPABASE_DB_PASSWORD=Xk9q$LmWv3Tz7Bn2R', False)` → `[]`; `scan_line('postgres://postgres:Xk9q$LmWv7Tz3Bn2R@db.host:5432/app', False)` → `[]`. Undisclosed (producer disclosed only the two NEW hints). `$` in passwords is common. Fold into the next hardening pass / G5 attention; compensated by push protection (blocker-tracked owner action).
2. **R1-D2 [low] Inventory class misses `NAME = value` (whitespace around `=`)** — `secret_scan.py:120-122` deliberately requires the value immediately after `=` (disclosed, kills the six historical-report false positives), but this leaves Python-config style `GEOCLIENT_SUBSCRIPTION_KEY = "<32-hex>"` uncovered by ALL classes (`key` alone is not a generic keyword). Repro: probe A → `[]`. Same for `VERCEL_TOKEN = <unquoted>` (probe B; `TOKEN` is a keyword but generic requires quotes).
3. **R1-D3 [low] `user:pass` hint can suppress a real URI** — username ending `user` + password starting `pass`: `scan_line('postgres://produser:passXk9qLmWv7Tz@db.host:5432/app', False)` → `[]` (`appuser`/`dbuser` are common usernames). Narrow; quantified under adjudication (b).
4. **R1-D4 [info] Inventory value floor `{8,}`** — `secret_scan.py:121`: values under 8 chars evade the inventory class (probe C). Undisclosed but negligible for real credentials.
5. **R1-D5 [low] `docs/SECRETS_POLICY.md` §5 first bullet is now stale** — still says "basename path allowlist" and lists only the 9 original classes, misdescribing the (stronger) implemented mechanism. Contract-bounded: the packet authorized exactly one §5 sentence, which the producer changed correctly. **Orchestrator action:** approve the 3–4 line §5 touch-up in a follow-up; the policy must not contradict the code it describes (this exact pattern — policy overstating/mis-stating enforcement — motivated this rework).

## Adjudication of the three producer disclosures

- **(a) Transient S4b touch of forbidden `services/api/.env.example` (reverted): ACCEPTED with process note.** Disclosed in the report, reverted in the same block via `git checkout --`, zero residual (commit stat = 4 allowed files only; my clean-tree S1 and `git status` confirm). However, it was avoidable: this reviewer executed the same end-to-end test in a 2.2 MB throwaway local clone without touching the worktree file. Process rule going forward: exact-path-keyed checks are tested in a temp clone, not by transiently editing forbidden paths.
- **(b) Placeholder-hint extensions `"..."` and `"user:pass"`: ACCEPTED; suppression risk quantified as low, and dominated by an undisclosed neighbor.** `"..."`: real base64/hex/JWT charmatter cannot produce a literal ellipsis by construction of those formats; only a human-chosen password containing `...` could be missed — negligible. `"user:pass"`: real miss demonstrated (R1-D3) but requires the conjunction username-ends-`user` AND password-starts-`pass` — narrow. The materially larger suppression surface is R1-D1 (`$`/`<`/`{` on the new charsets), which the producer did NOT disclose; net risk assessment therefore shifts to R1-D1, not the two new hints.
- **(c) Stale policy §5 wording left for orchestrator: ACCEPTED as contract-compliant.** The packet's output spec was "one section-5 sentence"; producer complied exactly and disclosed the residual (limitation 3). Tracked here as R1-D5 — must not be dropped.

## Original-defect closure matrix (reproduced originals vs new code)

D1 ✔ (probes I/J + S2), D2 ✔ (S2 + probes E/H; residual forms in R1-D2), D3 ✔ (rogue file scanned; decoy-basename channel closed), D4 ✔ (S3b), D5 ✔ (monkeypatch → 2), D6 ✔ (real PS 5.1 file), D7 ✔ (live SKIPPED notices), G5-F1 ✔ (grep + live ESC test), M0-T009-G5-F2 ✔ (validate_contracts emit), item 10 ✔ (live 4.10.3), F3-optional ✔ (UnicodeDecodeError).

## Low-storage / cleanup verification

Peak temporary usage: ~2.2 MB clone + ~15 MB venv in `%LOCALAPPDATA%\Temp`, both deleted (post-cleanup `g3r*` glob empty). Reviewer fixtures in the worktree removed; final `git status --short` in the worktree: empty. No persistent artifacts written anywhere except this report in the main checkout. Scanner runtime 0.47–0.88 s (budget 60 s).

## Reviewer conclusion

**PASS.** All 11 contracted items are genuinely fixed and were re-verified by this reviewer with fresh fixtures and live execution — including the two paths the producer could not execute honestly on this host (real jsonschema 4.10.3 legacy engine; end-to-end approved-template content check without touching a forbidden path). The five residual defects are strictly narrower than the closed ones, are in the detective layer's negative space, and carry the same compensating-control rationale G5 already accepted (push protection pending owner action; no real credentials exist yet). Recommended for G5 re-check focus: R1-D1 (hint/charset interaction), R1-D3, and confirmation after the next CI run that the legacy `NOTE:` appears in the live contracts-job log.
