# M5-T056 producer report — DB-036 condo-surface rider cluster (concise resubmission)

Task **M5-T056** (frontend). Directive refs: D-066-R001, D-073-R006, D-077-R002/R003.
Scope: close DB-036 riders (b)/(c)/(e)/(f)/(g) on the condo surfaces and (h) on the
condo-records API. DB-036(a) (slash-district `boundedToken` charset) and (d) (substitution
coupling) are deliberately untouched — they bind other future packets.

## Resubmission shape (why this pass is concise)

This pass **changes no code**. The seven code/test files are byte-stable at the identities pinned
in §1–§7. Per the resubmission instruction, the **per-file patches are supplied out-of-band by the
supervisor's bounded per-file collection** (with enough surrounding source context to assess parser
behavior and guard preservation); duplicating full patch text in this report does **not** resolve
the collector truncation the prior pass hit, so this report no longer embeds the diffs. It keeps:
per-file **git blob digest bindings** + **line anchors** + the **rider→change mapping**, the
**parser-behavior and guard-preservation prose** (§9), the **actual** documented-command results
(§10), the **preserved prior wrong-cwd executions** as separate evidence (§11), and the
**explicitly-pending** web-suite/required-check CI owed at the pushed SHA (§12).

## Digest binding (how a reviewer verifies identity)

