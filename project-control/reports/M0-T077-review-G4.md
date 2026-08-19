<!-- Orchestrator preservation note (report-preservation rule, 2026-07-16): the review
below was returned through the agent-return channel by the independent read-only
G4 QA reviewer and is saved VERBATIM (transport entity-decoding only). Received
2026-08-19. Verdict: PASS with required corrections - recorded as gate G4 PASS per
the gate-verdict semantics rule; the section-9 corrections are BLOCKING for
acceptance. Everything below this line is the reviewer's text. -->

# G4 Independent QA Verdict — M0-T077 / D-020 (MCP default-deny)

**Anchor: content identity `b0200803184b37b042dc734b092bb51759a52eaf`** (branch head `a861c4d`, which only preserves the G3 confirmation and touches no reviewed artifact — verified: `git diff --name-only b0200803 a861c4d` = `M0-T077-review-G3.md`, `tasks/M0-T077.json`).

All claims verified against blobs extracted with `git archive b0200803 | tar -x` into a scratch tree, so the producer's concurrent commits could not contaminate results. The branch moved four times during my review (`2d8173d → 002ffc3 → d06e805 → a861c4d → f254698`); I re-ran everything the deltas invalidated.

## VERDICT: PASS with required corrections

Recorded as **PASS** per the repo's gate-verdict semantics (`.claude/rules/project-control.md`). The corrections in §4 are **BLOCKING for acceptance**. My earlier blocking finding is **resolved** at this identity — I re-tested it directly and it is closed.

---

## 1. Probe provenance — pre- vs post-correction

`.claude/settings.json` is **byte-identical** (`sha256 fc636b01a022ecdb…`) at `eb742f2`, `90ea22f5`, `9e5c8221`, **and `b0200803`**. Every runtime MCP probe I ran therefore exercised the anchor's policy file, whenever it ran.

| Probe class | Pre-correction | Re-run at `b0200803` |
|---|---|---|
| 6 documented commands | yes | **yes — all six** |
| Root-session `claude mcp list` | yes | **yes (P-7f/P-8f/P-9f)** |
| Validator gap matrix | yes (found BLOCKING-1) | **yes — against the `b0200803` validator blob** |
| Coordinated-weakening probe | yes | **yes** |
| Report fact-checks, digests, diff, secrets | yes | **yes** |
| Subdirectory leak probes | yes (found it independently) | disclosure verified; substance unchanged |

## 2. Documented test commands — exact commands and exit codes at `b0200803`

| # | Command | Exit | Observed |
|---|---|---|---|
| P-1f | `python tools/validate_mcp_policy.py --check` | **0** | silent (pass) |
| P-2f | `python tools/test_mcp_policy.py` | **0** | `Ran 35 tests in 0.193s` / `OK` |
| P-3f | `python tools/validate_directive_compliance.py --check` | **0** | pass |
| P-4f | `python tools/test_project_control.py` | **0** | `all 23 project-control test groups passed` |
| P-5f | `python tools/test_directive_compliance.py` | **0** | `Ran 120 tests in 807.4s` / `OK`, zero FAIL/ERROR |
| P-6f | `python tools/modularity_check.py --check` | **0** | 265 files, 0 failures, 5 pre-existing warnings (none on the new files) |

Frozen blob digests I tested: `validate_mcp_policy.py` = `31bc4171…`, `test_mcp_policy.py` = `2da7ff7e…`, `.claude/settings.json` = `26ab9417…` (archive-normalized).

## 3. Fresh-session proof — independently re-executed

| # | Command / location | Observed | Report claim | Match |
|---|---|---|---|---|
| P-7f | `claude mcp list` in `wt-t077-proof` (root, clean) | `No MCP servers configured.` | Runs A/D | ✅ |
| P-8f | same, after P-7f's process exited | `No MCP servers configured.` | Run B restart-survival | ✅ |
| P-9f | `claude mcp list` in `wt-m0t077` (root) | `No MCP servers configured.` | Run C | ✅ |
| P-10 | `claude mcp list` in `C:\Users\MLFLL\Downloads` (non-repo) | Airtable ✔, M365 ! auth, pencil ✔, supabase ✔ | §3 functional control | ✅ |
| P-11 | policy file alone copied into an empty scratch dir | `No MCP servers configured.` | (my own probe) | portability proven |

