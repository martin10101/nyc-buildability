# Gate Report — M0-T005-R1 — G5 Security and Privacy Gate

- Gate ID: G5 (security and privacy)
- Task ID: M0-T005-R1 (secret scanner + contracts validator hardening; burn-down of M0-T005 G5 conditions and M0-T009 G5 F1/F2/F3)
- Reviewer: security-reviewer (independent; did not produce the work; did not perform G3)
- Producer: backend-engineer
- Result: **PASS** (no gate-blocking defect; 3 Low findings and 4 Info notes, all in disclosed negative space; follow-up scope listed)
- Review location: producer worktree `.claude/worktrees/M0-T005-R1`, branch `task/M0-T005-R1-scanner-hardening`, commit under review `1caa972`; one follow-on docs-only commit `a7f1f82` observed on the branch (see Note A)
- Method: reviewer independently executed live adversarial probes in a scratch area of the worktree (all scratch files deleted afterward; `git status --porcelain` clean at end), plus desk unit tests via importlib; producer report read LAST, after all reviewer evidence was captured
- Gate recording: delegated to the orchestrator per ADR-005; this reviewer wrote only this report file, ran no `project_control.py`, made no git writes

## 1. Scope and acceptance criteria reviewed

Task packet `project-control/tasks/M0-T005-R1.json` (11 items, S1–S6); M0-T005 G5 required-rework items 1–9; M0-T009 G5 findings F1 (RefResolver network fetch), F2 (log injection), F3 (UnicodeDecodeError); G5 catalog in `docs/GATES_AND_CHECKPOINTS.md`. Diff reviewed: `git show 1caa972` — exactly 4 files: `.github/scripts/secret_scan.py`, `.github/scripts/validate_contracts.py`, `docs/SECRETS_POLICY.md` (one §5 sentence), `project-control/reports/M0-T005-R1-producer-report.md`. No workflow, service, or tool files touched (forbidden paths respected).

## 2. Detection efficacy — reviewer's OWN adversarial suite (live, not producer fixtures)

Reviewer-crafted cases planted in `g5-scratch/` (26-line UTF-8 file + UTF-16LE file + decoy `.env.example`), scanned by the real script, then deleted. Full output captured in-session; exit code 1 with 16 findings.

### Detected (16/16 intended-detection cases)

