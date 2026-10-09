# M5-T093 producer report — D-087 PDF-1b real-corpus trial of the sheet reader

- **Task:** M5-T093 (research-only; D-087 wave 3). Producer: backend-engineer, orchestrator-dispatched
  subagent, isolated worktree `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t093` (branch
  `task/M5-T093-corpus-trial`, contract head `6cc93092`).
- **Directives:** D-087-R001/R002/R005/R009, D-066-R001 (cited in the packet).
- **Deliverables (the only two allowed paths, both replaced from placeholder):**
  - `docs/research/architect-corpus-reader-trial-2026-09.md` — provenance, per-file facts, reader
    outcome, the DB-055 (g) ruling, and the prioritised C1 scope.
  - `project-control/reports/M5-T093-producer-report.md` — this report.
- **No reader change.** Every file under `services/`, `apps/`, `packages/`, `tools/` and the corpus
  note itself is byte-untouched (the DB-055 (g)+(h) precondition; forbidden_paths honoured).

## Headline

`read_sheet` reads **none of the six real corpus files**. All six are refused at the
cross-reference stage with the identical typed refusal `feature='cross-reference stream'`
(`origin=strict_reader`, `reject_code=unsupported_pdf_feature`), before any page content is
interpreted. DB-055 (g)'s cross-reference-stream limit is the single, real, blocking defect for
real files; the `sh`-shading and inline-image limits are present in the corpus but **latent** (never
reached). DB-055 (h) is discharged with a **negative** result — nobody may tell the owner real
architect PDFs can be read.

## Method (all commands from the scratch subfolder `…/scratchpad/m5t093/`; nothing committed from it)

1. `[OBSERVED]` Downloaded items 1-6 by `curl` from the recorded URLs → `HTTP 200`, byte counts all
   equal to the note; `sha256sum` on the scratch copies reproduced every note digest exactly (no
   mismatch, no fetch failure). retrieved_at 2026-09-24T10:47-10:49Z.
2. `[OBSERVED]` Independent byte scan (`scan.py`, does NOT use the reader): raw byte walk for header
   version, xref kind (byte at the last `startxref` offset), `/ObjStm`, `/Encrypt`; stdlib-`zlib`
   inflation of every FlateDecode stream to reach keys packed into object streams and to token-scan
   content for the `sh` operator and ordered `BI·ID·EI` inline images; page count and producer
   corroborated with PyMuPDF/`fitz` (agreed on all six). `where_objs.py` confirmed the page tree
   lives only inside object streams.
3. `[OBSERVED]` Reader trial (`run_reader.py`): the accepted bare-package 3.11 shim technique with
   `API_ROOT` pointed at the **worktree's** `services/api` (the original `run_sheet_tests_ctl24.py`
   was not modified), so the 3.12-only `app/documents/units.py` is never imported. Each file read
   **twice**; `run1 == run2` was `True` for all six (frozen dataclasses — deterministic).
4. `[OBSERVED]` Deleted the six drawings at the end; committed nothing from the corpus.

## Acceptance scenarios

- **AS-1 (provenance) — MET.** 6/6 fetched from the recorded URLs; HTTP 200; bytes == note; sha256
  MATCH for all six; retrieved_at recorded. No mismatch or failure to record. Note §1 table.
- **AS-2 (per-file facts) — MET.** PDF version, producing app, page count, xref TABLE vs STREAM,
  object streams, shading, inline images, encryption established per file by the independent byte
  scan (not the reader), fitz-corroborated. Note §2 table.
- **AS-3 (reader result) — MET.** `read_sheet`'s exact outcome recorded per file (all six: the
  `cross-reference stream` refusal), reproduced by a second identical run. Note §3 table + verbatim
  detail.
- **AS-4 (conclusions) — MET.** Note §4 states which DB-055 (g) limits block real files (xref
  streams: 6/6, real; object streams: co-requisite; shading + inline images: latent; encryption:
  none) and §5 gives the prioritised C1 scope. No claim beyond these six files.