Zero mismatches between claimed and observed output anywhere. The report correctly redacts the Supabase project ref that the raw command prints in full.

## 4. Findings

### RESOLVED (was BLOCKING at `9e5c8221`) — incomplete shape guard, now closed

At `9e5c8221` the three-key `p9` enumeration let four silent-void shapes through. I verified the premise myself (`"model": 123` restores all four connectors while the file still parses). At `b0200803` the whole-file `KNOWN_KEY_SHAPES` assertion closes it. Re-test against the frozen `b0200803` validator:

| Mutation (MCP policy keys untouched) | @`9e5c8221` | @`b0200803` | runtime |
|---|---|---|---|
| `"$schema": 42` | passed (exit 0) | **catches (exit 1)** | voids policy |
| `"env": "not-an-object"` | passed | **catches** | voids policy |
| `"cleanupPeriodDays": "thirty"` | passed | **catches** | voids policy |
| `"includeCoAuthoredBy": "yes"` | passed | **catches** | voids policy |
| `"model": 123` | catches | catches | voids policy |
| intact policy (false-positive control) | exit 0 | **exit 0** | held |

I then attacked the new assertion with seven shapes neither G3 nor I had tried — `permissions:{"deny":["mcp__*"],"allow":5}`, `permissions` with a bogus nested key, `permissions.deny` containing an int, a denylist entry with an extra property, `hooks:{"SessionStart":"notalist"}`, `env` with an int value, and a legitimate `outputStyle:"explanatory"`. **All seven caught. Zero false negatives found.**

### MAJOR-1 (open) — coordinated weakening of settings + validator constants passes all 35 tests

Exact test at `b0200803`: removed `supabase` from `deniedMcpServers` and `disabledMcpjsonServers` **and** from `DENIED_SERVER_NAMES`/`DISABLED_MCPJSON_NAMES`. Result: `validate_mcp_policy.py --check` **exit 0**; `test_mcp_policy.py` **Ran 35 / OK / exit 0**. `test_each_denied_identifier_is_required` iterates the validator's own tuple, so shrinking the tuple silently shrinks the test.

Severity is bounded: I measured live effect and the policy still **held** (`No MCP servers configured`) because `allowedMcpServers: []` blocks independently. Actually re-admitting Supabase additionally requires relaxing the `p3` empty-allowlist assertion — a conspicuous code edit. Only PR diff review catches this class; no automated layer does. Fix: pin the audited identifiers independently of the validator's own constants.

### MAJOR-2 (open) — nothing asserts the CI steps exist

At `b0200803`, `grep -rl validate_mcp_policy --include=*.py --include=*.yml` returns exactly three files: `.github/workflows/ci.yml`, `tools/test_mcp_policy.py`, `tools/validate_mcp_policy.py`. Deleting the two `ci.yml` steps disables the entire durable validation and **no test fails**. Answering the charter question honestly: **no**, nothing asserts the step exists. It is visible in the PR diff and `.github/workflows/**` routes to review via `tools/agent_supervisor/policy.py:356`, but that is human review, not machine enforcement. G3's probe 42 checked step presence at review time — point-in-time, not durable.

### MINOR (open) — three stale factual claims, all still present at `b0200803`

- `docs/MCP_DEFAULT_DENY_POLICY.md:20` — "five additive keys"; there are **six** (the table immediately below correctly lists six, and the PR body already says six).
- `M0-T077-fresh-session-proof.md:100` — anchors its additive-diff claim to intermediate commit `a2bee92` and "the five policy keys", not the reviewed identity. The stronger claim holds: `31c50a09..b0200803` is `19 / 0`.
- `M0-T077-submission.md:40` — claims `+24 lines` for `.claude/settings.json`; actual is **`+19 / -0`**.

