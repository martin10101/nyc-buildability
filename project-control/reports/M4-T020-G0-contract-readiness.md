# M4-T020 G0 contract-readiness record (administrative; orchestrator)

Date: 2026-09-13 (local; ledger stamps UTC). Wave-5 slot 1 — the FIRST packet executed by the
relaunched codex loop under D-053 (loop worker builds; monitor stamps; R595 stays shadow —
D-053-R002 authority boundary unchanged).

- **Requirement identifiers**: D-045:D-045-R002/R008/R009 (A2 geometry lane — B3 is the
  research-pinned first build task of the lane, M4-T016 Part 4.3 item 1: "depends on nothing
  new; blocked by nothing"); D-046:D-046-R001/R002 (campaign execution shape; SINGLE writing
  producer — the loop worker — so disjointness is trivially satisfied; nothing else in
  flight). `evaluate_task_refs` ok=true — applicable == cited (missing/invalid/unresolved all
  empty). Registry applicability appended with same-commit digest resyncs (c14):
  D-045 0bcc87c0→8944c6be, D-046 3903932e→4536a16c.
- **Research pin**: accepted M4-T016 report — Part 2.3 (CRS/unit evidence: wkid 102718 /
  latestWkid 2263, US survey foot, both-sources-same-CRS), Part 3.1 (geometry already arrives
  on the accepted transport's wire; parse_segment_page deliberately discards it), Part 4.3
  item 1 (the B3 contract verbatim: sibling module that "parses, CRS-validates, and types the
  polyline geometry already arriving on the wire", mappluto_lot_outline-beside-
  mappluto_geometry_arcgis precedent).
- **Design boundaries pinned**: accepted transport `dcm_street_centerline_arcgis.py`
  byte-immutable (sibling-module pattern, M4-T016 G1 advisory 5 precedent) — reuse by
  READ-ONLY import, no duplicate transport, no second fetch of the same page; CRS fail-closed
  (typed error on anything but 102718/2263; no assumed CRS, no reprojection, no unit
  conversion — measurement-grade EPSG:2263; display stays mappluto_lot_outline's job);
  geometry-validity taxonomy typed and visible (silent drops would corrupt B4's buffer
  inputs); values pass through untouched; zero new dependencies (§G: a needed package =
  BLOCKED submission).
- **Scope**: THREE allowed files (module + tests + producer report), all placeholders seeded
  this commit (gate content-identity fail-closed rule; module/test ruff-clean). Every accepted
  connector, rules/**, fixtures, tools, control-plane path forbidden; allowed_paths are exact
  files (trailing-slash dirs never match under policy.py path_matches; allowed wins over
  forbidden, so scope stays narrow).
- **Scenarios**: S1–S5 (wire-format parse + typing; CRS fail-closed; malformed-geometry
  taxonomy; passthrough integrity + provenance; scope + regression + ruff + modularity).
- **Gates**: G0/G3/G4; reviewers code-reviewer (G3: research-pin + reuse fidelity) +
  qa-engineer (G4: test adequacy incl. taxonomy negatives), both ≠ producer. In-loop
  Codex/Astra bridge reviews are advisory production reviews (D-053-R004 role a); they never
  substitute for the gate lane (D-046-R003 unchanged).
- **Loop-execution profile**: documented_test_commands are closed-profile single segments
  from the repo root (no cd/&&; ruff included — api CI step 1); packet notes carry the
  Bash-tool requirement (broker defers PowerShell as unclassifiable) and the DL-2 checkpoint
  contract (FULL 40-hex starting_sha or empty string).
- **Producer model (D-047-R001 deviation recorded)**: claude-sonnet-5 is NOT on the loop's
  immutable config.toml allowlist ([claude-fable-5, claude-opus-4-8]); per D-053-R004 a
  blocked allowlist is an OWNER SETTINGS ITEM, never a bypass. The worker runs the
  model_selection.toml pin (claude-fable-5 after the D-036-R001 standing Thursday revert,
  executed this seam with the opus-4-8 quota fallback chain restored; claude-opus-4-8 if the
  owner reverts). Deviation recorded here and at the owner seam.

Verdict: **PASS** — packet claimable; loop-launchable after claim + worktree sync.
