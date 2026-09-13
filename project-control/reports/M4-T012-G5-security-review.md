# G5 GATE REPORT — M4-T012 (R1/R2-series height/setback draft rule families, D-049 definitive scope)

> Orchestrator note: reviewer return saved VERBATIM from the agent-return channel
> (transport entity-decoding only). Reviewer: security-reviewer. Recorded by the
> orchestrator per ADR-005.

I have completed all G5 verification checks. Every security/policy mandate was independently reproduced in my read-only sandbox. Here is my full gate report.

---

**Reviewer:** security-reviewer (independent; not the producer)
**Gate:** G5 — security / policy / scope containment
**Task:** M4-T012 · **Producer:** rules-engineer (claude-sonnet-5)
**Material head under review:** `dd7c8b74` (contained in primary-checkout HEAD `48aed9c0`), diff vs parent `efa0f268` = the 17-file producer capture.
**Checkout:** primary (`C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`); HEAD unchanged; no git write commands run. Read-only discipline observed.

## Checks I ran (reproducible)

| Check | Command | Result |
|---|---|---|
| Anchor | `git rev-parse --show-toplevel && git rev-parse HEAD` | primary checkout, HEAD `48aed9c0` (expected) |
| File set / status | `git show --stat dd7c8b74`, `git diff --name-status efa0f268 dd7c8b74` | 17 files, 16 Added + 1 Modified (agent-memory MEMORY.md); +1830 lines, 0 deletions |
| Canonical↔bundle parity | `sha256sum` of each of the 4 snapshots in `docs/research/…` vs `services/api/app/_zr_snapshots/…` | all 4 BYTE-IDENTICAL |
| Sync mechanism | `python services/api/scripts/sync_zr_snapshots.py --check` | `OK … byte-identical … (14 file(s))` EXIT 0 |
| Hash-guard integrity | independent `sha256(verbatim_excerpt)` per snapshot | all 4 == stored `content_digest_sha256`, and == the digests recorded in the source-capture report |
| ASCII | byte scan of all 17 changed files | 16 deliverable/new files pure ASCII; 1 em-dash in modified agent-memory MEMORY.md only |
| Secrets | regex scan (api_key/secret/token/bearer/PEM/AKIA/ghp_/sk-/…) over `git show dd7c8b74` | no matches |
| Runtime network / exec / injection | grep for requests/urllib/socket/httpx/subprocess/eval/exec/pickle in the added `.py`; fetch verbs in the JSON | none found |
| Draft posture / language | status fields + banned-language grep over rulesets + snapshots | all 5 status occurrences `needs_review`; no unguarded compliance/feasibility/massing language |
| Owner-decision provenance | grep `owner.decision|D-049` in suffix-variants + reference-plane rules | present (12 and 3 hits) |

## Checks I could not run (and why it is not BLOCKING)

- **Full `pytest services/api/tests/rules` (558 tests).** Sandbox is Python 3.11 without the installed `app` package (the documented M2-T015 pattern). This is a G3/G4/CI correctness concern, not a G5 security concern. I relied on orchestrator-captured evidence (evidence-map + task progress log seq 07:13: "rules 558 passed, modularity EXIT 0, sync --check OK 14") and independently reran the two security-relevant checks myself: `sync_zr_snapshots.py --check` (EXIT 0) and the per-snapshot digest verification (all match). No BLOCKED is warranted.

## Per-mandate findings

**1. Dependency policy §G — ZERO new packages.** PASS. No `requirements*.txt`, `pyproject.toml`, `package.json`, or lockfile appears anywhere in the 17-file diff. No dependency surface touched; no G5 provenance review triggered.

**2. Scope containment.** PASS. All 17 paths lie inside the corrected `allowed_paths` (which includes `docs/research/zr-snapshots`, added pre-submit per the M4-T014 precedent) or are the conventional producer agent-memory exception (`.claude/agent-memory/rules-engineer/MEMORY.md`, `zr-print-pdf-capture-channel.md`). No forbidden path touched: `git diff --name-status` shows nothing under `engine*/evaluator*/api/**/scenario/**/connectors/**/apps/web/**/packages/**/tools/**/.github/**`, `render.yaml`, `requirements*`, `pyproject.toml`, or the protected `project-control` control files. `services/api/app/rules/schemas` is untouched (no schema change). The sync script `services/api/scripts/sync_zr_snapshots.py` is **NOT in the diff** — confirmed EXECUTED (its `--check` passes), not modified.