### INFO — probes that came back clean

- **`settings.local.json` cannot weaken the policy.** A local-scope override setting `disableClaudeAiConnectors:false`, allowlisting pencil+supabase, `enabledMcpjsonServers:["supabase"]`, and `enableAllProjectMcpServers:true` all at once left the roster empty. (Also gitignored at `.gitignore:64`, absent from the worktree.)
- **A new unaudited `.mcp.json` server is blocked** by the empty allowlist, even with that permissive override in place.
- **JSON duplicate keys do not diverge** — Python and Claude Code both resolve last-wins, so validator and runtime agree. No parser-divergence gap.
- **Deny-beats-allow confirmed independently**: with both allowlisted, `pencil` (still denylisted) stayed blocked while `supabase` (de-denylisted) connected — the documented precedence is real.
- **F-3 fix verified**: the echo-decoy where hook filenames appear only inside an inert command is correctly rejected by `p7`.
- **New assertion is deliberately over-strict** — it rejects `outputStyle:"explanatory"`, a nested `permissions` key, and `env` with an int value, all of which the runtime tolerates. Fail-closed by design and documented as intended visibility; worth an explicit sign-off rather than passing unnoticed, since adding any legitimate new setting will now fail CI until `KNOWN_KEY_SHAPES` is extended.
- **Private absolute paths** appear in five added lines across `source-001.md` (the owner's own verbatim text, immutable), `tasks/M0-T077.json` (`"worktree"` — a convention that predates this task; `M0-T076` carries it at base), and `review-G3.md`. Consistent with prior accepted packets, already disclosed by G3; not a regression.

## 5. Test-gap analysis (charter item 4)

| Weakening a future edit could make | Validator @`b0200803` | Other layer that catches it |
|---|---|---|
| Any policy key removed / wrong value | **caught** (p2–p6, p8) | — |
| Settings file deleted, renamed, unparseable | **caught** (p1) | — |
| Wholesale replacement (merge violated) | **caught** (p7) | — |
| Hook registration dropped, or decoyed by substring | **caught** (p7, path-anchored) | hook test suites in same job |
| Any key with a schema-invalid type (silent whole-file discard) | **caught** (p9 whole-file) | — |
| Key at wrong nesting level | **caught** (top-level `.get`) | — |
| JSON duplicate keys | not applicable — no parser divergence | — |
| `settings.local.json` override | not read by validator | **empirically cannot weaken** (probed) |
| New `.mcp.json` server not in `disabledMcpjsonServers` | not checked | **empty allowlist blocks it** (probed) |
| Audited identifier dropped from settings **and** validator constants | **NOT caught** | PR diff review only → **MAJOR-1** |
| The two `ci.yml` steps deleted | **NOT caught** | PR diff review + workflow review routing → **MAJOR-2** |

## 6. Acceptance scenarios AS-1..AS-8 — my own evidence

| | Verdict | My basis |
|---|---|---|
| **AS-1** | **PASS** | P-7f/P-9f/P-11 at worktree root. Subdirectory case is a disclosed limitation, correctly scoped — not an AS-1 failure as written |
| **AS-2** | **PASS** | Two distinct clean worktrees, repeated across a process exit, identical output |
| **AS-3** | **PASS — all five rows** | Recomputed both file digests (`1fc898cc6935…`, `a738fcfa9573…`) **and reproduced all three structural digests** (`7500a3e4dad6…`, `c838ec230a5b…`, `e2f8bdbc3b6f…`) via `json.dumps(sub, sort_keys=True)`. Re-hashed after all probing: unchanged. Non-repo control retains all connectors |
| **AS-4** | **PASS** | `git diff --numstat 31c50a09 b0200803 -- .claude/settings.json` = `19 0`; every pre-existing key present; `p7` pins it permanently |
| **AS-5** | **PASS** | Every weakening AS-5 enumerates exits 1; intact policy exits 0 |
| **AS-6** | **PASS** | Cited lines verified exact at `b0200803` (`cli.py:2687`, `turnover_adapters.py:404-412`, `preflight.py:91`, `claude_runner.py:1085`); grep for `--settings`/`--mcp-config`/`--strict-mcp-config`/`mcpServers` in `tools/agent_supervisor/`: **no matches**; no supervisor file modified. Live supervised probe honestly recorded as owner-gated and not performed |
| **AS-7** | **PASS** | One pattern hit is a **false positive** — the literal strings `sb_`/`sbp_` inside the G3 reviewer's prose *describing* its own scan patterns. No credential, token, JWT, or full project ref in added content |
| **AS-8** | **PASS** | PR **#240 OPEN**, `mergedAt: null`. D-013 untouched (0 files in diff); no forbidden path touched — `agent_supervisor`, `model_routing`, `model_selection`, `ORCHESTRATION_POLICY`, `.claude/{hooks,agents,skills,rules}/`, `.mcp.json`, `apps/`, `services/`, `packages/`, `supabase/`, and the protected workflows are all absent from the diff |

## 7. Not-testable items

- **Live end-to-end supervised worker launch** asserting an empty MCP roster from inside a worker session — owner-present-only under standing D-018/D-019 boundaries. The static call-path trace plus same-cwd fresh-process resolution is the strongest available substitute, and the producer records this honestly.
- **"Usable `mcp__supabase*` tools in the subdirectory case"** (cited from G3 probes 40/41) — I deliberately invoked **no** MCP tool, per D-020-R010. I verified the load-bearing part (the servers connect) and confirmed G3's probes are documented with method and results.
- **A true interactive session restart of the orchestrator session** — cannot be self-verified from inside it; the fresh-process runs are the documented smallest safe equivalent.

## 8. No test weakened, removed, or skipped

`git diff --name-status 31c50a09 b0200803` shows exactly four modified files — `.claude/settings.json`, `.github/workflows/ci.yml`, `project-control/directives/index.json`, `project-control/state.json` — and **no deletions or renames**. No existing test file is modified. `ci.yml` is `+10 / -0`. `index.json` is semantically additive: all 19 prior directive entries byte-identical in content and order, `D-020` appended, only `updated_at` changed (its 303 deleted lines are pure reformatting). Evidence map: 23 of 34 requirements mapped, **every listed file exists**; the 11 unmapped (`R001–R004`, `R009–R015`) are process/prohibition/return obligations I verified through the diff and PR state instead.

I made no repository edits and ran no write commands; both worktrees show **zero** modifications attributable to me, and my scratch probe directories are cleaned up.

## 9. Required corrections (blocking for acceptance)

1. **MAJOR-1** — pin the audited identifier list independently of `DENIED_SERVER_NAMES`/`DISABLED_MCPJSON_NAMES` so a coordinated edit cannot shrink both the policy and its own test in one pass.
2. **MAJOR-2** — add an assertion that the two `ci.yml` steps exist (a few lines of YAML parsing in `test_mcp_policy.py` closes it).
3. **MINOR** — fix "five additive keys" → six (`docs/MCP_DEFAULT_DENY_POLICY.md:20`), `+24 lines` → `+19 / -0` (`M0-T077-submission.md:40`), and re-anchor the §4 additive-diff claim off `a2bee92` (`M0-T077-fresh-session-proof.md:100`).
4. **Sign-off item, not a defect** — explicitly accept the new validator's unknown-key strictness, since it will block any legitimate future settings addition until `KNOWN_KEY_SHAPES` is extended in the same reviewed change.

**Note on live state:** the branch has since advanced to `f254698` with G5 work in flight (subagent connector inheritance). That is outside my anchor and G5's domain; my verdict is against `b0200803` as instructed.

Paths: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t077\tools\validate_mcp_policy.py`, `...\tools\test_mcp_policy.py`, `...\.claude\settings.json`, `...\.github\workflows\ci.yml`, `...\docs\MCP_DEFAULT_DENY_POLICY.md`, `...\project-control\reports\M0-T077-fresh-session-proof.md`, `...\project-control\reports\M0-T077-submission.md`.
