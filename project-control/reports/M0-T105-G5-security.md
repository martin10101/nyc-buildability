# M0-T105 G5 security review — round 1 (VERBATIM reviewer return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Reviewer: security-reviewer
(independent, read-only, dispatched 2026-08-27). Verdict returned: **PASS** — no blocking
corrections; four non-blocking findings (1 LOW, 3 ADVISORY).

---

# G5 Security Gate Report — M0-T105 (D-024 Amendment 3 unit D: native event integration)

**Reviewer:** security-reviewer (independent, read-only)
**Task:** M0-T105 — durable hook event bus, stream-JSON subagent ingestion, dedup, redaction, replay, drift
**Frozen identity:** branch `control/D-024-fable-codex-loop`; live HEAD `70b38f87d5ded0988c84022b463d98ca35db1471`; deliverable commit `50abb346fc8637a374b1e5bae056d19d2792a827`; checkpoint content_manifest_sha256 `5f32cf98…e812b17`
**Applicable requirements:** D-024-R154, D-024-R155, D-024-R173
**Repo visibility:** PUBLIC
**Verdict:** **PASS** — no blocking corrections. Four non-blocking findings (1 LOW, 3 ADVISORY) recorded for a follow-up hardening task.

---

## 1. Scope and method

Reviewed every new byte at the deliverable commit: `tools/agent_supervisor/event_bus.py` (284), `event_stream.py` (234), `event_drift.py` (106); `.claude/hooks/supervisor_event_recorder.py` (77); the three fixtures; and `tools/test_agent_supervisor_event_bus.py` (463). Re-derived the sanitize-first pipeline through the REUSED `telemetry_journal.py`, `telemetry_redaction.py`, `telemetry_hooks.py`, `telemetry_records.py`, `redaction.py`. Independently reproduced the test pack and probed the masking boundary in-memory. Did not rely on producer conclusions.

Reproductions run (read-only):
- `python -m pytest tools/test_agent_supervisor_event_bus.py -q` → **32 passed in 1.30s** (independently reproduced).
- `git diff --stat 50abb346^..50abb346 -- .claude/hooks/readonly_agent_guard.py .claude/hooks/agent_dispatch_guard.py` → **empty (EXIT 0)**: both guard packs byte-untouched.
- `git show --stat 50abb346` → 13 files; `.claude/settings.json` **not** among them; no dependency manifest (requirements/pyproject/package.json) touched.
- Network/injection grep over the four new modules → **no** `urllib/requests/socket/http/subprocess/eval/exec/os.system/__import__`.
- Leak scan over all new files → only benign test needles (see §4).

---

## 2. Security-dimension findings

### 2.1 Prompt-injection posture / nothing-executed (R154/R155) — PASS
- **No execution of payload content anywhere.** No `eval`/`exec`/`os.system`/`subprocess`/format-into-command in any of the four new modules. Payloads are `json.loads`'d data, traversed only for hashing (`idempotency_key`, `stream_idempotency_key`) and whitelist extraction. Event names reach only dict keys and `type()`-name f-strings, never a shell or command.
- **Nothing reaches model context.** The recorder prints **nothing** to stdout (verified in source and by `test_s9_recorder_records_and_stays_silent`), so it cannot emit `additionalContext`/`permissionDecision`. `event_stream.py` has **no** sidecar/model-message surface (`test_s3_statusline_sidecar_stays_primary` asserts `TelemetrySidecar` absent from the source). The stream module is passive parsing only.
- **Prompts are dropped, not merely withheld.** `ingest_hook_event` copies only the `_EVENT_ATTRIBUTES` whitelist; the `prompt` field is **not** whitelisted, so it never reaches the record at all. Prompt-like *keys* that do survive elsewhere are digest-withheld wholesale by `sanitize_structure` (incl. nested lists/dicts, the M0-T088 G4-Adv2 fix). `test_s4_durable_record_sanitized` confirms prompt text absent.
- **Secrets/paths.** Every stored string passes `sanitize_structure` → `redact_text` (11 credential patterns + assigned-secret) and `redact_user_paths` (`[HOME]` for slash and dash-encoded forms). Sensitive-key values masked wholesale. Terminal escapes stripped.

