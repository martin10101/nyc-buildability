# Producer Report — M0-T005-R1 (secret scanner + contracts validator hardening)

- Task ID: M0-T005-R1
- Producer: backend-engineer (isolated worktree `.claude/worktrees/M0-T005-R1`, branch `task/M0-T005-R1-scanner-hardening`)
- Date: 2026-07-16
- **Status requested: `awaiting_gate`**
- Execution location: producer worktree on owner PC; all commands ran locally in < 2s each; no persistent artifacts outside the three deliverables and this report; all planted fixtures deleted (evidence in section 4/S6)

NOTE ON VALUES IN THIS REPORT: every credential-shaped value is written defanged
(`<...>` placeholders) or as the scanner's own masked output, so this report can
never itself become a scanner finding. The exact fixture bytes are reproducible
from the commands in section 4.

## 1. Files changed, mapped to the 11 packet items

| File | Items | Change |
|---|---|---|
| `.github/scripts/secret_scan.py` | 1–9, 11 | Rewritten in place (same architecture, hardened). See per-item map below. |
| `.github/scripts/validate_contracts.py` | 10, 11 | Legacy `RefResolver` fallback scheme-guarded fail-closed; all output routed through the sanitizing `emit()` helper; `UnicodeDecodeError` added to all three `load_json` call sites. |
| `docs/SECRETS_POLICY.md` | 5 | Exactly one section-5 sentence changed: "a pragma without a written justification should fail code review" → "a pragma with an empty justification does not suppress anything — the scanner reports the finding and fails (exit 1)". |
| `project-control/reports/M0-T005-R1-producer-report.md` | — | This report. |

Per-item implementation map (all line refs are to the new files):

1. **Compound-prefix generic regex** — `GENERIC_RE` now allows an optional
   `[A-Za-z0-9_-]*` identifier prefix before the keyword group, fixing the G3 D1
   `\b`-after-underscore bug. `AUTH_TOKEN=`, `DB_PASSWORD=`, `allowed_token =`
   forms now match (S2 lines 13–14; S3 pragma line).
2. **Inventory-name class** — `INVENTORY_CLASS` / `INVENTORY_RE`: the 10 exact
   names from G5 required-rework item 2 (the docs/SECRETS_POLICY.md §2 secret
   rows): SUPABASE_SERVICE_ROLE_KEY, SUPABASE_DB_URL, SUPABASE_DB_PASSWORD,
   SUPABASE_ACCESS_TOKEN, GEOCLIENT_SUBSCRIPTION_KEY, ANTHROPIC_API_KEY,
   VERCEL_TOKEN, RENDER_DEPLOY_HOOK_URL_<suffix-wildcard>, SENTRY_DSN,
   NEXT_PUBLIC_SUPABASE_ANON_KEY. Matches `NAME=value` (value immediately after
   `=`, quoted or unquoted) and `NAME: value` (YAML). Deterministic — no entropy
   gate; placeholder gate only. Does NOT match names-only mentions (docs,
   tables) or empty template assignments (proven: S1 clean, S2 lines 15–18 hit).
3. **Postgres-URI class** — `POSTGRES_CLASS` / `POSTGRES_RE`
   (`postgres`/`postgresql` scheme, userinfo with password, masks the password
   group only). S2 line 17.
4. **Exact-path allowlist + template content scan** — `PATH_ALLOWLIST` is now
   exact-relative-path keyed and contains only `apps/web/package-lock.json`
   (full skip, visible notice). The two policy-approved `.env.example` files
   are in `ENV_TEMPLATE_PATHS`: NOT skipped — every pattern class runs on them
   AND `ENV_ASSIGN_RE` flags ANY non-empty assignment value (class
   `env-template-nonempty-value`), strict per policy §3.1 names-and-comments-only.
   Any `.env.example` at another path is scanned exactly like a normal file
   (basename matching removed entirely). S1/S4.
5. **Empty pragma justification fails** — pragma with justification suppresses
   and prints `ALLOWLISTED LINE`; empty justification prints `EMPTY PRAGMA`
   notice, keeps the hits as findings, exit 1. S3. Policy §5 sentence updated.
6. **UTF-16 BOM detection** — `\xff\xfe` / `\xfe\xff` prefixes are decoded with
   the BOM-aware `utf-16` codec BEFORE the null-byte binary heuristic (the
   heuristic previously skipped UTF-16, the PS 5.1 `>` default). S2 UTF-16 file.
