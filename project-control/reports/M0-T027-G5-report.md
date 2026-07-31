# M0-T027 — G5 security/privacy gate (VERBATIM reviewer return)

**Orchestrator header (NOT part of the reviewer's return).** Dispatched read-only against frozen
identity `3ed05fda6d434670e5b610e6dad7a8b224a9aa94` on branch
`task/M0-T027-closeout-phases-3-4`. Agent type `security-reviewer`, spawn name `m0t027-g5`.
Model value passed at spawn: **explicit Opus 5** under the still-active temporary availability
exception (D-004-R307); the reviewer independently discloses its actual model below and it matches.
No Fable 5 is claimed for this wave. Everything from the horizontal rule to the end of this file is
the reviewer's return preserved **verbatim** (D-004-R385/R468); the orchestrator altered nothing **except for the R024 redactions enumerated immediately below**.

**R024 EVIDENCE-HYGIENE REDACTION (applied 2026-07-30, owner amendment 13 / `source-014`,
D-004-R553-R559).** The independent second-pass verification ruled **D-004-R024 VIOLATED** by this
file: the reviewer's return, preserved as delivered, carried machine-specific data into a public
repository. R024 forbids "session IDs, pane IDs, absolute user paths, and all machine-specific
data" in anything written to the repository. The orchestrator — not the reviewer — owned the
redaction duty at preservation time and did not discharge it before commit `f301421`. The following
substitutions were applied to this file, using D-004's own native convention already used in
`AGENT-TEAMS-PILOT-1.md` (`<REDACTED-USER>`) and `AGENT-TEAMS-PILOT-2-PROBE.md` (`<REPO>`):

| occurrences | substitution |
|---|---|
| 16 | absolute repository path -> `<REPO>` |
| 2 | session id -> `<REDACTED-SESSION-ID>` |
| 1 | bare machine username -> `<REDACTED-USER>` |

**Nothing else changed.** No verdict, finding, defect, severity, requirement ruling, SHA, digest,
count, line reference, or command output was altered, and no text was added to or removed from the
reviewer's return beyond these substitutions. **One precision, added by owner instruction
(D-004-R583) after an independent verifier noted it:** two of the substitutions above fall inside
fenced command blocks, so those command **strings** are no longer executable-as-printed. No command
**output** was altered, and no finding rests on re-running them. The return remains verbatim in every respect except
the redaction tokens themselves, which are visible rather than silent so the preservation stays
honest and auditable.


---

# Gate Report

- **Gate ID:** G5
- **Task ID:** M0-T027
- **Reviewer:** security-reviewer (agent identity `m0t027-g5`, spawned from `.claude/agents/security-reviewer.md`)
- **Producer:** orchestrator
- **Result: PASS**
- **Model actually running as (honest disclosure, D-004-R466):** Claude **Opus 5 (1M context)**, exact model id `claude-opus-5[1m]`. This is Opus 5, not Fable 5, and I make no claim to be Fable 5. It is consistent with the owner's amendment-8 Opus-5 exception (D-004-R307) carried forward in source-012 Phase 4 step 5.
- **Clean environment/worktree used:** Primary checkout, branch `task/M0-T027-closeout-phases-3-4`. My own first action:

```
$ git rev-parse HEAD
3ed05fda6d434670e5b610e6dad7a8b224a9aa94
$ git rev-parse --abbrev-ref HEAD
task/M0-T027-closeout-phases-3-4
```

**HEAD matches the frozen reviewed identity `3ed05fda6d434670e5b610e6dad7a8b224a9aa94` exactly (40/40 characters).** I explicitly invoked the `/run-quality-gate` skill for this review.

My read-only discipline was enforced by the harness, not merely self-imposed: three of my commands were denied by `readonly_agent_guard.py` with the verbatim text `'m0t027-g5' is operationally read-only: repository/GitHub/control-plane mutation and shell file-writes are blocked. Read-only git inspection, gh reads, and test execution are allowed; return findings via SendMessage.` I created, edited, and deleted nothing.

**Sandbox refusals and the substitute routes I used (named, not omitted):**
1. `git log --format="%H%n author=%an <%ae>..."` — denied; the guard's heuristic fires on literal `<`/`>` characters (redirection detection). **Substitute:** `git log -n 5 --pretty=fuller main..HEAD`, which returned full author/committer/date metadata. No loss of coverage.
2. Two Python one-liners containing `>=421` and a `'=>'` string literal — denied for the same reason. **Substitute:** rewrote using `int(...).__ge__(421)` and the word `BECOMES` in place of the arrow. Both checks ran to completion.
3. `grep -rn "npm ci\|npm install\|ignore-scripts" .github/workflows/` — denied (package-install string heuristic). **Substitute:** the `Grep` tool over `.github/workflows`, which returned the same lines with line numbers.

No check was skipped because of a refusal.

---

## Scope statement — what security surface actually exists here

I am required to say plainly whether the security matters in my standard checklist apply. **They largely do not, and I did not invent findings to fill them.**

The complete changed-file set is seven files, all under `project-control/`:

```
$ git diff --name-status main...HEAD
M	project-control/directives/D-004-agent-teams-runtime-adoption/manifest.json
M	project-control/directives/D-004-agent-teams-runtime-adoption/requirements.json
A	project-control/directives/D-004-agent-teams-runtime-adoption/source-012-amendment.md
M	project-control/reports/M0-T027-evidence-map.json
M	project-control/reports/M0-T027-producer-report.md
M	project-control/state.json
M	project-control/tasks/M0-T027.json

$ git diff --stat main...HEAD
 7 files changed, 4508 insertions(+), 20 deletions(-)

$ git merge-base main HEAD
11f3540c602849f4100517f35b7b93eca6742a8d

$ git log --oneline main..HEAD
3ed05fd M0-T027 Phase 4: closeout evidence frozen (resolver-derived 233-id evidence map)
1bb811e M0-T027 Phase 3: roster correction + AS-1/AS-6 truth-preserving clarifications
abef119 D-004 amendment 11 (R421-R516): GO to execute M0-T027 Phases 3 and 4
```

There is **no authentication code, no RLS policy, no Supabase table or storage bucket, no upload path, no HTTP client or outbound request, no SQL, no template rendering, no user input handling, and no deployment definition** in this diff. Consequently: cross-tenant isolation, service-role secrecy, private-storage configuration, SSRF, injection, and upload controls are **not applicable** to this changeset and I make no claim about them. The applicable surfaces are exactly the six named in my task: evidence hygiene / data leakage, secrets, integrity controls, control-plane privilege, gate integrity, and dependencies. Those I examined in full.

---

## Acceptance criteria reviewed

I reviewed the security-bearing acceptance scenarios. AS-2/AS-3/AS-4/AS-7/AS-8 are lifecycle and reviewer-conduct scenarios owned by the control-plane and code reviewers; I do not rule on them.

| Scenario | Security-relevant aspect I ruled on | Verdict |
|---|---|---|
| AS-1 (as clarified) | Registry digests re-derived correctly; no directive history altered/deleted/renumbered/rewritten; validator exit 0 | PASS |
| AS-5 | Evidence hygiene — no session ids, pane ids, absolute user paths, or machine-specific data in any added file | PASS |
| AS-6 (as clarified) | The historical FAILURE is preserved, not rewritten as a pass; `AGENT-TEAMS-PILOT-1.md` byte-unchanged on this branch | PASS |
| AS-9 | Containment — no effort key, `M0-T025.json` unmodified, no escape from authorized paths | PASS |
| AS-10 | No unrelated ledger/product state changed | PASS |

---

## Directive/requirement verification

I ruled individually on the **security- and integrity-bearing** subset of D-004 requirements at content identity `3ed05fda6d434670e5b610e6dad7a8b224a9aa94`. I did **not** rule on all 233 resolver-derived applicable requirements — that complete ruling is the `directive-compliance-verifier`'s job and belongs in `verification.json` (which correctly does not yet contain an `M0-T027` entry; the producer did not pre-write its own verification). I am reporting my actual coverage, not inflating it.

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-004-R377 | 3ed05fda | PASS | `requirements.json` main→HEAD: 420→516 rows, **0 deleted, 0 modified**, order of first 420 preserved (set/JSON comparison, below) |
| D-004-R424 | 3ed05fda | PASS | `reviewer_agents` now contains `security-reviewer`; `required_gates` include G5 unchanged |
| D-004-R425 | 3ed05fda | PASS | Exactly one addition. Packet diff hunk shows `+    "security-reviewer"` and nothing else added to the roster |
| D-004-R426 | 3ed05fda | PASS | `producer_agent` = `orchestrator` (unchanged), `required_gates` = `["G0","G2","G3","G5"]` (unchanged), all three pre-existing reviewer identities present and unmodified |
| D-004-R427 | 3ed05fda | PASS | Correction recorded in the `PHASE 3` `progress_log` entry with mechanical rationale; `reviewer_agents` confirmed absent from `MATERIAL_FIELDS` at `tools/directive_registry.py:814-816` |
| D-004-R428 | 3ed05fda | PASS | No substitute reviewer was used; the three prior reviewers remain and `security-reviewer` was added, not swapped in |
| D-004-R429 | 3ed05fda | PASS | `git log --follow -- project-control/gates/M0-T027-G0.json` = exactly one commit (`0361491`). Blob id `b542f03ee17ae18e947d87daea4213deb32539c5` **identical at `0361491`, `main`, and `HEAD`**. Not overwritten, recreated, or backdated |
| D-004-R430 | 3ed05fda | PASS | G0 record is `role: administrative`, `reviewer: orchestrator`, `result: PASS`. `gate()` classifies G0 in `ADMINISTRATIVE_GATES` (`tools/project_control.py:116`) and reserves it to the orchestrator — the stored record is lawful under the write-time contract |
| D-004-R431 | 3ed05fda | PASS (not triggered) | No replacement G0 is required; the stop-and-report condition did not arise |
| D-004-R438 | 3ed05fda | PASS | AS-1 text requires "no prior directive history is altered, deleted, renumbered, or rewritten"; independently confirmed true of the actual registry |
| D-004-R448 | 3ed05fda | PASS | Packet diff is exactly four changes: AS-1, AS-6, `reviewer_agents`, plus lifecycle fields (`status`, `progress_percent`, `updated_at`, `progress_log`). No other material field moved |
| D-004-R449 | 3ed05fda | PASS | No pilot report, no committed `source-00[1-11]-amendment.md`, no locked requirement row, and no prior gate record appears in `git diff --name-only main...HEAD` |
| D-004-R450 | 3ed05fda | PASS | Digest movement `dc5d2979…` → `d6afb9d7…` recorded in producer report §13.4 and in the `PHASE 3` progress-log entry, with the `_legacy_grandfather_check`-only consumer analysis |
| D-004-R451 | 3ed05fda | PASS | All new timestamps are 2026-07-30T19:2x/19:3x, later than every prior entry; no timestamp precedes its predecessor |
| D-004-R453 | 3ed05fda | PASS (consistent; see limitation) | `invalid_unblock_roster()` returns `None` for this packet — I ran it myself. `state.json` moved `M0-T027` from `blocked_tasks` to `active_tasks`, which is `sync_state()` behavior, not a task-file hand edit. See "what I could not verify" |
| D-004-R455 | 3ed05fda | PASS | I re-ran `directive_registry.load_registry().evaluate_task_refs(packet)` myself: **233 applicable ids, `ok: True`, `reasons: []`** — matches the map exactly |
| D-004-R457 | 3ed05fda | PASS | Derived count 233 is neither 128 nor 420 nor 516; no previously reported number was assumed |
| D-004-R477 | 3ed05fda | PASS | Changed-file set is the seven paths above and nothing else |
| D-004-R478 | 3ed05fda | PASS | No unrelated task packet and no product file changed |
| D-004-R492 | 3ed05fda | PASS | `project-control/tasks/M0-T025.json` absent from the diff; status still `backlog` |
| D-004-R497 | 3ed05fda | PASS | No `effort`/`effortLevel` key added anywhere. `git grep -nE '"?effort(Level)?"?\s*:' HEAD -- .claude/settings.json .claude/settings.local.json` → **exit 1 (no match)**. Every occurrence of the word "effort" in added lines is prohibition text |
| D-004-R498 | 3ed05fda | PASS | `git diff --name-only main...HEAD -- tools .claude .github CLAUDE.md` → **empty** |
| D-004-R515 | 3ed05fda | PASS | Old map count independently measured at 128 rows; new map rebuilt to 233. The stale count was not preserved |

---

## Steps independently executed

### 1. Working-tree delta — disclosure verified, not accepted

The disclosed delta was three lifecycle items. I verified it and found the disclosure **accurate for all tracked/ledger paths**, with one honest qualification.

```
$ git status --porcelain
 M .claude/agent-memory/backend-engineer/env-producer-sandbox-no-exec.md
 M project-control/state.json
 M project-control/tasks/M0-T027.json
?? .claude/CODEX_CLAUDE_SUPERVISOR_BUILD_DIRECTIVE_v4 (1).md
?? .claude/agent-memory/…  (30 untracked agent-memory files)
?? .npmrc
?? project-control/gates/M0-T027-G2.json
```

The three disclosed items are present and are the only **ledger** deltas. The remaining entries are pre-existing untracked `.claude/agent-memory/**` files (an explicitly non-authoritative, agent-writable tree per `.claude/rules/project-control.md`), an untracked root `.npmrc`, and an untracked stray doc — all present at session start and **none of them committed or staged**. Not a disclosure failure, but recorded so the delta is fully accounted for.

The uncommitted content delta is exactly two timestamps:

```
$ git diff HEAD -- project-control/state.json project-control/tasks/M0-T027.json
-  "updated_at": "2026-07-30T19:23:23.474515+00:00"
+  "updated_at": "2026-07-30T19:33:47.556123+00:00"
-  "updated_at": "2026-07-30T19:23:23.381489+00:00",
+  "updated_at": "2026-07-30T19:33:47.467362+00:00",
```

Plus the new `project-control/gates/M0-T027-G2.json`:

```
{
  "task_id": "M0-T027",
  "gate_id": "G2",
  "reviewer": "orchestrator",
  "role": "self_check",
  "result": "PASS",
  "report_file": "project-control/reports/M0-T027-producer-report.md",
  "reviewed_at": "2026-07-30T19:33:47.172167+00:00",
  "content_manifest_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "reviewed_sha": "3ed05fda6d434670e5b610e6dad7a8b224a9aa94",
  "updated_at": "2026-07-30T19:33:47.461360+00:00"
}
```

This is CLI-shaped and lawful: `G2 ∈ SELF_CHECK_GATES` and `gate()` requires the reviewer to be `orchestrator` for that class (`tools/project_control.py:869-874`). A G2 self-check **cannot** substitute for an independent gate — the code comment and the `role` field both say so.

### 2. Evidence hygiene / data leakage (public repository) — CLEAN

Scans over every added line of `git diff main...HEAD`:

```
# absolute user paths / home directories
$ git diff main...HEAD | grep -E '^\+' | grep -inE 'C:\\Users|C:/Users|/home/[a-z]|/Users/[A-Za-z]|%USERPROFILE%|\$HOME'
(no matches)

# session ids, pane ids, machine usernames, hostnames
$ git diff main...HEAD | grep -E '^\+' | grep -inE 'session_[0-9a-z]{8,}|pane[ _-]?id|<REDACTED-USER>|DESKTOP-|hostname|machine name|localhost:[0-9]+'
(no matches)

# emails, IP addresses, URLs
$ git diff main...HEAD | grep -E '^\+' | grep -oiE '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|\b([0-9]{1,3}\.){3}[0-9]{1,3}\b|https?://[^ )`"]+' | sort -u
(no matches)
```

I additionally read `source-012-amendment.md` in full (280 lines). It is verbatim owner text plus a reconciliation table and a transmission-truncation disclosure. It contains commit SHAs, PR numbers, task ids, and file paths **relative to the repository root only**. No absolute path, no machine identifier, no credential, no personal data. The honest marking of six transport truncations as `[truncated in transmission]` rather than reconstructing them is good practice and is itself an anti-fabrication control.

**No leak. This is the check I probed hardest for a failure and it is clean.**

### 3. Secrets — CLEAN

```
$ git diff main...HEAD | grep -E '^\+' | grep -inE 'sk-[A-Za-z0-9]{16,}|ghp_|gho_|github_pat_|AKIA[0-9A-Z]{12,}|xox[baprs]-|-----BEGIN [A-Z ]*PRIVATE KEY|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|(api[_-]?key|secret|passwd|password|token|bearer|credential)["']?\s*[:=]\s*["'][^"']{8,}'
(no matches)

$ gitleaks version
8.30.1
$ gitleaks detect --no-banner --redact --log-opts="main..HEAD"
INF 3 commits scanned.
INF scanned ~178520 bytes (178.52 KB) in 411ms
INF no leaks found
GITLEAKS_EXIT=0
```

The untracked `M0-T027-G2.json` I read in full; it contains only task/gate ids, timestamps, and SHA-256 digests.

### 4. Integrity controls — VERIFIED, AND NOT WEAKENED

**Committed bytes are LF-only.** This was the specific CRLF-vs-digest hazard I was asked to test, and it does not occur:

```
$ for f in <7 changed files + index/gate/report files>; do git cat-file blob HEAD:$f | tr -cd '\r' | wc -c; done
CR_bytes_in_committed_blob=0   …/source-012-amendment.md
CR_bytes_in_committed_blob=0   …/requirements.json
CR_bytes_in_committed_blob=0   …/manifest.json
CR_bytes_in_committed_blob=0   project-control/reports/M0-T027-evidence-map.json
CR_bytes_in_committed_blob=0   project-control/reports/M0-T027-producer-report.md
CR_bytes_in_committed_blob=0   project-control/tasks/M0-T027.json
CR_bytes_in_committed_blob=0   project-control/state.json
CR_bytes_in_committed_blob=0   project-control/gates/M0-T027-G0.json
(untracked G2 file, worktree CR count: 0)
```

`.gitattributes` pins `project-control/directives/** text eol=lf`; `git check-attr text eol` confirms `text: set, eol: lf` for all three directive files. Despite `core.autocrlf=true` on this Windows host (`git config --get core.autocrlf` → `true`), worktree bytes are byte-identical to committed blobs for all three:

```
source-012-amendment.md   worktree CR count: 0
  committed blob sha256: 9dcdcba7dc4186d3f4257071d3f710998983fcc7d55809a2daa6a274e0e7cabf
  worktree file  sha256: 9dcdcba7dc4186d3f4257071d3f710998983fcc7d55809a2daa6a274e0e7cabf
requirements.json         worktree CR count: 0
  both = f8e09facc764fb1233c3a517f5ac39ac7ab841619912db7cd0c9b2607ff3fec0
manifest.json             worktree CR count: 0
  both = 6342e662de8c86ac547e36627ab9237c3cf588022c3bd02bc83182dcd889a885
```

**A Linux CI checkout will therefore see the same bytes and the same digests. The integrity-control failure mode named in my task does not exist here.**

**Digests independently re-derived from first principles.** I read the algorithm at `tools/validate_directive_compliance.py:387-401` — id digest is `sha256("\n".join(sorted(req_ids)))`, content digest is `sha256(requirements.json raw bytes)` — then recomputed both myself rather than trusting the manifest:

```
requirements.json bytes: 600418   CR count: 0
content_digest_sha256 (raw bytes) = f8e09facc764fb1233c3a517f5ac39ac7ab841619912db7cd0c9b2607ff3fec0
row count: 516   unique ids: 516   first: D-004-R001   last: D-004-R516
id_digest over newline-joined sorted ids = 70758c6723abc3f60c103f71a2da9e67b3ae946ce67c244f81f9a1a9ae3c9871

manifest requirements_id_digest_sha256      = 70758c6723abc3f60c103f71a2da9e67b3ae946ce67c244f81f9a1a9ae3c9871   MATCH
manifest requirements_content_digest_sha256 = f8e09facc764fb1233c3a517f5ac39ac7ab841619912db7cd0c9b2607ff3fec0   MATCH
manifest locked_requirement_ids count       = 516, order-identical to file order   MATCH
source-012 sha256 = 9dcdcba7…  == manifest sources[12].content_digest_sha256   MATCH
```

**All twelve source digests re-verified, not just the new one:**

```
OK   source-001.md            seq 1   CR 0   cb62b582374d9b8a
OK   source-002-amendment.md  seq 2   CR 0   bba041d9c629cf5e
OK   source-003-amendment.md  seq 3   CR 0   8f2bece86cfc9485
OK   source-004-amendment.md  seq 4   CR 0   d15911caa921bcf8
OK   source-005-amendment.md  seq 5   CR 0   518348c3a878803a
OK   source-006-amendment.md  seq 6   CR 0   4f697eb9cfead699
OK   source-007-amendment.md  seq 7   CR 0   4d5caed0ca1ca71f
OK   source-008-amendment.md  seq 8   CR 0   9cb73c514dfd9a22
OK   source-009-amendment.md  seq 9   CR 0   372842e93b0e697e
OK   source-010-amendment.md  seq 10  CR 0   3b281586434267e8
OK   source-011-amendment.md  seq 11  CR 0   0d019ee1e77d091b
OK   source-012-amendment.md  seq 12  CR 0   9dcdcba7dc4186d3
total sources: 12   digest mismatches: 0
```

**Append-only property proved structurally, not by digest alone** (a digest match only proves the manifest agrees with the file; this proves the file itself did not lose history):

```
main rows: 420   HEAD rows: 516
MISSING (deleted) ids: []
MODIFIED pre-existing ids: []
ADDED ids: 96, range D-004-R421 … D-004-R516
order preserved for first 420 rows: True
top-level keys identical main vs HEAD; only requirement_count 420→516 and
  amendments_applied gained source-012-amendment.md

manifest field-level diff:
  version 11 BECOMES 12
  sources: main len 11, HEAD len 12, prefix preserved True
  amendments: main len 10, HEAD len 11, prefix preserved True
  audit_log: main len 11, HEAD len 12, prefix preserved True
  locked_requirement_ids: main len 420, HEAD len 516, prefix preserved True
  requirements_id_digest_sha256 9a9d2381… BECOMES 70758c67…
  requirements_content_digest_sha256 f4b66f9a… BECOMES f8e09fac…
```

**Mechanism not weakened:** the only manifest fields that changed are `version` and the four append targets plus the two digests. No digest field was removed, nulled, renamed, or relaxed. `.gitattributes` was not touched. `tools/validate_directive_compliance.py` was not touched.

**Producer report byte-preservation independently confirmed** (this is what makes "append-only, nothing softened" checkable rather than asserted):

```
main bytes: 15102   HEAD bytes: 31358
HEAD starts with main bytes (prior sections byte-preserved): True
sha256 of main (LF-normalized) = 6674a8b916e1f0cdc002a0abf75a41ea20ae19433213e2ed03a5245b2f7a79c1
claimed pre-append digest      = 6674a8b916e1f0cdc002a0abf75a41ea20ae19433213e2ed03a5245b2f7a79c1   MATCH
appended bytes: 16256
```

### 5. Control-plane privilege — NO WEAKENING

```
$ git diff --name-only main...HEAD -- tools .claude .github CLAUDE.md
(empty)
$ git diff --name-only main...HEAD -- .claude/hooks/
(empty)
$ git diff --name-only main...HEAD -- .claude/agents/
(empty)
```

No `tools/**`, no `.claude/hooks/**`, no `.claude/agents/**`, no `.claude/rules/**`, no `.github/**`, no `CLAUDE.md`, no settings file. `producer_agent` and `required_gates` unchanged. No bypass flag and no special-cased task id introduced — I read `invalid_unblock_roster` and `_orchestrator_governance_exception` directly and confirmed admission is on packet *shape* only; the source states "There is no special-cased task id, no flag, and no environment override."

**Least privilege in the new requirement rows.** I checked whether the 96 new rows could bind unrelated work (an over-broad `applicability` would inject obligations project-wide):

```
new rows: 96
rows with NO task_ids scoping: 0
task_ids histogram: {'M0-T027': 83, 'D-004-OPTIONB': 13}
task_types histogram: {'["governance"]': 96}
classification: prohibition 24, evidence 23, obligation 20, return 13,
                sequencing 9, harness 6, authorization 1
independent_verifier: directive-compliance-verifier × 96   (≠ producer 'orchestrator' × 96)
```

Every row is narrowly scoped. **24 prohibitions to 1 authorization** — the changeset is overwhelmingly restrictive. The single `authorization` row is D-004-R421: "This GO is EXECUTION CONFIRMATION for the already-authorized OPTION B sequence in D-004 source-010; it does NOT authorize Step 5 or any unrelated work" — itself a limiting clause. Every row names an `independent_verifier` distinct from the `producer`, preserving producer≠verifier at the row level.

**Prompt-injection surface.** The registry is read by `.claude/hooks/directive_reminder.py`, which is unchanged. I inspected it: it emits only sanitized, length-capped directive **ids and titles** via `hookSpecificOutput.additionalContext`, and its own docstring states "registry text is treated as inert DATA". Requirement *text* is not injected as imperatives. A control-weakening-language scan across all 96 new rows (`disable|bypass|turn off|ignore the (rule|hook|guard)|override the (guard|hook|permission)|grant write|--force|settings\.local|permissionMode|dangerously|allowlist`) returned exactly one hit:

```
control-weakening language hits: 1
 - D-004-R480 :: PHASE 4 step 8: do NOT force, bypass, substitute reviewers, or call a red result green.
```

That is the opposite of a weakening. The write path into the registry is orchestrator-only and digest-enforced, so there is no untrusted-input channel into this surface.

### 6. Gate integrity — INTACT

- **No reviewer equals the producer.** `producer_agent` = `orchestrator`; `reviewer_agents` = `[control-plane-verifier, directive-compliance-verifier, code-reviewer, security-reviewer]`; `producer in reviewer_agents` → **False**. Independently, `gate()` rejects `reviewer == producer` *and* rejects the reserved `orchestrator` identity for any independent gate (`tools/project_control.py:886-893`), so the orchestrator structurally **cannot** record G3 or G5 regardless of roster contents.
- **G0 not overwritten, recreated, or backdated.**

```
$ git log --follow --oneline -- project-control/gates/M0-T027-G0.json
0361491 M0-T027: D-004 Step-1 reviewer pilot — negative test FAILED, blocker B-015
$ git rev-parse HEAD:…/M0-T027-G0.json   → b542f03ee17ae18e947d87daea4213deb32539c5
$ git rev-parse main:…/M0-T027-G0.json   → b542f03ee17ae18e947d87daea4213deb32539c5
$ git rev-parse 0361491:…/M0-T027-G0.json → b542f03ee17ae18e947d87daea4213deb32539c5
reviewed_at still 2026-07-24T18:35:04.645350+00:00; reviewed_sha still da0d42b6…
```

  One commit in its history; one blob across three refs. (Its *working copy* is CRLF from `core.autocrlf=true` checkout, so the worktree file hashes to `9a59951b…` while the canonical committed blob hashes to `40abdd49…` — the producer report cites `40abdd49…`, the correct canonical value. `git status` reports the file unmodified. No digest is computed over gate bytes, so there is no integrity consequence.)
- **No gate record hand-edited.** Only two gate files exist for this task (G0, G2). G0 is untouched; G2 is newly written by the CLI and carries the CLI's exact record schema including the in-regime `content_manifest_sha256`/`reviewed_sha` stamping added at `tools/project_control.py:913-923`.
- **Producer did not pre-write its own verification.** `verification.json` is unchanged on this branch and contains **no `M0-T027` entry** — correct; that record belongs to the independent `directive-compliance-verifier`.

### 7. Dependencies — NONE CHANGED

```
$ git diff --name-only main...HEAD | grep -iE 'package(-lock)?\.json|requirements.*\.txt|pyproject|poetry\.lock|yarn\.lock|pnpm-lock|Pipfile|\.npmrc|constraints'
(empty)
```

No dependency manifest, no lockfile, no vendored code, no new import. Nothing enters the supply chain through this changeset.

### 8. Test and validator execution (exit codes as requested)

```
$ python tools/validate_directive_compliance.py --check
VALIDATOR_EXIT=0

$ python tools/test_directive_compliance.py
Ran 55 tests in 36.335s
OK
EXIT=0

$ python tools/test_project_control.py
OK: original 15-check workflow preserved
OK: S1 transition enum (legal chain passes; every prohibited jump rejected)
OK: S2 accept preconditions (status, gates, dependencies, blockers)
OK: S3 gate classes (independent/self_check/administrative; no bypass)
OK: S4 containment (task ids, report paths, gate ids, checkpoint ids)
OK: S5 atomic writes (concurrent invocations, interrupted write, serialization failure)
OK: S6 spoofing attempts all rejected
OK: S7 backward compatibility (361 real ledger files parse; legacy records accepted; …)
OK: S8 hardening follow-up (orchestrator roster prohibition, --gates enum, blocked-task roster precondition)
OK: S10 governance-orchestrator unblock semantics (4 conjunctive conditions, preserved defaults,
        fail-closed malformed data, gate() unchanged, source-level generality proofs)
    S10 [D-004-R413/R414]: 10/10 blocks executed, 118 assertion cases
    S10 per-block case counts: 1-non-governance-orchestrator-refused=32,
        2-governance-orchestrator-unblocks=9, 3-governance-orchestrator-no-reviewers-refused=2,
        4-orchestrator-only-roster-refused=3, 5-governance-no-independent-gate-refused=6,
        6-malformed-fails-closed=31, 7-normal-producer-unchanged=12,
        8-cancel-and-message-only-ungated=12, 9-gate-unchanged=8,
        10-source-level-generality-proofs=3
OK: docs honesty (--agent disclaimed in --help and module docstring)
OK: S9 directive claim enforcement (refs required, selective citation refused, governance-path guard)
OK: S9 submit git-canonical identity (clean-required, dirty fails closed, stale on edit)
OK: S9 accept requires independent per-task verification at the git identity
OK: S9 regime-bypass closed + migration table (9 adversarial proofs)
OK: all 15 project-control test groups passed
EXIT=0
```

**Operational note for the orchestrator:** `test_project_control.py` exceeds a 2-minute timeout — my first run was killed at 120 s (exit 143). It passed on re-run with a 10-minute budget. Anyone reproducing this must allow the longer timeout; a 2-minute run will look like a failure when it is not.

---

## The roster correction — my ruling, as asked

**It was a legitimate, non-material, rigor-increasing correction. It was NOT a way to manufacture a passable gate. I say this on mechanical evidence, not on the producer's account.**

The decisive test is whether adding `security-reviewer` unlocked anything previously locked. I ran the guard against both rosters myself:

```
AFTER  correction: invalid_unblock_roster = None
BEFORE correction roster: ['control-plane-verifier', 'directive-compliance-verifier', 'code-reviewer']
BEFORE correction: invalid_unblock_roster = None
```

**The unblock guard returns `None` either way.** The roster correction was *not* load-bearing for the `blocked → in_progress` transition; that was admitted by the M0-T033 guard on the packet's shape (governance + orchestrator producer + required independent gates + three already-usable independent reviewers). The producer's claim on this point is accurate.

What the correction actually changed is narrower: which *identity* may record G5. Before it, `gate()` would have accepted a G5 record from `code-reviewer` or `control-plane-verifier` — both rostered, both independent — because `gate()` checks roster membership and independence, not specialization. So the alternative to this correction was **not** "no G5"; it was "G5 recorded by a generalist." `docs/GATES_AND_CHECKPOINTS.md:164` reads "Security-sensitive work requires `security-reviewer` even if QA passed." The correction moves the gate toward the documented specialist requirement.

Three further checks that it cannot be abused:

1. **Nothing was removed.** All three prior reviewers remain. The roster grew by exactly one, matching the owner's verbatim authorization at `source-012-amendment.md:139-141` ("I authorize adding exactly: security-reviewer").
2. **It cannot enable self-gating.** The producer is `orchestrator`, which `gate()` bars from *every* independent gate by reserved-identity rule, independent of the roster. Adding a reviewer would be dangerous if a producer added *itself*; that did not happen and could not have worked.
3. **It is genuinely non-material.** `reviewer_agents` is absent from `MATERIAL_FIELDS` (`tools/directive_registry.py:814-816`) — verified by reading the tuple, not by trusting the claim. The packet digest did move (`dc5d2979…` → `d6afb9d7…`), but entirely from the AS-1/AS-6 edits, and the producer disclosed that movement and its (nil) control-plane consequence rather than hiding it.

The uncomfortable structural fact remains true and I state it rather than glossing it: **I was added to the roster in the same changeset I am reviewing.** That is a real conflict shape and it deserved the scrutiny applied. My conclusion is that it is benign here because the addition was owner-authorized verbatim in advance, was not necessary to make *some* gate recordable, removed no check, and raised the specialization bar rather than lowering it. Had the roster correction been the difference between "no independent gate possible" and "gate possible," or had it swapped a stricter reviewer for a laxer one, I would have called it manufacturing and failed the gate.

---

## Expected versus actual

| Producer claim | My independent result | Verdict |
|---|---|---|
| Validator exit 0 | exit 0 | confirmed |
| `test_project_control.py` 15/15 groups | 15/15, exit 0 | confirmed |
| `test_directive_compliance.py` 55 tests OK | 55 tests, OK, exit 0 | confirmed |
| S10 guard block, 118 cases across 10 blocks | 118 cases, 10/10 blocks, per-block 32/9/2/3/6/31/12/12/8/3 | confirmed exactly |
| 516 locked ids, both digests match | 516, both digests re-derived and matching | confirmed |
| Registry grew append-only 420→516, zero rows edited | 0 deleted, 0 modified, order preserved | confirmed |
| Resolver-derived applicable = 233, 0 unresolved | 233, `ok: True`, `reasons: []` | confirmed |
| Evidence map covers all applicable ids | uncovered = `[]`, extra = `[]`, empty-valued = `[]` | confirmed |
| 128 carried forward, none dropped, 105 new | 128 retained, 0 dropped, 105 added | confirmed |
| G0 byte-unchanged, canonical `40abdd49…` | blob identical across three refs; canonical digest matches | confirmed |
| Producer report §1-12 byte-preserved, pre-append `6674a8b9…` | prefix-identical; digest matches exactly | confirmed |
| `invalid_unblock_roster()` → `None` before and after | `None` both | confirmed |
| Content manifest `e3b0c442…` is the empty-set hash | `sha256(b"")` = `e3b0c442…` — it is | confirmed (see LOW-1) |
| B-015 resolved; no OPEN blocker references M0-T027 | B-015 `resolved`; 7 non-resolved blockers (B-001, B-002, B-004, B-010, B-011, B-012, B-013), none mentions M0-T027 | confirmed |
| Dependency M0-T024 accepted | `status: accepted` | confirmed |
| M0-T025 unmodified | absent from diff; `status: backlog` | confirmed |

I found **no discrepancy between any producer claim and my independent measurement.**

---

## Evidence paths

- `<REPO>\project-control\tasks\M0-T027.json`
- `<REPO>\project-control\reports\M0-T027-producer-report.md`
- `<REPO>\project-control\reports\M0-T027-evidence-map.json`
- `<REPO>\project-control\directives\D-004-agent-teams-runtime-adoption\source-012-amendment.md`
- `<REPO>\project-control\directives\D-004-agent-teams-runtime-adoption\requirements.json`
- `<REPO>\project-control\directives\D-004-agent-teams-runtime-adoption\manifest.json`
- `<REPO>\project-control\directives\D-004-agent-teams-runtime-adoption\verification.json` (unchanged; no M0-T027 entry — correct)
- `<REPO>\project-control\gates\M0-T027-G0.json` (historical, byte-unchanged)
- `<REPO>\project-control\gates\M0-T027-G2.json` (new, uncommitted, CLI-written)
- `<REPO>\project-control\state.json`
- `<REPO>\.gitattributes`
- `<REPO>\tools\project_control.py` (read only — `gate()` :864-930, `invalid_unblock_roster()` :700-751, `_directive_submit_check()` :424-459, `_task_git_identity()` :319-327, `_MANIFEST_EXCLUDE_PREFIXES` :311)
- `<REPO>\tools\directive_registry.py` (read only — `MATERIAL_FIELDS` :814-816)
- `<REPO>\tools\validate_directive_compliance.py` (read only — digest algorithm :387-401)
- `<REPO>\.claude\hooks\directive_reminder.py` (read only — injection scope)
- `<REPO>\.claude\agents\security-reviewer.md` (read only — my own definition: `disallowedTools: Write, Edit, MultiEdit, NotebookEdit, Agent`; `permissionMode: plan`)

---

## Human-style walkthrough findings

Not applicable. This changeset has no user interface, no route, and no runtime behavior. `/human-walkthrough` is not required for G5 on a control-plane governance change.

---

## Regression/security/provenance findings

**Critical: none. High: none. Medium: none.**

### LOW-1 — The content-identity integrity control is vacuous for this task (out of scope by owner directive)

`content_manifest_sha256` for M0-T027 is `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, which I confirmed is `sha256(b"")` — the hash of *no input*. The cause is structural: `_task_git_identity()` calls `frozen_git_identity(..., exclude_prefixes=_MANIFEST_EXCLUDE_PREFIXES)` where `_MANIFEST_EXCLUDE_PREFIXES = ("project-control/",)` (`tools/project_control.py:311`), and **every** `allowed_path` of M0-T027 lies under `project-control/`. The set of hashed files is therefore empty.

Security consequence: for this task the content-manifest control provides **zero** tamper-detection over the actual evidence, and the `require_clean=True` dirty-check it carries also inspects nothing. A post-review edit to `M0-T027-producer-report.md` would not move this value.

Why it is LOW rather than higher, and why it does not block:
- The **`reviewed_sha` stamp is real and non-vacuous** — `3ed05fda6d434670e5b610e6dad7a8b224a9aa94` is recorded in the G2 record and in every reviewer dispatch, so tamper-detection is available through commit identity even though it is unavailable through the content manifest.
- It is **pre-existing D-001 behavior**, not introduced by this changeset, and the producer disclosed it explicitly rather than presenting the empty hash as meaningful (report §13.6: "the empty-set hash is the correct value, not a defect").
- The owner **explicitly scoped it out**: D-004-R489 — "The D-001 empty-applicable-set behavior found during M0-T033 acceptance is NOT part of this task."

**Recommendation (follow-up task, not rework here):** consider whether `frozen_git_identity` should return a distinguishable sentinel, or hash the task's own control-plane evidence files, so that "nothing was hashed" cannot be confused with "these bytes were verified."

### LOW-2 — The evidence map's self-declared identity fields were changed from values to `null`

`project-control/reports/M0-T027-evidence-map.json` previously carried `reviewed_sha: "9f065f0d…"` and `content_manifest_sha256: "e3b0c442…"`; both are now `null`. In isolation that reads as a removed binding.

I traced the consumer before judging it. `_directive_submit_check()` (`tools/project_control.py:424-459`) reads only the map's `requirements` keys for coverage, then computes the authoritative identity itself via `_task_git_identity()` and stamps `content_manifest_sha256` / `reviewed_sha` into the **submit report record**. The map's own copies are informational. Setting them to `null` at regeneration time is therefore defensible — arguably preferable to carrying the *stale* `9f065f0d…` identity from the abandoned prior closeout attempt, which would have been affirmatively misleading. **No control was weakened.** Recorded for completeness; not a defect.

### INFO-1 — Session identifier and owner email in commit trailers of a public repository

The three commits on this branch carry `Claude-Session: https://claude.ai/code/<REDACTED-SESSION-ID>` and author `martin10101 <myhappybook212@gmail.com>`.

I checked whether this is introduced here or pre-existing:

```
commits on main carrying a Claude-Session trailer: 28
total commits on main: 537
distinct session ids in main history: 3
$ git grep -l "<REDACTED-SESSION-ID>" HEAD
(no output — not present in any tracked file)
```

This is a **pre-existing owner-configured convention** (the owner's global `CLAUDE.md` mandates the trailer), it predates this changeset, and the session id appears **only in commit metadata, never in any tracked file**. AS-5's redaction requirement is about report *content*, and that requirement is fully met. A Claude Code session id is an identifier, not a credential — viewing the linked session still requires the owner's own authentication. Flagged for owner awareness only; **not a finding against this changeset and not blocking.**

### INFO-2 — OUT OF SCOPE: npm lifecycle scripts execute in CI

While confirming that no dependency file changed, I noticed a genuine pre-existing supply-chain gap. Reporting it because a security reviewer who saw it and stayed silent would be doing the job badly, but stating clearly that it is **unrelated to this diff and has no bearing on the verdict**:

```
$ cat .npmrc                     →  ignore-scripts=true
$ git ls-files | grep -i npmrc   →  (empty — no .npmrc is tracked)
$ git check-ignore -v .npmrc     →  exit 1 (not ignored, simply never committed)
.github/workflows/ci.yml:38  run: npm ci --no-audit --no-fund
.github/workflows/ci.yml:80  run: npm ci --no-audit --no-fund
.github/workflows/generate-lockfile.yml:25  run: npm install --package-lock-only --no-audit --no-fund
```

The `ignore-scripts=true` protection exists only in the owner's local untracked working copy. CI runners and fresh clones do not inherit it, and `npm ci` there runs dependency lifecycle scripts. **Recommendation:** a separate follow-up task to either commit a project-level `.npmrc` or add `--ignore-scripts` to the CI install steps. Nothing in M0-T027 touches this.

### INFO-3 — `project-control/gates/**` is not EOL-pinned

`.gitattributes` pins only `project-control/directives/**`. Under `core.autocrlf=true`, gate files check out CRLF (which is why the G0 worktree file hashes differently from its blob). Today this is harmless: committed gate blobs are LF-only, and no digest is computed over gate-file bytes. It would become an integrity issue only if a future change began hashing gate records from the filesystem. Note only; no action required for this gate.

---

## Defects

**None.** No critical, high, or medium finding. The two LOW items are a disclosed pre-existing D-001 property that the owner explicitly placed out of scope, and a change I traced to be neutral. Neither requires rework on this task.

## Required rework

**None.**

## What I verified independently versus what I could not

**Verified independently** (I ran the command or recomputed the value myself, and did not rely on the producer report): HEAD identity; full diff, stat, name-status, and merge-base; commit metadata and history; working-tree delta; all EOL/byte checks; all thirteen SHA-256 digests (twelve sources plus the requirements body) recomputed from raw bytes; the id-digest algorithm read from source and reproduced; append-only structure proved by set comparison against `main`; manifest field-level prefix preservation; producer-report prefix byte-preservation and its pre-append digest; G0 blob identity across three refs; the resolver's 233-id applicable set re-derived; evidence-map coverage set-differenced against it; previous-map row count measured at 128; `invalid_unblock_roster()` executed against both the corrected and the pre-correction roster; `MATERIAL_FIELDS` read from source; `gate()` gate-class and reviewer-independence logic read from source; the empty-set hash confirmed as `sha256(b"")`; validator and both test suites executed with exit codes; gitleaks 8.30.1 over the commit range; four independent leak/secret scan patterns; blocker and dependency statuses read from the ledger; requirement-row applicability scoping tabulated; control-weakening-language scan over all 96 new rows; `directive_reminder.py` injection scope read from source; my own agent definition's `disallowedTools`.

**Could not verify, stated honestly:**

1. **That the `blocked → in_progress` transition was performed by the CLI rather than by a hand edit (D-004-R453).** No artifact records the invoking process. My evidence is circumstantial but coherent: `state.json` moved `M0-T027` from `blocked_tasks` to `active_tasks` with a fresh `updated_at`, which is `sync_state()` behavior that a task-file edit alone would not produce; the `progress_log` entries carry the CLI's exact field shape; and `invalid_unblock_roster()` genuinely returns `None`, so the transition was lawfully available and there was no motive to bypass. I record this as **consistent with** a CLI invocation, not **proven** to be one. The `control-plane-verifier` is better placed than I am to rule on it.
2. **Runtime behavior of the guard fix under agent-teams conditions.** I verified `readonly_agent_guard.py` is unchanged and that the M0-T033 S10 test block passes 118 cases; I did not re-run the M0-T028 fresh-session Phase-8 sentinel experiment, which is historical evidence at head `88045b06` and outside this frozen identity. AS-6's arc-satisfaction ruling belongs to `code-reviewer`/`directive-compliance-verifier`. (I can attest to one adjacent live data point: the guard denied three of my own commands during this review, so it is active for a named teammate identity in this session.)
3. **The complete 233-requirement directive ruling.** I ruled individually on the 23 security- and integrity-bearing rows tabulated above. The remaining rows are the `directive-compliance-verifier`'s to rule on, and `verification.json` correctly has no `M0-T027` entry yet. I did not spot-check and then generalize.
4. **CI status at a PR head.** No PR exists yet at this identity; CI verification is a post-submit step.

---

## Reviewer conclusion

**G5 verdict: PASS.**

This is a control-plane governance changeset with no auth, RLS, storage, network, or product-code surface — and I confirmed that rather than assuming it. Against the six surfaces that do apply:

- **Evidence hygiene:** clean. Four independent scan patterns plus a full manual read of the 280-line verbatim owner capture found no session id, pane id, absolute path, machine username, hostname, email, IP, or URL in any added line. The public-repository constraint is met.
- **Secrets:** clean. Pattern scan and gitleaks 8.30.1 over all three commits: no leaks found, exit 0.
- **Integrity controls:** verified and strengthened, not weakened. All thirteen digests re-derived from raw bytes and matching; committed blobs LF-only so a Linux CI checkout will reproduce them (the specific CRLF hazard I was asked to hunt does not exist here); the registry grew strictly append-only with zero rows deleted or modified and every list prefix preserved.
- **Control-plane privilege:** no enforcement path touched — zero changes under `tools/**`, `.claude/hooks/**`, `.claude/agents/**`, `.claude/rules/**`, `.github/**`, or any settings file; no effort key anywhere; no bypass flag or special-cased task id; and the 96 new requirement rows are narrowly scoped to `M0-T027`/`D-004-OPTIONB` with 24 prohibitions to a single limiting authorization.
- **Gate integrity:** intact. No reviewer equals the producer, and the producer is structurally barred from independent gates regardless of roster. The historical G0 is byte-identical across `0361491`, `main`, and `HEAD` — not overwritten, recreated, or backdated. No gate record was hand-edited, and the producer did not pre-write its own verification.
- **Dependencies:** none changed.

On the roster question: **the correction that added me to `reviewer_agents` was legitimate and non-material, and it did not manufacture a passable gate.** The unblock guard admits this packet identically with or without me (`None` both ways, measured), G5 was already recordable by three other independent reviewers, no reviewer was removed or substituted, and the addition raises the review bar to the specialist that `docs/GATES_AND_CHECKPOINTS.md:164` requires for security-sensitive work. The conflict shape was real and worth challenging; on the evidence it is benign.

Every producer claim I tested reproduced exactly, with no discrepancy. Notably, the producer preserved a historical FAILURE rather than rewriting it, disclosed a digest movement it could have stayed silent about, disclosed a one-commit baseline drift and six transport truncations rather than absorbing them, and recorded the empty-set content hash as what it is instead of presenting it as verification. That pattern of disclosure is part of why I am comfortable passing this gate.

Two LOW observations and three informational notes are recorded above; none requires rework on M0-T027. I recommend two separate follow-up tasks: the D-001 empty-set content-manifest sentinel (LOW-1, explicitly out of scope here by D-004-R489), and the untracked `.npmrc` / CI `--ignore-scripts` supply-chain gap (INFO-2, wholly unrelated to this changeset).