| # | Case | Class reported |
|---|------|----------------|
| 1 | `AUTH_TOKEN = "<22-char high-entropy>"` (compound prefix, spaces around `=`) | generic-credential-assignment |
| 2 | `DB_PASSWORD="<22-char>"` | generic-credential-assignment |
| 3 | `allowed_token = '<22-char>'` (lowercase compound, single quotes) | generic-credential-assignment |
| 4 | quotes-in-quotes: `cfg = "AUTH_TOKEN='<22-char>'"` | generic-credential-assignment |
| 5 | `GEOCLIENT_SUBSCRIPTION_KEY=<32-hex>` unquoted | inventory-secret-name-assignment |
| 6 | `GEOCLIENT_SUBSCRIPTION_KEY="<32-hex>"` quoted, no spaces (verified in producer S2; reviewer variant #5 unquoted) | inventory-secret-name-assignment |
| 7 | `VERCEL_TOKEN: <value>` (YAML form) | inventory-secret-name-assignment |
| 8 | `RENDER_DEPLOY_HOOK_URL_API=https://api.render.com/deploy/srv-…?key=…` | inventory-secret-name-assignment | <!-- secretscan:allow reviewer adversarial demo value, fake/elided, gate-report evidence --> |
| 9 | `SUPABASE_DB_URL=postgresql://postgres:<pw>@db…supabase.co:5432/…` | inventory + postgres (double hit, both correct) |
| 10 | `conn = "postgresql://svc:<pw>@db.internal:5432/app"` (URI inside quoted string) | postgres-uri-with-password |
| 11 | `postgresql://svc:p%40ss…@host/db` (percent-ENCODED password) | postgres-uri-with-password | <!-- secretscan:allow reviewer adversarial demo value, fake/elided, gate-report evidence --> |
| 12 | `ANTHROPIC_API_KEY=sk-ant-api03-…` | inventory-secret-name-assignment | <!-- secretscan:allow reviewer adversarial demo value, fake/elided, gate-report evidence --> |
| 13 | `SENTRY_DSN=https://…@o123456.ingest.sentry.io/…` | inventory-secret-name-assignment | <!-- secretscan:allow reviewer adversarial demo value, fake/elided, gate-report evidence --> |
| 14 | UTF-16LE + BOM file containing `rnd_<20-alnum>` | render-api-key (file scanned, NOT skipped) |
| 15 | Decoy `.env.example` at NON-approved path with `SUPABASE_DB_PASSWORD=<value>` | inventory-secret-name-assignment (no basename privilege) |
| 16 | Finding line with `# secretscan:allow` EMPTY justification | reported as finding + `EMPTY PRAGMA` notice, exit 1 |

All masked first/last-4; no full value ever printed.

### Missed (10 designed near-misses, all as predicted from source; per-case adjudication)

| # | Near-miss | Why missed | Adjudication |
|---|-----------|------------|--------------|
| M1 | `AUTH_TOKEN=<unquoted non-inventory value>` | generic class requires quotes (unchanged design) | Disclosed since M0-T005; push protection is the stated compensating layer |
| M2 | secret split across two lines (`AUTH_TOKEN =` / `"<value>"`) | line-based scanner | Disclosed limitation; inherent to the design |
| M3 | `GEOCLIENT_SUBSCRIPTION_KEY = "<32-hex>"` (spaces around `=`) | inventory `=` branch requires value immediately after `=` (deliberate FP-kill for two-column doc listings); generic misses because bare `key` is not a keyword | **Finding F2 (Low)** — Python-style assignment of an inventory name evades ALL classes |
| M4 | `geoclient_subscription_key=<32-hex>` (lowercase) | inventory names are case-sensitive | Part of F2 (Low) |
| M5 | `RENDER_DEPLOY_HOOK_URL=<hook URL>` (suffix-less) | regex requires trailing `_` after URL; all policy §2 names carry suffixes | Info I1 |
| M6 | `postgresql://appuser:password123@host/db` | full-match placeholder gate: substring `user:pass` occurs whenever username ends "user" and password starts "pass" | **Finding F1 (Low)** |
| M7 | `postgresql://svc:Str0ng$Pass9x@host/db` | `$` hint fires on real passwords containing `$` | Part of F1 (Low) |
| M8 | `SUPABASE_DB_URL=postgresql://myuser:pass1234…@…` | `user:pass` hint suppresses BOTH inventory and postgres classes on an exact inventory-name secret | Part of F1 — the strongest miss found |
| M9 | `PASSWORD="abc...def<high-entropy>"` (literal `...` inside value) | new `...` hint | Negligible: generic charset excludes `:` and `$`, so only `...`/word hints apply; real base64/hex tokens do not contain `...` |
| M10 | `SUPABASE_DB_PASSWORD=Todo4Life…` | pre-existing word hint `todo` inside a real-shaped value | Pre-existing hint behavior, not introduced by this task; folded into F1 remediation |

Desk-probe extras: username containing `sample` (`postgresql://samplecorp:<pw>@…`) also suppresses the postgres class (full-match gating includes username) — folded into F1.

## 3. Verification of the security-specific dispatch items

### 3.1 Suppression-abuse surface (pragma)

Reviewer-verified live: `# secretscan:allow x` (junk one-character justification) suppresses a generic finding AND `# secretscan:allow demo suppression test` suppresses an inventory + JWT double-hit (i.e., the pragma suppresses every class on the line, including the deterministic inventory class). Both print a visible `ALLOWLISTED LINE <path>:<line> -- justification: <text>` notice on every scan run. Empty justification verified NOT to suppress (finding reported, `EMPTY PRAGMA` notice, exit 1) — item 5 satisfied.

**Adjudication: residual risk accepted, non-blocking.** A committer can still silently-ish suppress a real finding with a junk justification, but: (a) the notice is emitted on every CI run and in PR checks, making the suppression the loudest artifact in the log; (b) policy §5 obligates reviewers to check pragma justifications; (c) a malicious committer with repo write access can more simply gut `PATTERNS` — the self-modifiable-control threat model documented in the M0-T005 G5 report is unchanged and its mitigation remains server-side GitHub push protection (**B-006, still pending — keep priority**) plus branch protection. The visible-notice compensating control is sufficient for a repo-local detective layer; it would NOT be sufficient as the only layer, which is exactly why B-006 must not slip past the first real credential.

### 3.2 Placeholder-hint false-negative risk (`...`, `user:pass`)

Quantified per class:
- **generic**: value charset `[A-Za-z0-9+/=_.-]` cannot contain `:` or `$`, so of the new hints only `...` applies; real token formats (base64, hex, `rnd_`, `sbp_`, JWT segments) cannot contain a literal ellipsis. Risk ≈ negligible; only a human-chosen quoted password containing `...` is exposed (M9).
- **inventory (value-gated)** and **postgres (FULL-match-gated)**: `user:pass`, `$`, `<`, `{`, and word hints all can fire on real values. Demonstrated real-shape misses: M6/M7/M8/M10 and the `sample`-username probe. The postgres gate on the FULL match (including username) is the widest exposure: common username suffix "…user" + password prefix "pass…" or any marketing-word username suppresses a genuine URI.

**Adjudication: Low (F1), non-blocking** — this is negative space of a detective control that policy explicitly labels non-exhaustive, compensated by the env-template strict check (any non-empty value in the approved templates flags regardless of hints) and by B-006 once enabled. But the remediation is cheap and should ride the next scanner touch: gate the postgres class on the password group only; replace the `$` hint with `${` for the inventory/postgres classes (template interpolation is the actual FP source and `${…}` is already covered by `{`); apply `user:pass` only when the userinfo is exactly `user:pass`.

### 3.3 Fail-closed RefResolver guard (item 10) — independently reproduced

Reviewer probe (not the producer's script): loaded `jsonschema` 4.26.0 normally, evicted+blocked `referencing` via a `sys.meta_path` finder to force the legacy branch, installed tripwires on `socket.socket`, `requests.get`, and `urllib.request.urlopen`, loaded `validate_contracts.py` via importlib, and drove `make_validator` directly:

- Legacy NOTE printed once; validator's resolver is `_LocalOnlyRefResolver`.
- `$ref` → `https://attacker.invalid/evil.json` (store miss): `_RefResolutionError` wrapping the `REMOTE_REF_BLOCK_MSG` marker; **0 sockets created during validation** (the single tripwire entry in the first probe run was localized by a differential probe to `import requests` in the reviewer harness itself — urllib3's import-time IPv6 capability probe — not to the validator).
- `$ref` → `file:///C:/Windows/win.ini`: **also blocked** with the marker (the guard covers non-HTTP schemes, closing the local-file-read primitive too).
- In-store `$ref` to a second loaded schema resolves normally and produces correct validation errors (guard does not break legitimate refs).
- Choke-point confirmation from installed library source: `resolve()` → `_remote_cache` (lru-wrapped bound `resolve_from_url`) → `store[url]` → `resolve_remote(url)` on KeyError; the `handlers` dict, `requests.get`, and `urlopen` branches are ALL inside `resolve_remote`, and no `handlers` are passed. This structure is unchanged from jsonschema 2.x through 4.26, so the subclass override intercepts every scheme under 4.10.3 (the live CI runner version per M0-T009 G4) — consistent with M0-T009 PROBE B's trace of the same flow.
- The fixture loop converts a guard trip into an engine-verdict failure (build FAIL), not a degrade-to-NOTE — verified in source (`REMOTE_REF_BLOCK_MSG in str(exc)` branch).
- Grep of both scripts: zero network-capable imports (`urllib.parse.urljoin` is string-only). **M0-T009 F1: closed.**

### 3.4 Log-injection (items 7/11) — every output path

- Each script contains exactly ONE `print(` call, inside `emit()`, which routes every message through `sanitize_for_log()` (`[\x00-\x1f\x7f]` → `?`). Grep-verified: no other print/`sys.stderr.write`/`sys.stdout.write` in either script.
- Desk-tested against `\n::add-mask::…`, `\r\n::error…`, ESC, NUL, DEL, TAB, and a path shaped like a spoofed finding line: all emerge as ONE line with control characters replaced. GitHub workflow commands require `::` at start of a log line; sanitized output cannot produce a new line.
- Unicode line separators (U+0085/U+2028) survive sanitization but encode as multi-byte UTF-8, never a 0x0A byte, so the runner's line parser cannot be split by them; file content containing them is additionally split by `str.splitlines()` before scanning, so they never reach a finding tuple.
- Pragma justifications and masked values are printed mid-line after fixed prefixes; masked values are drawn from charsets that exclude control characters. **M0-T005 F1 + M0-T009 F2: closed.** `UnicodeDecodeError` added at all three `load_json` call sites (**M0-T009 F3: closed**; verified in diff at validate_contracts.py:457, 512, 556).

### 3.5 Exit-code and CI semantics (item 6)

- Reviewer-executed from a non-repo directory: exit **2** with a sanitized ERROR line, distinct from findings (1) and clean (0). `git ls-files` failure returns 2 by code inspection (same wrapped handler; producer's inability to execute that path non-destructively is reasonable).
- `secret-scan.yml` runs `python3 .github/scripts/secret_scan.py` with no `continue-on-error`, no `|| true`; ANY nonzero exit fails the job — a git failure can never read as "clean" in workflow context. Grep of all workflows found no exit-swallowing on the two jobs in scope (`generate-lockfile.yml`'s `exit 0` is a pre-existing unrelated skip path, out of this diff).
- Edge noted (Info I2): `git ls-files` succeeding but returning an empty list would yield "scanned 0 files … PASS" — unreachable after a successful checkout, but a one-line `scanned == 0 → exit 2` guard would remove the theoretical hole.

### 3.6 Transient forbidden-path disclosure (S4b)

Verified in the worktree: `git log --all -- services/api/.env.example` shows only the original M0-T005 commit (4886551); `git reflog` shows no commit ever contained the appended line; working tree clean. Producer disclosed the deviation prominently in the report. **Adjudication: acceptable this once — disclosed, transient, zero residue** — but unnecessary going forward: the reviewer exercised the same code path with zero file writes via `scan_line("SUPABASE_URL=https://…", env_template=True)` (returns the `env-template-nonempty-value` hit; empty and comment lines return none). Future scenario packs should specify the unit-call method instead of touching forbidden paths.

### 3.7 Remaining dispatch items (8)

- **No secrets in the diff:** producer report is fully defanged (`<…>` placeholders/masked outputs); reviewer's clean full-tree scan with the report committed passes (0 findings, 0 pragmas anywhere in the tree — no `ALLOWLISTED LINE` notices on the clean run).
- **No new network calls:** grep-verified both scripts (section 3.3).
- **Runtime:** clean scan 0.47 s / 246 files; validate_contracts 0.38 s; both far under 60 s.
- **Regression:** 3 path-exact `ALLOWLISTED PATH` notices (package-lock full-skip + 2 templates now content-scanned); original 9 classes confirmed alive via reviewer probes (rnd_ in UTF-16, JWT on the pragma line, generic) plus producer's S6 transcript showing all 9 at baseline positions with identical masking.

## 4. G5 checklist

| G5 item | Result | Evidence |
|---|---|---|
| RLS / cross-tenant isolation | N/A | Diff is two CI scripts + one policy sentence; no tenant/runtime code |
| Service-role secrecy | PASS | No secrets in diff; scanner now catches `SUPABASE_SERVICE_ROLE_KEY=<value>` deterministically (inventory class, reviewer-verified); templates content-scanned strictly |
| Private storage | N/A | No storage surface in diff |
| SSRF / injection defenses | PASS | RefResolver fail-closed guard independently reproduced for https AND file schemes, zero sockets (3.3); no subprocess shell, argv arrays only, no eval/exec |
| Upload controls | N/A | No upload surface |
| Prompt-injection defenses | N/A | No AI component; both scripts deterministic |
| Input validation | PASS | BOM/binary/oversize handling explicit with visible notices; UTF-16 decoded not skipped (reviewer-verified live); non-repo and ls-files failures exit 2 |
| Least privilege | PASS | Workflows untouched (forbidden path respected); `contents: read`, SHA-pinned checkout, no installs — unchanged from M0-T005 G5-verified posture |
| Sensitive-log redaction | PASS | Single sanitized emit path per script; first/last-4 masking unchanged; injection desk-tests all defeated (3.4) |
| Dependency vulnerabilities | PASS | Stdlib-only, both scripts; optional jsonschema strengthening layer unchanged |
| Detection efficacy (negative space) | PASS with F1/F2 | 16/16 reviewer adversarial detections; 10 near-miss FNs all in disclosed/adjudicated negative space (section 2) |

## 5. Findings

| # | Severity | Location | Finding | Reproduction | Remediation |
|---|---|---|---|---|---|
| F1 | **Low** | `secret_scan.py:68-71` (hints), `:120-127` (inventory/postgres), `:189-199` (gating) | Placeholder-hint false negatives: postgres class gates on the FULL match (username included), so `user:pass` substrings (username ending "user" + password starting "pass"), `$` in real passwords, and hint-words in usernames suppress genuine URIs; same hints suppress inventory-name values (reviewer misses M6–M8, M10, `sample`-username probe) | Plant `SUPABASE_DB_URL=postgresql://myuser:pass1234WqZx@db.host:5432/app` in a tracked file; run scanner; 0 findings | Gate postgres on the password group only; change `$` hint to `${` for inventory/postgres; apply `user:pass` only when userinfo == exactly `user:pass`. Fold into next scanner task; non-blocking because env-template strict check + pending B-006 push protection compensate |
| F2 | **Low** | `secret_scan.py:120-122` | Inventory class misses `NAME = value` (whitespace around `=`; deliberate FP trade-off for two-column doc listings) and lowercase name forms; combined with bare `key` not being a generic keyword, `GEOCLIENT_SUBSCRIPTION_KEY = "<32-hex>"` (Python-style) evades ALL classes | Reviewer case M3/M4 (live, 0 findings) | Allow `\s*=\s*` with a negative lookahead for the `NAME=\s+\d+:` listing shape, or add case-insensitive inventory matching; follow-up scope |
| F3 | **Low** | `secret_scan.py:271-276` | Pragma accepts junk justification ("x") and suppresses every class on the line, including deterministic inventory hits | Reviewer live: `# secretscan:allow x` suppressed a generic finding with visible notice | Accept residual (visible `ALLOWLISTED LINE` notice + policy §5 reviewer duty); the real mitigation is server-side push protection — **keep B-006 open and prioritized**; optionally require a minimum justification length or a linked task ID in a future pass |
| I1 | Info | `secret_scan.py:117` | `RENDER_DEPLOY_HOOK_URL=` (suffix-less) not matched — regex requires trailing `_`; all policy §2 names carry suffixes, and the URL value matches no other class | Reviewer case M5 | Make the trailing suffix optional (`RENDER_DEPLOY_HOOK_URL(?:_[A-Z0-9_]*)?`) in follow-up |
| I2 | Info | `secret_scan.py:228-240` | `scanned == 0` with a succeeding ls-files still prints PASS/exit 0 (unreachable after a successful checkout) | n/a (theoretical) | `if scanned == 0: return 2` one-liner in follow-up |
| I3 | Info | Commit `a7f1f82` (follow-on, docs-only, outside the dispatched review commit) | Fixes the stale §5 text (producer limitation 3) and applies ADR-004 Vercel-row replacement; however the new §5 sentence lists "Render deploy-hook URLs, and hex-format keys" as if they were standalone value-shape detectors — they are detected only via the inventory NAME class (see M5). Minor overstatement of the same kind D2 originally flagged | Read §5 vs. reviewer case M5 | One-line wording fix ("…detected via their inventory names…") whenever the doc is next touched; orchestrator should include a7f1f82 in the merge set and have G3 confirm the docs diff |
| I4 | Info | Process | S4b touched a forbidden path transiently (disclosed, reverted, zero residue — verified via git log --all/reflog/status) | Section 3.6 | Future packets: use the `scan_line(…, env_template=True)` unit-call method; no file touch needed |

No Critical, High, or Medium findings. All five M0-T005 G5 required-rework items verified closed (compound prefix, inventory class, postgres class, exact-path allowlist + template content scan, empty-pragma fail), plus items 6–9 (UTF-16, sanitization, exit codes, re-fixture with real pragma hit) and all three M0-T009 findings (F1 RefResolver, F2 log injection, F3 UnicodeDecodeError).

## 6. M0-T005 G5 condition — status

The M0-T005 G5 PASS was conditional on this rework landing **before the first real credential enters the repository or M0 exit**. **The producer-scope portion of that condition is satisfied by this work once merged to main.** Two orchestrator-scope companions remain open and are still required for the condition's spirit: (a) **B-006 — enable GitHub secret scanning + push protection** (the designated compensating control for every false negative documented above, including F1/F2 here); (b) branch-protection confirmation on `main`. Neither blocks this gate; both should be closed before the first real credential is provisioned (B-001/B-002/B-004).

## 7. Reviewer attestation

Producer and reviewer identities differ. Implementation was not modified; the only file written is this report (per dispatch). All reviewer scratch fixtures were deleted and the worktree verified clean afterward. Live probes ran without permission interference. Gate recording in the ledger is the orchestrator's responsibility per ADR-005.