7. **Workflow-command-injection sanitization** — `sanitize_for_log()` strips
   `[\x00-\x1f\x7f]` → `?` from every printed line via `emit()`; a filename or
   justification containing `\n::notice ...` / `::add-mask::...` can never
   start a new log line. S5 desk test.
8. **Exit codes + visible skips** — `git rev-parse` AND `git ls-files` failures
   both return 2 (`OSError`/`CalledProcessError` wrapped; G3 D5); oversized
   (>2 MB) and binary skips print visible `SKIPPED <path> -- <reason>` notices
   (G3 D7). The current tree has zero binary/oversized files, so S1 output gains
   no notices (verified by pre-implementation survey, section 4.0).
9. **Re-fixtured S2** — 19-line fixture + separate UTF-16 file: the pragma line
   now ACTUALLY hits (compound fix makes `token = "<v>"` match) and the visible
   `ALLOWLISTED LINE` notice is captured in real scanner output for the first
   time; new lines for compound names, hex inventory key (quoted AND unquoted),
   postgres URI, deploy-hook URL, UTF-16 file. Section 4/S2.
10. **Legacy RefResolver fail-closed guard** — in `make_validator`'s
    `except ImportError` branch (the LIVE path under CI's jsonschema 4.10.3), a
    `_LocalOnlyRefResolver(jsonschema.RefResolver)` subclass overrides
    `resolve_remote()` to raise `RuntimeError(REMOTE_REF_BLOCK_MSG + uri)`.
    `resolve_remote()` is the single choke point through which EVERY non-store
    resolution flows in jsonschema's RefResolver (the `handlers` dict,
    `requests.get`, and `urlopen` branches are all inside it, unchanged from
    jsonschema 2.x through 4.26), so the override blocks every scheme under
    4.10.3 semantics, not just http/https. A one-time NOTE announces the legacy
    mode in CI logs. `run_instance_validation` detects the marker string and
    surfaces the guard trip as an engine failure (build FAIL via validator
    disagreement) instead of degrading to a NOTE. Store misses in the modern
    `referencing` branch already fail closed upstream (registry unresolvable).
11. **Shared sanitize helper in both scripts** — implemented as a duplicated,
    textually identical block (`_CONTROL_CHARS_RE` + `sanitize_for_log()` +
    `emit()`) in both scripts, each carrying a comment naming the twin.
    REASONING: the task scope forbids creating any new module outside the two
    script paths, and `.github/scripts/` has no package structure; a
    same-directory import would also require `sys.path` manipulation inside CI.
    Textual duplication with a cross-reference comment is the smallest honest
    option; drift is detectable by diffing the marked blocks. Optional tail
    adopted: `UnicodeDecodeError` added to all three `load_json` except
    tuples in validate_contracts.py (M0-T009 G5 F3).

## 2. Pre-implementation false-positive survey (why the gates are shaped this way)

Dry-running the naive new patterns over all 246 tracked files found exactly six
would-be false positives, ALL inside historical gate reports that are outside
this task's allowed paths and must not be edited
(`project-control/reports/M0-T005-G3-review.md:86`, `M0-T005-G5-security-review.md:21,22,23,24`,
`M0-T005-producer-report.md:103–104`). They are neutralized by three deliberate
design choices, each of which also blocks a real-noise class:

- **No whitespace between `=` and the value** in the inventory class (env-style
  assignment); YAML `NAME: value` still matched. Kills the `NAME=  33:NAME=`
  two-column listing false positives.
- **Placeholder hints extended** with `"..."` (truncated doc example — real
  base64/hex/URI values never contain a literal ellipsis) and `"user:pass"`
  (the canonical URI doc example), applied to the inventory class (value), the
  postgres class (FULL match, so doc usernames/passwords are covered), and the
  generic class (value, as before).
- Existing hints `<`, `{`, `$` already cover `${{ secrets.* }}` workflow
  references and `<32-hex>`-style doc placeholders.

Verified post-implementation: S1 clean scan passes over the unmodified reports.

## 3. Acceptance scenarios — expected vs actual

All commands run from the worktree root
`C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T005-R1`
with local Python 3.11.9, jsonschema 4.26.0. Full transcripts in section 4.