### 2.2 Recorder attack surface (R155) — PASS
- **Stdin bomb cap math correct.** `raw = sys.stdin.read(MAX_STDIN_BYTES + 1)`; `if len(raw) > MAX_STDIN_BYTES: return 0`. Exactly-1 MiB passes, ≥1 MiB+1 rejected with nothing recorded. Cap is on characters (text mode), still hard-bounded.
- **sys.path bootstrap is soundly anchored.** `_REPO_ROOT = Path(__file__).resolve().parents[2]` inserted at `sys.path[0]`, so the repo's real `tools/` package wins over any lower-priority shadow. `resolve()` defeats symlink/relative tricks. Import occurs only *after* `payload` is validated as a dict with a non-empty string `hook_event_name`.
- **Path traversal / symlink via `NYCB_EVENT_STORE_PATH`** — see ADVISORY-1. Within threat model (env is not payload-controlled).
- **Fail-closed swallowing** — see ADVISORY-3. Correct session-safety trade; this journal is explicitly *not* the tamper-evident log (`audit_log.py` holds the hash chain).

### 2.3 Leak analysis (PUBLIC repo) — PASS
- Store `.claude/telemetry/` is **gitignored** (`.gitignore:89`) and **untracked** (`git ls-files` empty). The durable store never reaches git.
- Byte scan of all new files: the only hits are inside the **test file** — `MLFLL` (×2) are leak-needle *assertion strings* (`assert "MLFLL" not in whole`), the single full UUID is the `# synthetic` `SESSION_UUID` constant used to *prove* masking, and `sk-ant-fake…` / `/home/realname` are synthetic S4 inputs asserted to be redacted. Production modules and all three fixtures are clean (fixtures use `[SESSION-D-FIXTURE]`, `[HOME]`, `[UUID]`, `[PROJECT]`). No usernames, real session UUIDs, tokens, or emails in shipped code/fixtures.
- **S4 masking to the durable store** — real session/task/prompt UUIDs arrive as top-level string fields and are digest-masked (`_mask_if_uuid`) before the journal write; `transcript_path` (which embeds the session UUID in its filename) is **not** whitelisted and is dropped entirely. Nested-structure gap: see LOW-1.

### 2.4 Denial / abuse — PASS (with ADVISORY-2)
- Bounded on every axis: stdin 1 MiB; `_seen` capped at `max_seen_keys` (4096 default, LRU-evicted, `test_s10_seen_keys_bounded`); `SubagentRegistry` capped at 512 (closed-first eviction); journal byte-bounded + generation-rotated (`test_s10_journal_rotation_bounds_disk`); per-record byte cap raises `TelemetryBoundsError`. No unbounded growth vector found.
- No crash-loop: recorder always `exit 0`.
- Per-event replay cost — ADVISORY-2.

### 2.5 Authority boundaries — PASS
- Recorder never blocks/gates/injects (no `permissionDecision`/`additionalContext` in code; `test_s11` asserts). Always exits 0.
- **No `.claude/settings.json` registration** in the change (confirmed absent from the commit file list). Committing the recorder activates nothing.
- **`readonly_agent_guard.py` and `agent_dispatch_guard.py` byte-untouched** at the deliverable commit (empty diff against parent).
- **No new dependencies**: recorder imports `json/os/pathlib/sys` + the existing sibling `event_bus`; the three modules import only stdlib + existing telemetry siblings. No manifest changed.
- **Amendment-3 prohibitions respected**: no MCP, no SDK admission, no bypass/`dangerously` flags anywhere (grep clean; the only `mcp`/`forward-subagent` strings are docstrings describing what is parsed). The S8 live tooth runs `claude --version` via a `shutil.which`-resolved absolute path, list-form `subprocess`, no shell.

### 2.6 C1 owner-gated canary — PASS
- No committed artifact launches or enables C1. The recorder is unregistered; no auto-run script exists; the only live code path is the S8 version tooth (`claude --version`, read-only, skips when absent). The canary is prose-only in the report, queued for owner exact-command (R192/R197).

### 2.7 Cross-tenant isolation / service-role secrecy / private storage / SSRF — NOT APPLICABLE
- This change introduces no Supabase/DB access, no storage buckets, no HTTP client/server, and no service-role credential handling. No new SSRF surface (zero outbound network). Nothing to violate; no new attack surface in these categories.

---

## 3. Findings (all NON-BLOCKING)

