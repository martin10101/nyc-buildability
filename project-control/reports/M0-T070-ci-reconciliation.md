# M0-T070 — PR #222 live CI reconciliation (D-014 amendment 2)

Owner instruction of 2026-08-18 ("PR #222 LIVE CI RECONCILIATION — DO NOT MERGE")
captured verbatim as `D-014/source-002-amendment.md` (sha256 `b2b17b294ce8…`),
decomposed into rows D-014-R040..R052 (amendment_sequence 2), all bound to the
D-014-BOOTSTRAP sentinel so the already-gated M0-T070 applicable set is unchanged.

## Failure 1 — control-plane c14 digest mismatch (M0-T070-owned; FIXED)

- CI run 32108527309, job 95622882065: `D-014 requirements.json content digest
  mismatch — manifest 352e50c36264… actual 237abcd104c5…`.
- Root cause (proven locally): the capture scripts wrote the D-014 registry JSON
  with Python `write_text` newline translation → **CRLF** working-tree bytes on
  Windows; the recorded digest `352e50c36264…` was computed over those CRLF
  bytes; git normalized the committed blob to **LF** (`237abcd104c5…`), which is
  what CI checks out and hashes. Requirement BODIES were never edited — the two
  digests differ only by line endings. (`source-001.md` was LF everywhere, which
  is why its digest never failed.)
- Fix (through the amendment process, never silently): requirements.json,
  manifest.json, verification.json, and index.json rewritten with LF bytes that
  match the git blob exactly; amendment-2 rows appended; `locked_requirement_ids`
  grown to 52; `requirements_id_digest_sha256` and
  `requirements_content_digest_sha256` restamped (`96828f9097cd…`); the restamp
  and its before/after digests are recorded in the manifest `audit_log`. The
  rewriting script asserts R001–R039 JSON values are unchanged.

## Failure 2 — web-dependency-security / nanoid (EXTERNAL; recorded as B-019)

- nanoid `<3.3.18`, severity high, GHSA-2v37-7h3g-55p8, via postcss.
- Read-only verification: `apps/web/package-lock.json` pins nanoid **3.3.17 with
  the byte-identical integrity hash** at PR head 04cae38, PR base de2f224, and
  origin/main 5c71fe0; PR #222 touches **zero** files under `apps/`
  (`git diff de2f224..HEAD -- apps/` is empty). Pre-existing on main; the
  advisory is newer than the committed lock.
- Per D-014-R047 nothing in M0-T070 edits the lock, runs `npm audit fix`, or
  suppresses the advisory. Recorded as open blocker
  `project-control/blockers/B-019-nanoid-transitive-advisory-web-dependency-gate.json`
  with the recommended separate repair: its own owner-authorized task, branched
  from **origin/main** (not stacked on the control or repair branches), bumping
  nanoid 3.3.17 → 3.3.18 under the dependency-security policy (7-day age gate;
  single-package owner age-waiver if 3.3.18 is younger). Merge order: that PR
  lands on main first; PR #222 inherits the green gate untouched.

## Item 3 — gate identity reconciliation

- G2/G3/G5 record reviewed_sha `6aae5857`; later commits (`bcc0962`, `04cae38`,
  and this reconciliation commit) are control-plane-only.
- The lifecycle's authoritative identity is the **git-canonical material
  identity over allowed_paths** (`frozen_git_identity` — the same function used
  by submit, gate, and accept). Identity at reviewed sha 6aae5857 =
  `296b8fa6b7ff5e44cee9eacf0e2bb1b7bbfdd3fa170c0e77cae71140372f965c` — equal to
  the submit-stamped `content_manifest_sha256`, and equal at the reconciled HEAD
  (verified post-commit; no allowed_paths file changed after 6aae5857). The
  recorded gates therefore still attest the exact reviewed material; M0-T070
  remains `awaiting_gate` (95%), not accepted — acceptance is a later lifecycle
  act and will re-derive this identity plus the amendment-2 sentinel rows.

## Post-fix verification (local, this checkout)

| check | result |
|---|---|
| `python tools/validate_directive_compliance.py --check` | exit 0 (registry VALID, D-001..D-014, amendment 2 recorded) |
| `tools/test_project_control.py` + `tools/test_directive_compliance.py` + `tools/test_directive_reminder.py` | **155 passed** |
| `tools/test_agent_supervisor_command_authority.py` | **29 passed** |
| full supervisor suite `tools/test_agent_supervisor_*.py` | **1557 passed, 2 skipped, 0 failed** |
| M0-T070 applicable set after amendment | unchanged: 30 rows (R009..R039), resolver `ok: true` |
| committed-blob digest == manifest digest | verified post-commit (CI-equivalent bytes) |

Final GitHub job results for the reconciled head are appended to the return
message (D-014-R044) after the watch completes.