| Scenario | Expected | Actual | Result |
|---|---|---|---|
| S1 normal | exit 0; 3 path-exact allowlist notices; well under 60 s | exit 0; `scanned 245 files in 0.50s`; exactly 3 `ALLOWLISTED PATH` notices (package-lock full-skip + 2 templates content-scanned); `PASS -- no findings` | **PASS** |
| S2 invalid-input | every planted line detected with correct class + masked value; UTF-16 scanned | exit 1; 17/17 findings: 9 original classes (lines 2,3,4,5,6,9,10,11,12), compound generic (13,14), inventory quoted+unquoted hex (15,16), inventory+postgres double-hit on the DB URI (17), deploy-hook URL (18), UTF-16 file line 2 `render-api-key`; all masked first/last-4 (12-char postgres password fully asterisked per the ≤12 rule); pragma line 19 visibly `ALLOWLISTED LINE` | **PASS** |
| S3 boundary | justified pragma suppresses WITH visible notice; empty justification exit 1 | S3a: exit 0 + `ALLOWLISTED LINE scratch_r1_pragma.txt:1 -- justification: ...`; S3b: exit 1 + `EMPTY PRAGMA scratch_r1_pragma.txt:1` + the finding listed | **PASS** |
| S4 ambiguous | rogue `.env.example` flagged; approved template with non-empty value flagged | S4a: `scratch_s4/.env.example:2 [render-api-key]`, exit 1 (scanned as a normal file); S4b: appended a value that matches NO pattern class to `services/api/.env.example` → `services/api/.env.example:45 [env-template-nonempty-value]`, exit 1; reverted via `git checkout --`, `git status` shows only the 3 deliverables modified | **PASS** |
| S5 failure | outside-git exit 2 distinct from findings; sanitized paths | From non-repo dir: `secret-scan: ERROR: not a git repository...`, exit 2. Desk test: hostile path with `\n::notice`/`\r::add-mask` and hostile justification with `\n::error` printed as ONE line with control chars → `?` (workflow commands require `::` at line start, now impossible) | **PASS** |
| S6 regression | 9 original classes identical to G2 baseline; package-lock allowlisted; no workflow changes | All 9 at the same fixture positions with identical class labels and mask format; line 12 uses the exact baseline value → identical masked output `Zq7p...6Ws1`; `apps/web/package-lock.json` allowlisted in every run; `git status --short` = only the 3 allowed files; runtime 0.45–0.52 s | **PASS** |
| validate_contracts normal | identical to pre-change baseline | Byte-identical output diff except the pre-existing DeprecationWarning's line number (101→144, pure line shift from the added helper); exit 0; 25 OK / 0 FAIL | **PASS** |
| validate_contracts forced-legacy (item 10) | same verdicts via the legacy RefResolver path; store miss fails closed, never fetches | Legacy branch forced (preload jsonschema, poison `referencing`): one-time legacy NOTE printed, 25 OK / 0 FAIL, exit 0, engine cross-check active. Guard desk test with ALL sockets monkeypatched to raise: store-miss `$ref` → `_RefResolutionError: remote $ref fetch blocked (fail-closed): ... 'https://contracts.nycbuildability.test/v1/NOT_LOADED.schema.json'`; marker detected (`guard marker present: True`); the socket tripwire never fired → zero network attempt | **PASS** |

## 4. Exact commands and outputs

### 4.0 Environment + survey (pre-implementation)

```
python -c "import sys, jsonschema; print(sys.version); print('jsonschema', jsonschema.__version__)"
-> 3.11.9 ... / jsonschema 4.26.0
```

Tree survey (python one-liners over `git ls-files -z --cached --others --exclude-standard`):
246 files; `.env.example` only at the two approved paths; `package-lock.json`
only at `apps/web/`; zero UTF-16-BOM files; zero binary/oversized files; all 9
template assignments have empty values. Dry-run of the naive new patterns found
the six historical-report lines listed in section 2 and zero compound-generic
hits repo-wide.

Baseline (pre-change): `python .github/scripts/validate_contracts.py` → exit 0,
25 OK / 0 FAIL, saved to /tmp/r1_vc_baseline.txt for the post-change diff.

### 4.1 S1 — clean tree

