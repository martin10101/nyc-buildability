# M3-T013 producer report — ZR snapshot table-payload tamper-evidence (DB-276, Option A)

Producer: backend-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-ae722d74707eb2cec`.
Claim head reset to `1cbc8ccfeef53ce6986d1ccc7d76acc290d2723a` (task/wave28-placement-wiring); working tree clean before edits.

## Summary of the work

Additive `table_digest_sha256` over the canonical JSON of each ZR capture's table payload, verified by the
snapshot loader so a silently edited table value fails on load. No existing `content_digest_sha256` or citation
digest moves; no captured value, reading, or label changes. The set is derived by glob (37 table-bearing files,
incl. the sweep-missed `zr-22-131`), never hard-coded.

Changes:
1. `services/api/app/rules/snapshots.py` — three helpers (`_table_payload`, `_canonical_table_digest`,
   `_verify_table_digest`) + one call in `load_snapshot_file` after the unchanged `content_digest_sha256` check.
   Digest is over the PARSED payload: `sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",",":")).encode("utf-8"))`.
   Fails closed on: digest mismatch; payload present without digest; digest present without payload; both `table`
   and `tables` present; a `table`/`tables` key of an unexpected shape.
2. 37 canonical snapshots under `docs/research/zr-snapshots/v1/` — `table_digest_sha256` inserted on the line
   IMMEDIATELY ABOVE `content_digest_sha256` (2-space indent, trailing comma), leaving the `content_digest_sha256`
   line byte-identical in every file. Re-synced the 37 bundled copies under `services/api/app/_zr_snapshots/v1/`
   with `sync_zr_snapshots.py` (byte-identical). No non-table snapshot changed.
3. `docs/RULES_ENGINE_ARCHITECTURE.md` §5.1 — documents the three payload shapes (`table.rows`, `tables`,
   `table.row_groups`) and the new field, the parsed-payload canonicalization, and the fail-closed loader behavior.
4. `services/api/tests/rules/test_zr_snapshot_table_digest.py` — new test (13 tests), glob-derived set + mutation
   + revert proof + both-direction fail-closed + non-table pass + canonicalization-stability.

## Glob-derived set: 37 table-bearing files with each table_digest_sha256

Derived by glob over a `table` or `tables` key (18 `table.rows` + 18 `tables` + 1 `table.row_groups`). The
digest-bearing set == the glob set (asserted by `test_digest_bearing_set_equals_glob_set`). Digest = sha256 of the
canonical JSON of the parsed payload:

| file | shape | table_digest_sha256 |
|---|---|---|
| zr-22-121 | tables | 46dfd6959d324c7481e441ef3d1d12772be62172385ad2342cc391d3b4c1266a |
| zr-22-131 | tables | 08c6a6c007f3c077e810ecddf4e4519f208fd8f3e3535fca1f484b168d9ae9e3 |
| zr-23-12 | tables | 08925508b88ca4e13613f0a019c20b4cc6bba219ea818af9a1e9760d1c1466d8 |
| zr-23-21 | table.rows | 7a6cf2242b82dc50e46c01640fad3c1f29660396895352fc5eb2017600ce3f43 |
| zr-23-22 | table.rows | 518c1f2bf6154ebc15c9f4812f9a31f6d55713db7f88afc2ae47608def9d7f97 |
| zr-23-371 | tables | 4c3509c23833e15b2eb0375b8696819a117a99588cd0951367991492c574edeb |
| zr-23-422-r3-r4 | table.rows | f0e78a58edf52ec169a9ce5056ea6a86f1735853356c6729b6a77380a64735a6 |
| zr-23-422 | table.rows | 7a2643e52930b2c25a05efa67d5c9c5401715c90ee7975e7cb609d680cf01941 |
| zr-23-424-r1-r2 | table.rows | 38abef9fdf2457f5c68df924869deb40b98d22d604f3ff869e42bee2fc364990 |
| zr-23-424 | table.rows | 184a2e31705fb8e1b65d668076b489043ea95fe61f5e2aece53c9322ebd6fca7 |
| zr-23-432 | table.rows | 6218cfcf1df312640560bb54a67c06ba5fc1890063680d33e0f42f57df1478a4 |
| zr-23-434 | table.rows | 495aebfb0ca7fab6eae12d348f53c6cb5c014a388444f286e27ecaf687e321db |
| zr-23-441 | table.rows | 5ff0eac9da6004e4b6e1cf027ad2221ba7bb2eba512776d1dc0f2aa625581644 |
| zr-23-442 | table.rows | e9411d340824faca1c14f1dba3ec4dcf24516bf866324a8797c7bca64e6bd234 |
| zr-23-443 | tables | a29bb68daad3ced5943ad38151d3c3153de324f1015cf5c5afe34594fb4d8a2e |
| zr-24-11 | tables | 3db6b4157fceb19195ebf6f5d69c58a56b04a006b366fbda43dc1e81fa3ad7ac |
| zr-24-111 | table.rows | 79b184e6e13f8fa21290ee2726881c23e3a76c6d9dc9d4f8fd1a063a2bfa3f57 |
| zr-24-162 | table.rows | f791c1909feca3cb7d4807eab93f2bcdb5e5cae0768d76dfd0c0bfd8127d8e3e |
| zr-24-34 | table.rows | 08e45980bfa7b90dcfd97a4412968f9117ed7a0c9ae0160a884f421969595e01 |
| zr-24-522 | table.row_groups | 741844317a971e5ae990a60ad1bdf1bfd935f1d4b35898f632b2abb1a8b6690d |
| zr-25-212 | tables | c7cf2a04cb5d0b703c65b6e76fced0cc425a228348b02fe52917da92b9044eae |
| zr-25-222 | tables | efa5d6ca043c29f859e856f5172201666075daf3dce939a5f07ded9a83b95975 |
| zr-25-232 | tables | acec73199afac7751df93ae3272f70926a23dca3485cf598a291160e813277a4 |
| zr-25-811 | table.rows | 5c639053099b242c7706e0e73155b63ef28d6f3efbaee8eea600ae8c3ca39c51 |
| zr-32-121 | tables | fca7b9e8b1c43fea460b62601da37067bce235c93473b1582819bf20d2a97ce2 |
| zr-32-131 | tables | a20492cce0cd6e8df6faf755774f198c0e0510ee53204d379af0b9b9daf98543 |
| zr-32-161 | tables | 367d8b6cd927d94539534af560bc1e214a8250798ff9cf7e2f82639104caf2f4 |
| zr-33-121 | tables | 6beb3dea51a09e674002893f25f3ca2d4079070f538509791af386aef7b7d6fb |
| zr-33-122 | tables | 09bb3857564837187ae2f069684692167a1a8d6ef943304b28713cab914d9baa |
| zr-33-123 | tables | 61a28da5617b07968bda45d9c2f4f04c2084df78b41170ba7db72098522e134c |
| zr-34-112 | table.rows | e3362b847aceee309fe74e306cf842d15448e95cce9e84ae2c86fb623e065474 |
| zr-35-32 | table.rows | 140e4cee69d7de4f54f37e81eef959d0564321625a737cbc547f09f67e6e50c3 |
| zr-35-33 | table.rows | 198f4d68f3ee8b00d500b24e4889ddc18c673288e9b67028cd5cb56032aeb9b3 |
| zr-36-21 | tables | eb9303cb76c2a3b5f2420038b4baaf00016daeb5f4e9a2606307d38a1d31dbdc |
| zr-36-231 | tables | 48cc98b39e48ed622e8861f91582785353a791469ca033b1776a8344fe055eae |
| zr-36-62 | tables | 9fe5f67666c3a6ac37549bfe58c3b5950d4fcf828cc5ef8173d9ff457b75490b |
| zr-36-711 | table.rows | ae9c0f5cd9efc70638128e6d8698d50d7b0e39053ea4440cea9ad4deab9a0f9c |

Each of the 37 canonical files has a byte-identical bundled copy under `services/api/app/_zr_snapshots/v1/`
(sync `--check` OK, 255 files). Aggregate sha256 over the sorted `path sha256` (LF-normalized) lines of all 74
changed snapshot files: `7841f4ba303454fb73a89ffc196b562f2234861cda119cb7862d39a5076023ce`.

## Loader cases (snapshots.py `_verify_table_digest`)

- payload present + correct digest → loads (the 37 production files; S1/S2).
- payload present + digest mismatch → `SnapshotError("… table_digest_sha256 mismatch …")`.
- payload present + no `table_digest_sha256` → `SnapshotError("… table payload present but no table_digest_sha256")`.
- `table_digest_sha256` present + no payload → `SnapshotError("… table_digest_sha256 present but … no table payload")`.
- both `table` and `tables` keys → `SnapshotError("… carries both 'table' and 'tables' …")`.
- `table` of unexpected shape (no rows/row_groups) → `SnapshotError("… 'table' payload is not an object …")`.
- no payload (non-table snapshot) → loads unchanged; no digest required (S5; the ~218 non-table snapshots).
- `content_digest_sha256` over `verbatim_excerpt` is verified EXACTLY as before, ahead of the new check.

## Mutation proof (tests, exit 0)

- `test_flipped_table_value_fails_load`: build a tmp snapshot with a valid table + digest (loads); flip one table
  value WITHOUT updating the digest → `load_snapshot_file` raises `SnapshotError: … table_digest_sha256 mismatch`.
- `test_pre_change_excerpt_digest_is_blind_to_the_table_edit` (revert direction): the flipped file's
  `content_digest_sha256` still equals `sha256(verbatim_excerpt)`, so the PRE-CHANGE loader (excerpt digest only)
  would have accepted it — the new `table_digest_sha256` check is the sole load-time guard that catches the edit.
- Same mutation proven for the `tables` list shape and the `table.row_groups` shape.
- `test_digest_is_over_parsed_payload_not_file_bytes`: a compact and a pretty/key-reordered serialization of the
  same payload both load — the digest is over the parsed object, so re-indentation never breaks it (RISK B3).

## Unchanged-digest proof

Script `prove_unchanged.py` compared every table-bearing file in BOTH directories against the claim head
`1cbc8ccf` via `git show`:
- table-bearing files checked (both dirs): 74
- `content_digest_sha256` values MOVED: 0
- files that gained `table_digest_sha256` (absent at claim head): 74
- non-table snapshot files whose BYTES changed: 0
Also confirmed: `zr-23-432` content_digest == `sha256(excerpt)` == `9fab7be8…` (unchanged); `zr-23-22` likewise;
the existing citation pins `943b65f9…`/`9fab7be8…` do not move. The old whole-file hash `37c1414c…` (NB-06, see
below) appears in exactly one place.

## Checks (direct exit codes; lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider; heavy runs under flock heavy-run.lock)

| check | exit | result |
|---|---|---|
| `python -m ruff check .` (cwd services/api) | 0 | All checks passed |
| focused pytest (new test + bundle + far-provenance + r6b reference cases) | 0 | 85 passed |
| new test alone (`test_zr_snapshot_table_digest.py`) | 0 | 13 passed |
| `sync_zr_snapshots.py --check` | 0 | OK, 255 files byte-identical |
| `tools/research_record_check.py --check` | **1** | **FAIL — NB-06 pin on zr-23-432 (see BLOCKER)** |
| `tools/modularity_check.py --check` | 0 | pass (warns only on pre-existing files; snapshots.py not flagged) |
| `scripts/lanes/check_lane_paths.py --coverage` | 0 | LANE COVERAGE PASS, 10812 files |
| full api suite `pytest -q` (cwd services/api) | **1** | 10075 passed, 8 skipped, **4 failed (pre-existing, see below)** |

Path note: the packet's documented focused command named `tests/rules/test_r6b_reference_cases.py`; the file is at
`tests/rules/reference_cases/test_r6b_reference_cases.py` (used that; same test, green).

## BLOCKER — research_record_check: NB-06 pins zr-23-432's whole-file hash (orchestrator scope correction needed)

`tools/research_record_check.py --check` exits 1 with ONE cause:
`NB-06: 'evidence[9].saved_copy' 'docs/research/zr-snapshots/v1/zr-23-432.snapshot.json' sha256 does not match`.
`docs/research/evidence-records/NB-06-street-wall-setback-side-yard.json` evidence item E10 is a `saved_copy`
pin of `zr-23-432.snapshot.json` by its whole-file (LF-normalized) sha256. Signing zr-23-432 (mandatory — it is
table-bearing; S1's glob set includes it; it carries the governing R6B base-height table) changed the file's bytes
and therefore that whole-file hash. NB-06 is in the packet's forbidden paths (`docs/research/evidence-records/`),
so per the brief ("STOP that part and report it; never edit a forbidden file") I did NOT edit it.

Scope: I swept all 7 NB evidence records (36 `saved_copy` snapshot pins). EXACTLY ONE breaks — NB-06 → zr-23-432 —
because it is the only snapshot that is both table-bearing AND NB-pinned. No rule file, review_register, reference
case, or pytest test pins a snapshot's whole-file hash (confirmed by grepping the old hash `37c1414c…`: NB-06 only).

E10's human-written `excerpt` row reading (R6B base 30/45/55, qual 45/65) and every other NB-06 value are unchanged;
only the saved_copy file's BYTES changed, from the additive `table_digest_sha256` field.

Required correction (orchestrator, same pattern as the M5-T170/NB-03 seam defect): add
`docs/research/evidence-records/NB-06-street-wall-setback-side-yard.json` to allowed_paths and re-pin E10.sha256:
- OLD: `37c1414c2f1fb93404dca4178d70304c6f39eeecf0f39aa215bd2754cd16887a`
- NEW: `ae06010e91a8fae0017f7a33a671c8ce5750c8ddb4f25a647a92ca79c1280898`
following the NB evidence-record revision procedure (and confirming no reading/label change, which there is none).
After that re-pin, `research_record_check --check` passes. The planning sweep's "no digest moves / S9 green" missed
this whole-file saved_copy pin (it checked only the content_digest pins and that snapshots.py was non-NB-pinned).

## Pre-existing full-suite failures (NOT introduced by this task)

4 failures, all in `tests/rules/test_zoning_rule_review_register*.py`: "orphan calculation page with no entry:
calc-area-allocation.md" and "calc-first-placement.md". Those pages exist under
`docs/zoning-rule-review/calculations/` with ZERO register entries. None of the register, the review pages, or
those test files are in my diff (`git diff --stat HEAD` for those paths = empty); they are byte-identical to the
claim head and are M5-T172-owned content not yet integrated on this wave-28 branch. My changed snapshots are not
read by the register-calculation tests, so these reds reproduce identically at the pristine claim head.

## What I could NOT check / limitations

- Did not run the full directive-compliance test harness (`tools/test_directive_compliance.py`) — out of a
  producer's scope and prohibitively slow; validator/CI own that.
- Did not re-fetch live ZR pages (R6B readings settled per docs/reference-cases/R6B/cases/); this task adds
  integrity metadata only and changes no captured value, reading, evidence record, or label (D-093-R037 /
  principle 20 not triggered) — EXCEPT for the forced NB-06 re-pin above, which is a mechanical saved_copy hash
  update with no reading change, left for the orchestrator.
- Did not start any server or touch ports 3000/3001/8000.

## Round 2 (builder, backend-engineer) — the NB-06 E10 re-pin (G4 F1 / G1 check 6)

Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-ad04ce314c137419d`. Base reset to
`c106173557013163f8cfbd41d6c9fce980129e80` (head of task/wave28-placement-wiring with M5-T172 accepted plus the
orchestrator's cherry-pick of round-1 commit 06651e8d); clean status before edits.

Round 1 left research_record_check red on exactly one cause: NB-06 evidence E10 pinned zr-23-432.snapshot.json by
its whole-file LF sha256, and signing that snapshot moved its bytes. M5-T172 (which owned NB-06) is now accepted,
so scope correction 1 added NB-06 and the records README to the allowed paths and scenario S10. This round applies
only that re-pin — a records-only change; no code, snapshot, loader, doc or test touched.

NB-06 (`docs/research/evidence-records/NB-06-street-wall-setback-side-yard.json`) → revision 6:
- `revision` 5 → 6; `last_changed` stays `2026-10-15` (same day).
- E10 (`evidence[9]`) `saved_copy` sha256 re-pinned:
  OLD `37c1414c2f1fb93404dca4178d70304c6f39eeecf0f39aa215bd2754cd16887a`
  → NEW `ae06010e91a8fae0017f7a33a671c8ce5750c8ddb4f25a647a92ca79c1280898`
  (the LF sha256 of the signed zr-23-432.snapshot.json at this head: `tr -d '\r' < f | sha256sum`; matches the
  value G1 and G4 independently found).
- Appended one `implementation.dependency_assessment` entry: the saved copy gained only the additive
  `table_digest_sha256` field; `verbatim_excerpt` and its `content_digest_sha256` are byte-identical, so the R6B
  30/45/55 ft base-height readings, the setback-above-base reading and the side-yard reading are unchanged. A
  saved-copy hash re-pin only.
- Unchanged: `code_identity`, every `reading`/`interpretation`/`condition`, the `conclusion.research_status`
  (`interpretation_awaiting_review`), and `promotion.requested_label` (null — nothing labelled Verified).

README index cell: `docs/research/evidence-records/README.md` was NOT changed. Its index columns are
Record | Question | Research status (copied from `conclusion.research_status`, which did not change); the format
carries no revision number, so per the packet it needs no edit.

Checks (direct exit codes; lanes venv; multi-file pytest under `flock /root/project/lanes-runtime/heavy-run.lock`;
see the RETURN hand-back for the full run log and counts):
- `python3 tools/research_record_check.py --check` → exit 0 (PASS; NB-06 now current; NB-04 code_current=False is
  pre-existing, reported-not-failed, unrelated to this change).
- `cd services/api && python -m ruff check .` → exit 0.
- `flock … python -m pytest -q -p no:cacheprovider tests/rules` (cwd services/api).
- `python3 services/api/scripts/sync_zr_snapshots.py --check` → 255 files byte-identical.
- `python3 scripts/lanes/check_lane_paths.py --coverage`.
- whole api suite once.

Scope: this round edits only NB-06 and this report. No snapshot, loader, doc or test from round 1 was retouched;
the 37 signed captures and their bundled copies remain as cherry-picked into the base.