**LOW-1 — Nested-UUID masking gap contradicts the stated S4 invariant (contained by gitignore).**
`event_bus._store` masks UUIDs only at the top level: it walks `attributes` one level deep (`_mask_if_uuid(value)`) plus the record's own `session_id`/`task_id`. The journal-level `sanitize_structure` recurses but masks paths/secrets/prompts/escapes — **not** UUIDs. So a UUID nested inside a whitelisted attribute value (supplied as a dict/list) reaches the durable store raw. Reproduction (in-memory, read-only):
```
payload = {'hook_event_name':'SubagentStart','session_id':REAL,'agent_id':{'x':REAL},'model':['p',REAL]}
→ top-level session_id masked: True
→ nested agent_id.x survives:  True   (stored as {'x':'0a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d'})
→ nested model[1] survives:    True
```
Why non-blocking: (a) the store is gitignored/runtime-local and never committed; (b) genuine session/task/prompt UUIDs arrive as top-level strings and **are** masked, and `transcript_path` is dropped — so the *real* session identity is not exposed; (c) the nested vector requires attacker-shaped payloads, where the UUID is attacker-chosen, not the real correlation identity; (d) secrets/paths/prompts nested in the same structures **are** still redacted (only bare UUIDs slip). Remediation (recommend for follow-up): fold UUID digest-masking into the recursive `sanitize_structure` walk (or make the bus mask recursively), **or** narrow the `event_bus.py` docstring claim from "raw session/task UUIDs never reach the durable store" to "top-level identity fields," so the code and the stated invariant agree.

**ADVISORY-1 — `NYCB_EVENT_STORE_PATH` is honored in production without validation.**
`_store_path()` returns any env-provided path verbatim; the "test-only" designation is documentation, not enforcement. A hostile env value could redirect writes to any user-writable location (append-only, sanitized JSONL — no arbitrary content, no code exec). Acceptable within the accepted threat model (hooks run as the user; env is not payload/attacker-web-controlled), but recommend either documenting the trust boundary or constraining the override to resolve under an allowed root.

**ADVISORY-2 — O(n) per-event replay may erode the "hooks stay fast" claim.**
Each recorder invocation constructs a fresh `DurableEventBus`, which replays the active journal (`warm_rotated=False`, so bounded to `max_bytes` ≤ 4 MiB) to rebuild the dedup set + registry, then publishes one event. As the active file fills, each event pays a full re-parse (O(active-file-size) per event). Bounded and non-fatal, but latency grows toward the rotation boundary. Recommend a smaller hook-store `max_bytes` or a lighter persisted dedup index if hook latency is observed.

**ADVISORY-3 — Total exception swallowing = silent telemetry loss on persistent write failure.**
The recorder's top-level `except Exception: code = 0` (and the bus re-raise it catches) means a durable-store failure records nothing and surfaces nothing. This is the correct trade for a passive observer (session-safety > telemetry completeness) and consistent with this journal being explicitly non-tamper-evident. Noted for completeness; no change required.

---

## 4. Requirement coverage (security aspects)

- **D-024-R154** (stream ingestion outside Fable context; statusLine sidecar primary; typed errors): PASS — no sidecar/model surface in `event_stream.py`; malformed lines raise typed `StreamEventError`; usage carries R042 labels and the R043 `final_request_*` caveat; forwarded text stored as digest reference only.
- **D-024-R155** (hooks fast/deterministic/sanitized/bounded/fail-closed; external state only; never block/inject/message): PASS with ADVISORY-2 (fast) — recorder is external-state-only, silent, fail-closed, bounded; sanitize-first atomic journal reused.
- **D-024-R173** (unknown-event/version-drift honest handling): PASS — unknown hook events `known:false`, unknown stream types `known_type:false`, drift tooth (`catalog_drift` + fixture + live version check) surfaces divergence, never guesses.

(Full requirement-by-requirement directive verification is the `directive-compliance-verifier`'s pass recorded in `verification.json`; the above covers only the security-relevant slices in this gate's scope.)

---

## 5. Verdict

**PASS.** All critical security properties hold: no network surface, no committed secrets, no payload execution/injection, prompts dropped and secrets/paths masked before the gitignored store, fully bounded resources, fail-closed recorder, guards and settings untouched, no new deps, no MCP/SDK/bypass, and the C1 canary neither launched nor enabled. The one LOW finding is a defense-in-depth/documentation-accuracy gap contained by the gitignored runtime store and by the fact that real session identities are masked; it and the three advisories are recommended for a follow-up hardening task and are **not blocking** for acceptance.

Relevant absolute paths:
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\event_bus.py` (LOW-1: `_store`/`_mask_if_uuid`, lines 69-73, 210-237)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\event_stream.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\event_drift.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.claude\hooks\supervisor_event_recorder.py` (ADVISORY-1: `_store_path`, lines 46-48; ADVISORY-3: lines 73-77)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\telemetry_redaction.py` (sanitize pipeline; no UUID pass — LOW-1 root)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_event_bus.py`
- Fixtures under `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\`