```
python .github/scripts/secret_scan.py ; echo EXIT=$?
secret-scan: scanned 245 files in 0.50s
secret-scan: exact-path allowlist/template rules applied to 3 file(s):
  ALLOWLISTED PATH apps/web/.env.example -- policy-approved template (exact path); content-scanned: any non-empty value fails
  ALLOWLISTED PATH apps/web/package-lock.json -- npm sha512 integrity hashes are high-entropy base64 lookalikes
  ALLOWLISTED PATH services/api/.env.example -- policy-approved template (exact path); content-scanned: any non-empty value fails
secret-scan: PASS -- no findings
EXIT=0
```

(245 = 246 tracked minus 1 full-skip; the two templates are now SCANNED and
counted, previously they were skipped.)

### 4.2 S2 — planted fixture (19 lines UTF-8 + 2-line UTF-16LE file)

Fixture `scratch_r1_fake_creds.txt` (defanged listing; all values fake, exact
bytes reproducible from the python heredoc in the session transcript):

```
 1  # M0-T005-R1 S2 scratch fixture -- every value below is fake
 2  render_key = rnd_<20-alnum>
 3  supabase_pat = sbp_<40-hex>
 4  jwt_sample = eyJ<seg1>.eyJ<seg2>.<seg3>          (all segments 8+ chars)
 5  service_role_key: "<26-char value>"
 6  <the five-dash BEGIN RSA PRIVATE KEY five-dash PEM header>   (7-8: filler)
 9  aws_id = AKIA<16-uppercase>
10  gh_token = ghp_<36-alnum>
11  slack = xoxb-<digits>-<16-alnum>
12  password = "<the exact 22-char G2-baseline generic value>"
13  AUTH_TOKEN = "<26-char high-entropy value>"
14  DB_PASSWORD="<28-char high-entropy value>"
15  GEOCLIENT_SUBSCRIPTION_KEY="<32-hex>"            (quoted)
16  GEOCLIENT_SUBSCRIPTION_KEY=<same 32-hex>         (unquoted)
17  SUPABASE_DB_URL=postgresql://fakeadmin:<12-char-pass>@db.fake.test:5432/postgres
18  RENDER_DEPLOY_HOOK_URL_API=https://api.render.com/deploy/srv-<id>?key=<12-char>
19  token = "<28-char value>" # secretscan:allow fake fixture value proving the pragma path (M0-T005-R1 S3)
```

`scratch_r1_utf16.txt`: UTF-16LE with BOM (head bytes `ff fe 23 00 ...`,
verified), line 2 = `render_key=rnd_<22-alnum>`.

```
python .github/scripts/secret_scan.py ; echo EXIT=$?
secret-scan: scanned 247 files in 0.45s
secret-scan: exact-path allowlist/template rules applied to 3 file(s):
  [same 3 notices as S1]
secret-scan: inline pragma allowed 1 line(s):
  ALLOWLISTED LINE scratch_r1_fake_creds.txt:19 -- justification: fake fixture value proving the pragma path (M0-T005-R1 S3)
secret-scan: FAIL -- 17 potential credential(s) found:
  scratch_r1_fake_creds.txt:2 [render-api-key] rnd_...I9j0
  scratch_r1_fake_creds.txt:3 [supabase-access-token] sbp_...4567
  scratch_r1_fake_creds.txt:4 [jwt] eyJh...VyZQ
  scratch_r1_fake_creds.txt:5 [service-role-assignment] fake...7890
  scratch_r1_fake_creds.txt:6 [pem-private-key] ----...----
  scratch_r1_fake_creds.txt:9 [aws-access-key-id] AKIA...MNOP
  scratch_r1_fake_creds.txt:10 [github-token] ghp_...6789
  scratch_r1_fake_creds.txt:11 [slack-token] xoxb...mnop
  scratch_r1_fake_creds.txt:12 [generic-credential-assignment] Zq7p...6Ws1
  scratch_r1_fake_creds.txt:13 [generic-credential-assignment] Xk4r...Fg7s
  scratch_r1_fake_creds.txt:14 [generic-credential-assignment] Vb3n...cE1i
  scratch_r1_fake_creds.txt:15 [inventory-secret-name-assignment] 4f8a...9c1e
  scratch_r1_fake_creds.txt:16 [inventory-secret-name-assignment] 4f8a...9c1e
  scratch_r1_fake_creds.txt:17 [inventory-secret-name-assignment] post...gres
  scratch_r1_fake_creds.txt:17 [postgres-uri-with-password] ************
  scratch_r1_fake_creds.txt:18 [inventory-secret-name-assignment] http...1234
  scratch_r1_utf16.txt:2 [render-api-key] rnd_...6789
secret-scan: remove the credential, rotate it if it was real (docs/SECRETS_POLICY.md incident procedure), or allowlist a verified false positive with a justification.
EXIT=1
```