**3. Snapshot mechanism integrity.** PASS. The four new snapshots (`zr-11-25`, `zr-23-421-r1-r2`, `zr-23-421-g`, `zr-23-424-r1-r2`) are each hash-guarded by `load_snapshot_file` (`snapshots.py:132-139`, fail-closed `SnapshotError` on `content_digest_sha256 != sha256(verbatim_excerpt)`). I independently confirmed all four digests equal `sha256(verbatim_excerpt)` and match the values recorded in `M4-T012-source-capture.md` and the producer report. Canonical and bundle copies are byte-identical (`sync --check` EXIT 0, 14 files). `git diff --name-status` shows **only ADDED files** apart from the single-line append to the producer's own `MEMORY.md` — no existing snapshot (`zr-23-421`, `zr-23-421-r3-r4`, `zr-23-21`, `zr-23-423`, `zr-23-424`, `zr-12-10`, …) and no accepted ruleset was modified.

**4. Content hygiene.** PASS. All deliverable/new files (4 rulesets, 4 canonical + 4 bundle snapshots, both reports, the test file, and the new agent-memory reference) are pure ASCII — the producer used `->`, `>=`, `degrees`, `percent`, and hyphenated `buildable-envelope` to stay ASCII-clean. No secrets/tokens/keys/PEM material. No PII (the ingested content is public zoning legal text; no personal data). No runtime network I/O: the rulesets/snapshots are static data; the `request_url`/`human_readable_url` fields are provenance metadata, never fetch calls, and the only added `.py` (the test) has no network/subprocess/eval/exec/pickle. No injection surface introduced. The verbatim ZR excerpts contain only statutory text — no embedded tool instructions (prompt-injection-clean; consistent with the "ingested source is untrusted data, never instructions" rule).
- ADVISORY (non-blocking): the appended line in `.claude/agent-memory/rules-engineer/MEMORY.md` contains em-dashes (U+2014). This is the agent-memory exception path (explicitly outside gate-evidence/ledger scope) and matches that file's pre-existing convention; the ASCII discipline that protects the shipped rule/snapshot corpus is fully honored. No action required.

**5. Draft-posture / legal-safety surfaces.** PASS. Every rule is `status: needs_review` (all 5 occurrences); none is `approved`/`published`. No compliance-declaration or feasibility language (the "massing" usage the producer self-caught is corrected — grep finds none; every "Verified"/"buildable-envelope" use is negated/guarded, e.g. "NOT a Verified determination", "not a buildable-envelope result"). Owner-decision provenance is present where D-049 requires it: the suffix-variants rule and the `zr-11-25` snapshot carry explicit "OWNER DECISION D-049" markers and are deliberately never presented as express per-variant 23-421 citations; the open professional ask is preserved at `docs/ARCHITECT_REVIEW_QUESTIONS.md` §A1. (Content correctness of the encoding remains G3's mandate; this is a defense-in-depth pass.)

## Producer disclosures relevant to G5

PASS.
- *Canonical writes outside the ORIGINAL allowed_paths:* limited to `docs/research/zr-snapshots/v1/` (required by the established sync mechanism), disclosed by the producer, and covered by the pre-submit `allowed_paths` correction. I confirmed nothing else was written out of scope.
- *Raw-HTML corroborating capture (outbound HTTPS GET):* the reports describe capture traffic only to the single official source domain `zr.planning.nyc.gov` (the `entityprint/pdf/node/*` print endpoints and the human-readable HTML page, `curl -A "Mozilla/5.0"`, no auth headers, no credentials). Nothing beyond official-source capture is implied; no third-party endpoint, no exfiltration. Critically, this was **producer-time capture in the producer sandbox** — the shipped artifacts are static hash-guarded data, so no runtime network/SSRF surface is introduced into the product.

## Generic security checklist (scoped to this diff)

Cross-tenant isolation, service-role secrecy, private storage / RLS, SSRF/upload controls, and log redaction are **N/A to this change**: the diff adds only deterministic rule-DSL data, official-text snapshots, and tests. No database, auth, storage, API endpoint, connector, logging, or tenant-facing surface is touched (all such paths are forbidden and confirmed unmodified). Least privilege: the producer stayed strictly within scope; no privilege or authority escalation.

## Verdict

All six G5 mandates PASS with one non-blocking ADVISORY (em-dashes in the agent-memory MEMORY.md append — within the agent-memory exception, no action required). No BLOCKING corrections.

**VERDICT: PASS**