Each row carries the file's **git blob object id** as `<old-blob> → <new-blob>`. `<new-blob>` is
git's content hash over the **LF-normalized** blob (this repo normalizes EOL to LF on commit), so it
equals the blob at the commit the controller freezes. Read-only reproduction after the controller
commits: `git rev-parse <pushed-sha>:<path>` (or `git hash-object` on the LF-normalized working file)
must equal the `<new-blob>` here, and the supervisor-collected per-file patch applied to `<old-blob>`
yields `<new-blob>`. Working-tree HEAD at this report = `92b0d265` (the claim seam); the eight files
(seven code/test + this report) are uncommitted working-tree changes on top of it (commit/push is
the controller's).

`apps/web/src/components/architect/ReportView.tsx` is a permitted path but is **UNCHANGED** (§9) and
is not one of the eight.

## §1–§7. Per-file identity, anchors, and rider mapping

**§1 `apps/web/src/lib/condo-records.ts`** — parser + view type.
Blob `020255b01ef7bb698d525b8b5f21c039e7e6e79d → 35abf32891164ce8c4305adb2857f608bd273be4`.
Anchors: import (`+37`); `recordedZoningStatus` on `CondoBaseLotRecord` (`+86..91`);
`enteredBbl`/`enteredLotClass`/`billingBblStatus`/`recordedZoningDependency` on `CondoRecordsView`
(`+131..167`); `enteredBblValue` parser (`+262..273`); per-lot status fallback in `baseLotRecords`
(`+284..289`); `documentView` wiring (`+349..364`).
- **(b)** `enteredBblValue` parses the entered BBL through the shared `lib/bbl.ts` validator
  READ-ONLY; a well-formed value is carried, anything else is an explicit `null` (never invented).
- **(e)** `baseLotRecords` mirrors the api's `recorded_zoning_status`, with an honest fallback to
  `"recorded"|"unknown"` derived from the zoning value when the source omits it; `documentView`
  parses `recorded_zoning_dependency`.
- **(g) preservation:** `boundedTimestamp` (colons + `+` kept) is untouched; the parser does not
  reroute timestamps through `boundedToken`, and the `boundedToken` charset is UNTOUCHED.

**§2 `apps/web/src/components/architect/PropertyOverview.tsx`** — single decision + shared section.
Blob `4a82771e41e4beb314137acde55632268a8dce5f → 3d61696be951bd4202aa374d9f05073b1249779e`.
Anchors: substitution `<h2>` + entered fallback (`+228,+231`); records branch derivations + labels +
gated notices + `<h2>` (`+239..271`); conflict-panel copy (`+280`).
- **(b)** entered vs billing under distinct labels; a unit input's billing lot is an explicit
  "not recorded (unknown)", never the entered unit BBL relabelled.
- **(c)** dangling reference repaired to "under the development limits above" (records intro) and
  "The development limits above govern." (conflict panel); no "professional-review determination
  above" text remains.
- **(e)** divergent notice gated on `anyZoningRecorded`; ZTLDB gap note gated on
  `anyZoningUnknown && recordedZoningDependency`; `zoningGapNote` is scope-aware (partial vs full-gap).
- **(f)** `City records for this condo` and `Recorded base lot for this condo` are real `<h2>`.
- **Shared guard (unchanged):** the render still consumes the ONE `deriveCondoSurface` decision; the
  new locals (`anyZoningRecorded`/`anyZoningUnknown`/`enteredLot`/`billingLot`/`zoningGapNote`) are
  render-branch derivations from already-parsed view fields, not a second decision point (§9).

**§3 `apps/web/src/lib/__tests__/condo-records.test.ts`** — parser pins.
Blob `12e35fa1cbcd92dffa7a31ea92c4874499f99566 → 84bb42184a9d8168e02f1334b5a88a70ba39f69c`.
Anchors: `ZONING_DEPENDENCY` fixture (`+33..35`); multi-lot fixture status fields (`+87..104`); unit
fixture entered/billing split (`+115..122`); retrievedAt value pin in the existing multi-lot test
(`+181..187`); unit-input entered-vs-billing pins (`+199..214`); new `DB-036 rider parsing (M5-T056)`
block (`+410..471`). Pins (b) entered≠billing identity, (e) per-lot status + dependency + fallback,
(g) the char-for-char retrievedAt round-trip (a `boundedTimestamp→boundedToken` revert fails it).

**§4 `apps/web/src/components/architect/__tests__/condo-resolution-display.test.tsx`** — screen render.
Blob `6692b38313a7189aae427bbf7033a0f02976ca98 → cb6d134dc2b0ccf191d12be6696667d3b3c37087`.
Anchors: channel fixtures incl. new no-zoning fixture (`+86..161`); conflict-panel dangling-ref
repair in the existing brief test (`+439..453`); new `DB-036 rider rendering (M5-T056)` block
(`+706..796`). Renders (b) entered-vs-billing labels, (c) repaired reference, (e) no-zoning vs mixed
notice gating with the ZTLDB source named in plain language, (f) real `level:2` headings, (g) the
exact retrievedAt VALUE on the surface.

**§5 `apps/web/src/components/architect/__tests__/report-view.test.tsx`** — brief render.
Blob `b4f2646fb1ae8bf8708ef36b0e999e2684566cdc → 5eddbe73f7da8794baa853390f5087c6eba83ef5`.
Anchor: new brief-surface DB-036(f)/(g) test (`+473..493`) — the shared section renders under a real
`level:2` heading on the brief and value-pins the exact `retrieved`/`dataset version` strings
end-to-end (proves the inheritance through the ONE shared component, no second data path).

**§6 `services/api/app/api/v1/condo_records.py`** — rider (h): 422 repr length cap.
Blob `b21e34fd29362bd4264a1118e781d00cf7c07f7e → 73d4e5047004e8a1c21150c2529348a75d203dac`.
Anchors: `MAX_RAW_VALUE_REPR_CHARS = 256` + marker (`+135..143`); `_capped_raw_value` helper
(`+231..238`); applied to `detail.raw_value` in the 422 branch (`+591..597`). The repr is ALREADY
`repr()`-sanitized upstream in `app.connectors.bbl`; this bounds **length only**, so a repr at or
under the cap is byte-identical and every ordinary 422 is unchanged.

**§7 `services/api/tests/api/test_condo_records_api.py`** — rider (h): binding tests.
Blob `06ba2dcbff059b02278696bc347dd522c683c33a → 2f00411940d80b8336ca0cc2490946c8054bdf0e`.
Anchors: repr-cap pack (`+564..625`) — short repr byte-identical; oversized repr truncated to ceiling
+ marker with exact length; end-to-end oversized entered BBL 422 length-capped; end-to-end short
malformed input uncapped and verbatim.

## §8. This report

`project-control/reports/M5-T056-producer-report.md` is the eighth changed file. Its own blob digest
is self-referential; the controller captures it at the freeze commit alongside the seven §1–§7 digests.

## §9. Shared-guard context (UNCHANGED — preservation binding)

- **One monotone decision.** Both surfaces (screen `PropertyOverview` and printed `ReportView`)
  render from the SAME `deriveCondoSurface` decision through the SAME `CondoRecordsChannelSection`.
  This pass adds NO second decision point: the §2 changes are render-branch derivations from
  already-parsed view fields, not a new withhold/allow decision. The withhold/fail-safe direction is
  unchanged; `deriveCondoSurface`/`channelWithholdsAllowances` are outside this packet's diff.
- **`ReportView.tsx` is UNCHANGED** (permitted path, not one of the eight). It already reads the
  shared `useCondoRecords → deriveCondoSurface` decision (`ReportView.tsx:45-49`) and renders the
  shared `CondoRecordsChannelSection` under `DevelopmentLimits` (`ReportView.tsx:91-97`), inherited
  from accepted M5-T052, so the brief inherits every DB-036 fix through that one shared component. §5
  binds the brief surface (real `h2` + exact timestamp value) without a second data path.
- **Sanitizer boundaries respected.** Timestamps stay on `boundedTimestamp` (colons + `+` kept — §3
  value-pins it). The `boundedToken` charset is UNTOUCHED — DB-036(a) (slash-district charset, e.g.
  `R7-2` reaching a token field) binds the future zoning-propagation packet, and DB-036(d)
  (substitution coupling) binds substrate-substitution; neither is touched here.

## §10. Documented-command results (actual, this resubmission)

All four documented commands re-run for this resubmission. The api commands ran **from
`services/api`** (the packet's binding COMMAND CWD); the modularity check ran **from repo root**.
Outcomes are the actual observed results at the working-tree identity pinned in §1–§7. The supervisor
collects each command's argv, exit code, and output digest.

| # | documented command | cwd | actual outcome |
|---|---|---|---|
| 1 | `python -m ruff check .` | `services/api` | **exit 0** — `All checks passed!` |
| 2 | `python -m pytest tests/api/test_condo_records_api.py -q` | `services/api` | **exit 0** — `19 passed in 1.83s` |
| 3 | `python -m pytest tests/api -q` | `services/api` | **exit 0** — `501 passed in 20.29s` |
| 4 | `python tools/modularity_check.py --check` | repo root | **exit 0** — `selected 455 files; failures 0; warnings 20` |

The 20 modularity warnings are pre-existing review-signal / symbol-ceiling advisories on `tools/**`,
`services/api` connectors/rules/scenario modules, and `surveyReview/types.ts` — **none on any of the
eight M5-T056 files**; advisory, exit 0.

## §11. Prior wrong-cwd executions (preserved as separate evidence, not overwritten)

The earlier evidence pass ran the api commands from the **worktree root** (wrong cwd). Those results
are preserved verbatim below; they are **command-routing failures, not code failures**, now proven by
the correct-cwd §10 green with no code change:

| documented command | cwd the prior pass used | prior outcome (preserved) |
|---|---|---|
| `python -m ruff check .` | worktree ROOT | exit 1 — 45 findings, all in `tools/**` + `project-control/reports/**`; zero in `services/api/**` or any allowed path |
| `python -m pytest tests/api/test_condo_records_api.py -q` | worktree ROOT | exit 4 — `file or directory not found: tests/api/...`; zero collection |
| `python -m pytest tests/api -q` | worktree ROOT | exit 4 — same; zero collection |
| `python tools/modularity_check.py --check` | worktree ROOT (correct) | exit 0 — 455 files; 0 failures |

- The prior ruff exit 1 scanned the whole monorepo from root; the 45 findings were all in `tools/**`
  and `project-control/reports/**`, **none** in `services/api/**` or any M5-T056 allowed path. Those
  root-level findings are **out of scope and were NOT repaired** (packet + resubmission instruction
  forbid touching unrelated root-level lint).
- The prior pytest exit 4 was zero-collection: the api suite is rooted at `services/api/` and never
  collects from the worktree root (`.claude/rules/CODING_RULES.md`). Run from `services/api`, the
  targeted file passes (19) and the full suite passes (501) (§10 #2–#3).

No code was changed to obtain the §10 green; only the cwd was corrected to the documented one.

## §12. Web suites + required-check CI — owed to the controller at the pushed SHA (explicitly pending)

Web behavior proves **only in CI on the pushed head** (thin client; no npm/npx/node locally). The
eight files are currently **uncommitted working-tree changes** on top of HEAD `92b0d265`, so there is
**no pushed implementation SHA yet** and therefore **no web-suite / required-check CI result to
bind**. This is explicitly **not** claimed green from local reasoning.

Owed to the controller (commit/push + lifecycle are the controller's, ADR-005):
- Commit the eight files, push the branch, and at the resulting **pushed implementation SHA** capture
  green for the web suites `apps/web/src/lib/__tests__/condo-records.test.ts`,
  `apps/web/src/components/architect/__tests__/condo-resolution-display.test.tsx`, and
  `.../report-view.test.tsx` (§3–§5), plus the repo's required checks (web + api CI jobs). Bind those
  conclusions to that SHA in the gate record.
- After commit, the §1–§7 blob digests equal `git rev-parse <pushed-sha>:<path>` for each path, so
  review has digest-bound identity without a re-derivation from this producer.

## §13. Authority / scope

- Changes stayed within the nine allowed paths; the only file edited on this resubmission is this
  report (§8). No unrelated root-level lint finding was repaired; no controller-owned file was touched.
- Commit, push, gate records, and every lifecycle transition remain the controller's. This report is
  submitted for **independent review** (code-reviewer, qa-engineer, security-reviewer,
  human-journey-reviewer, directive-compliance-verifier) before any completion or acceptance.

## §14. Discovery / next-packet exposure (orchestrator sweep)

- DB-036(b)/(c)/(e)/(f)/(g)/(h) closed here; (a)/(d) untouched by design.
- A future zoning-propagation packet wiring real per-lot zoning routes through the per-lot
  `recordedZoningStatus` seam and must add a `boundedZoningDistrict` (slash-safe charset) BEFORE any
  `/`-bearing district (e.g. `R7-2`) can reach `boundedToken` — that is DB-036(a).
- The view now also exposes `enteredBbl`, `enteredLotClass`, `billingBblStatus`, and
  `recordedZoningDependency`, and the API caps `detail.raw_value`; hand these to the next packet that
  touches these surfaces as guard context.

## Digest binding (orchestrator-captured at harvest; producer hashing not broker-approved)

LF-normalized sha256 (first 16) of the 7 material files + this report at the task-branch
harvest snapshot (the report digest was taken immediately BEFORE this appended section):

- `9589d43fc1e49c4e` apps/web/src/components/architect/PropertyOverview.tsx
- `bea9d429fa976894` apps/web/src/components/architect/__tests__/condo-resolution-display.test.tsx
- `8ee3e2e05f7ac343` apps/web/src/components/architect/__tests__/report-view.test.tsx
- `f9156628bfb8bee4` apps/web/src/lib/__tests__/condo-records.test.ts
- `5731a801987ea828` apps/web/src/lib/condo-records.ts
- `18223ea2418dca36` services/api/app/api/v1/condo_records.py
- `bfd61b33dfd9734d` services/api/tests/api/test_condo_records_api.py
- `86baf3ec12f63395` project-control/reports/M5-T056-producer-report.md (pre-append)

Orchestrator self-checks in this worktree at harvest (2026-09-20, loop-3 runs 04-05 close):
`python -m ruff check .` (services/api) = All checks passed; `python -m pytest tests/api -q`
= 501 passed; `python tools/modularity_check.py --check` = exit 0. Web suites prove in CI at
the pushed head per the packet.