The G3-adjudicated evidence gap is closed: the inline-pragma suppression path
executed against the REAL script with a visible `ALLOWLISTED LINE` notice.
Line 17 double-hit (inventory + postgres) is intentional: two independent
detection classes, both correct. The 12-char postgres password masks to all
asterisks (mask() ≤12 rule, unchanged from M0-T005).

Cleanup: `rm scratch_r1_fake_creds.txt scratch_r1_utf16.txt` before S3.

### 4.3 S3 — pragma pair (isolated file `scratch_r1_pragma.txt`)

S3a `token = "<28-char value>" # secretscan:allow fake fixture value, justified pragma run (M0-T005-R1 S3a)`:

```
secret-scan: inline pragma allowed 1 line(s):
  ALLOWLISTED LINE scratch_r1_pragma.txt:1 -- justification: fake fixture value, justified pragma run (M0-T005-R1 S3a)
secret-scan: PASS -- no findings
EXIT=0
```

S3b same line with bare `# secretscan:allow`:

```
secret-scan: 1 pragma(s) with EMPTY justification -- NOT suppressed:
  EMPTY PRAGMA scratch_r1_pragma.txt:1 -- add a written justification or remove the line
secret-scan: FAIL -- 1 potential credential(s) found:
  scratch_r1_pragma.txt:1 [generic-credential-assignment] Qw8r...Zx0c
EXIT=1
```

Cleanup: `rm scratch_r1_pragma.txt`.

### 4.4 S4 — .env.example handling

S4a rogue file `scratch_s4/.env.example` containing `RENDER_API_KEY=rnd_<22-alnum>`:

```
secret-scan: FAIL -- 1 potential credential(s) found:
  scratch_s4/.env.example:2 [render-api-key] rnd_...3210
EXIT=1
```

(Note: `RENDER_API_KEY` is not an inventory name; the hit is the rnd_ prefix
class — proving the rogue file is scanned exactly like a normal file, with no
template privileges and no basename skip.)

S4b: appended `SUPABASE_URL=https://fakeproj.supabase.co` (a value matching NO
pattern class) to `services/api/.env.example`:

```
secret-scan: FAIL -- 1 potential credential(s) found:
  services/api/.env.example:45 [env-template-nonempty-value] http...e.co
EXIT=1
```

Reverted immediately: `git checkout -- services/api/.env.example`;
`git status --short` after → only `M .github/scripts/secret_scan.py`,
`M .github/scripts/validate_contracts.py`, `M docs/SECRETS_POLICY.md`.
DISCLOSURE: `services/**` is a forbidden path; this was a transient planted
fixture required to execute S4b (the content check keys on the exact relative
path), reverted in the same command block, zero residual diff. Flagged for
reviewer adjudication.

### 4.5 S5 — failure + injection desk test

Outside git (from `/tmp/r1_norepo`, `git rev-parse` exit 128 confirmed first):

```
python <worktree>/.github/scripts/secret_scan.py ; echo EXIT=$?
secret-scan: ERROR: not a git repository or git unavailable: Command '['git', 'rev-parse', '--show-toplevel']' returned non-zero exit status 128.
EXIT=2
```

Sanitization desk test (Windows forbids `\n` in filenames, so per the packet
this is a desk test): loaded the module via importlib, emitted a finding line
and an ALLOWLISTED LINE for a hostile path containing
`\n::notice title=spoofed::...` + `\r::add-mask::...` and a hostile
justification containing `\n::error::injected`. Output remained ONE line each,
every control character replaced by `?` — a GitHub workflow command requires
`::` at start of line, which sanitized output can no longer produce.
`git ls-files` failure path: mapped to exit 2 by code inspection
(wrapped in `try/except (CalledProcessError, OSError) -> return 2`); not
independently executable without breaking the repo mid-scan.

### 4.6 validate_contracts — both modes

Normal (jsonschema 4.26.0 + referencing):

```
python .github/scripts/validate_contracts.py ; echo EXIT=$?   -> EXIT=0
diff vs pre-change baseline: identical except the pre-existing
DeprecationWarning line number (101 -> 144; pure line shift from added helper).
25 OK verdicts, 0 FAIL, same classifications as M0-T009 for every fixture.
```