- **AS-5 (scope) — MET.** Exactly the two allowed doc paths change; no corpus file, script, or
  fixture is committed; the reader and all `app/**` files are byte-untouched. Verified by
  `git status` / `git diff --stat` before the single commit (see below).

## The three tables in brief

**Provenance (AS-1):** items 1-6, HTTP 200, bytes = note, sha256 MATCH all six.

**Per-file facts (AS-2):**

| # | ver | producer | pages | xref | ObjStm | shading | inline img | enc |
|---|---|---|---|---|---|---|---|---|
| 1 | 1.7 | PDFMaker 9.0 for AutoCAD | 88 | STREAM | 10 | no | no | no |
| 2 | 1.7 | PDFMaker 9.0 for AutoCAD | 94 | STREAM | 76 | no | yes | no |
| 3 | 1.5 | Adobe PDF Library 11 / PDFMaker 11 for Word | 14 | STREAM | 32 | yes | no | no |
| 4 | 1.6 | Canon iR-ADV C5840 → Acrobat 23 Paper Capture | 8 | STREAM | 13 | no | yes | no |
| 5 | 1.6 | Acrobat 11.0.3 Paper Capture / I.R.I.S. | 1 | STREAM | 3 | no | no | no |
| 6 | 1.6 | Acrobat 11.0.3 Paper Capture / I.R.I.S. | 1 | STREAM | 3 | no | no | no |

**Reader outcome (AS-3):** 6/6 → `REFUSAL origin=strict_reader reject_code=unsupported_pdf_feature
feature='cross-reference stream'`; `run1 == run2` for all six.

## Conclusions (detail in the note §4-§5)

- **Cross-reference streams block 6/6 real files** across both drawing classes and three independent
  producing toolchains. Confirms the M5-T083 DCV worst case: the reader reads **neither** positive
  vector fixture.
- **Object streams are an inseparable co-requisite** — the page tree lives only inside `/ObjStm` in
  every file sampled, so xref-stream support alone is insufficient.
- **`sh` shading (item 3) and inline images (items 2, 4) are real reader gaps but latent** — never
  reached because the xref refusal fires first. Encryption is absent.
- **C1 priority:** P1 = xref streams + object streams (blocking; re-run this corpus by sha256 as the
  C1 harness); P2 = inline-image + `sh` handling, reachable only after P1; P3 = make the scan-only
  class (items 4-6) refuse for a **scan-only** reason, not the incidental xref one; deprioritise
  encryption. Sequencing: DB-055 (b) requires the `sheet_reader.py` modularity split before P1 grows
  the reader.

## Discoveries (D-069 — route at the seam; not fixed in-packet)

- **DB-055 (g) resolved to a fact:** the two positive VA vector items (1-2) **do** use cross-reference
  streams — the risk the DCV flagged is confirmed, not merely possible. The `sh`-shading limit and a
  new inline-image limit (`BI`/`ID`/`EI` present in items 2 and 4; the reader has no `BI` handler)
  are latent behind the xref blocker. Suggest annotating DB-055 (g)+(h) as **discharged with a
  negative result** and recording the inline-image gap as a new reader-scope item for C1.
- **Object-stream co-requisite (new):** page-tree nodes live only inside `/ObjStm` in this corpus;
  C1's xref-stream work must include object-stream decoding or it still resolves no page.
- **Corpus-note enrichment (minor):** item 4's true origin is a Canon iR-ADV C5840 scan later run
  through Acrobat Paper Capture; the note recorded only the Acrobat producer. No contradiction.

## Scope attestation / self-check

- `git rev-parse --show-toplevel` = the wt-m5t093 path; HEAD was `6cc93092` at start; tree clean.
- Only the two allowed paths modified; forbidden paths (`services/`, `apps/`, `packages/`, `tools/`,
  `.github/`, and the corpus note) untouched — confirmed by `git status` / `git diff --stat` before
  commit.
- No ledger CLI, no `git push`, no `gh`. One commit containing only the two allowed paths.
- Evidence status form used throughout; every recorded command ran from the scratch subfolder cwd.

END-OF-REPORT