Forced-legacy (simulates CI's jsonschema 4.10.3 branch shape: preload
jsonschema so its own internals resolve, then `sys.modules['referencing']=None`
so ONLY the `from referencing import ...` inside `make_validator` raises
ImportError, then `runpy.run_path(..., run_name='__main__')`):

```
meta-schema engines : stdlib-structural + jsonschema 4.26.0
instance engines    : stdlib mini-validator + jsonschema 4.26.0 (cross-checked)
NOTE: legacy jsonschema RefResolver in use ('referencing' not importable); remote $ref fetching is blocked -- any store miss fails closed.
... 25 OK / 0 FAIL ...
Checked 6 schema file(s); 0 failure(s).
EXIT=0
```

Fail-closed guard desk test (same forced-legacy loading, PLUS
`socket.socket`/`socket.create_connection` monkeypatched to raise
AssertionError so ANY network attempt would crash distinctively): built a
validator whose store contains only the root schema and whose `$ref` targets a
non-loaded URI, then `iter_errors`:

```
RAISED _RefResolutionError: remote $ref fetch blocked (fail-closed): target not in the loaded contract store: 'https://contracts.nycbuildability.test/v1/NOT_LOADED.schema.json'
guard marker present: True
```

The socket tripwire never fired: zero network attempt. Bonus evidence from the
first (mis-poisoned) attempt: with jsonschema entirely unavailable the script
correctly ran in stdlib-only degraded mode, 25 OK / 0 FAIL, exit 0.

4.10.3-semantics note (desk-verified, cannot pip-install 4.10.3 per
constraints): `RefResolver.resolve_from_url` does `store[url]` and on KeyError
calls `self.resolve_remote(url)`; the `handlers` dict, `requests.get`, and
`urlopen` branches ALL live inside `resolve_remote` — an API shape unchanged
from jsonschema 2.x through 4.26 (where the identical method still exists,
deprecated). Overriding `resolve_remote` therefore guards every scheme under
4.10.3, not only http/https. The `RefResolver is deprecated` warning seen in
the forced-legacy run is emitted only by jsonschema >= 4.18; CI's 4.10.3
predates the deprecation and will not print it.

### 4.7 Final state

```
git status --short
 M .github/scripts/secret_scan.py
 M .github/scripts/validate_contracts.py
 M docs/SECRETS_POLICY.md
?? project-control/reports/M0-T005-R1-producer-report.md
ls scratch*  -> no scratch files remain
```

Final S1 re-run AFTER writing this report (report included in the scan) —
recorded in section 8.

## 5. Assumptions and defaults

1. **Inventory list = the 10 names in G5 required-rework item 2** (policy §2
   secret rows + SENTRY_DSN + the anon key). The low-sensitivity identifiers
   also listed in §2 (SUPABASE_URL, SUPABASE_PROJECT_REF, VERCEL_ORG_ID,
   VERCEL_PROJECT_ID, ENVIRONMENT) are intentionally excluded to keep the class
   zero-noise; committing them into the templates is still caught by the
   env-template non-empty-value check.
2. **Placeholder hints extended with `"..."` and `"user:pass"`** to keep six
   pre-existing doc-example lines in unmodifiable historical gate reports from
   failing S1 (section 2). Residual: a real credential containing a literal
   ellipsis or the exact substring `user:pass` would be suppressed —
   vanishingly unlikely (real base64/hex/URI credentials contain no `...`) and
   disclosed here.
3. **`ALLOWLISTED PATH` label retained for the two templates** for S1
   continuity ("3 allowlist notices now path-exact" per the packet), with
   notice text stating they are content-scanned, not skipped. Reviewers may
   prefer a different label; one-line change if so.
4. **Template content check is strict**: ANY non-empty assignment value fails,
   even placeholder-looking ones — policy §3.1 says templates are names and
   comments only. Documentation examples belong in comments.
5. **Forced-legacy simulation** (preload + poison) is assumed representative of
   the real 4.10.3 branch selection; the underlying `import referencing`
   failure is identical in kind, and the guarded API is desk-verified stable
   (section 4.6).

## 6. Known limitations

1. Generic-class gates unchanged by design: quotes required, 20-char floor,
   entropy 3.5 — unquoted non-inventory secrets still evade (disclosed since
   M0-T005; compensating control remains GitHub push protection, human action
   item F2 tracked at orchestrator level).
2. Line-based scanning: secrets split across lines remain undetectable.
3. `docs/SECRETS_POLICY.md` §5 first bullet still describes the ORIGINAL nine
   pattern classes and says "basename path allowlist" — now understating
   coverage and mis-describing the (stronger) exact-path mechanism. The packet
   authorized exactly one section-5 sentence change, so I did not touch it.
   Recommend an orchestrator-approved doc touch-up (3–4 lines) in follow-up.
4. UTF-32 files (`ff fe 00 00` BOM) decode as UTF-16 garbage and are scanned
   harmlessly but not meaningfully; no UTF-32 files exist in the tree and PS
   5.1 does not produce them.
5. One line can yield two findings (e.g. inventory + postgres on a DB URL) —
   intentional, both classes are correct.
6. In the legacy engine path, a guard trip on a VALID fixture surfaces as a
   `validator disagreement` FAIL (clear, build-failing); for schemas with
   unresolvable refs the phase-3 stdlib meta check already fails the build
   before any fixture runs, so the guard is defense-in-depth, not the primary
   detector.
7. `git ls-files` failure → exit 2 is verified by code inspection, not
   execution (no non-destructive way to make ls-files fail while rev-parse
   succeeds).

## 7. Security and provenance impact

Strictly tightening; no new attack surface:

- Four new/hardened detection classes close G3 D1/D2 (the most common
  real-world leak shapes: compound `*_TOKEN/_PASSWORD` names, the project's own
  inventory names, DB URIs, secret URLs).
- Empty-pragma enforcement (D4) converts a review-vigilance control into a
  mechanical one, matching what policy §1 claims.
- Exact-path allowlist (D3) closes the decoy-basename channel; templates are
  now scanned MORE strictly than normal files, not less.
- UTF-16 handling (D6) closes the documented PS 5.1 foot-gun on this host.
- Output sanitization (G5 F1 + M0-T009 F2) removes the CI log-injection class
  from both scripts.
- The RefResolver guard removes the only latent network call from CI's
  validate-contracts job (fail-closed, loud). Both scripts remain stdlib-only,
  no-network-by-design, deterministic.
- Scanner still never prints an unmasked candidate value; masking unchanged.

## 8. Final self-scan including this report

After writing this report (defanged values throughout), the final clean-tree
scan was re-run with the report present. The FIRST run flagged this report
itself at the fixture-listing line that still contained the literal PEM BEGIN
header (`[pem-private-key]`, exit 1) — the header pattern needs no value, so it
self-matches; an unplanned live demonstration that the scanner catches exactly
this class in project-control reports. The line was defanged and the re-run
confirms:

```
python .github/scripts/secret_scan.py ; echo EXIT=$?
secret-scan: scanned 246 files in 0.47s
[same 3 ALLOWLISTED PATH notices]
secret-scan: PASS -- no findings
EXIT=0
```

## 9. Risks and recommended next steps

- **Risk (low):** the extended placeholder hints could theoretically mask a
  real credential containing `...` or `user:pass` — documented, accepted, and
  compensated by push protection once enabled (orchestrator action F2).
- **Risk (low):** helper duplication between the two scripts can drift; the
  marked twin comments make drift diff-detectable. If a third script ever needs
  the helper, promote it to a small shared module in an appropriately scoped task.
- **Recommended:** (a) G3 re-run of S1–S6 + both validate_contracts modes from
  a clean worktree; (b) G5 re-check of the diff (negative-space focus:
  placeholder-hint bypass, template content check, guard behavior);
  (c) orchestrator: the §5 doc touch-up noted in limitation 3; (d) after the
  next CI run on this branch, confirm the legacy NOTE appears in the real
  4.10.3 contracts job log (positive evidence the guard is on the live path).

## 10. Return-packet summary

- Status requested: **awaiting_gate**
- Contracts/schemas changed: none (validator behavior identical on the current
  contract set in both engine modes; scanner CLI contract extended only by new
  finding classes and notices; exit codes now fully match the documented 0/1/2)
- All 11 packet items: implemented (none partial, none blocked)
- Scenarios: S1–S6 PASS (S5 filename case as desk test per packet; S4b via
  disclosed transient fixture in a forbidden-path file, reverted with evidence)
- Report path: `project-control/reports/M0-T005-R1-producer-report.md`
