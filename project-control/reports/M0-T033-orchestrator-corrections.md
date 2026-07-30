# M0-T033 — ORCHESTRATOR CORRECTION RECORD (C1, C2, C3)

Author: orchestrator (main session, Opus 5 under the D-004-R307 availability exception).
Raised by: `control-plane-verifier` (C1–C4) and `code-reviewer` G3 (C1–C3); `security-reviewer` G5
independently raised C1 as its OBS-3.

These corrections are **blocking for acceptance** per the gate-verdict semantics in
`.claude/rules/project-control.md` (a reviewer verdict of "PASS with required corrections" is
recorded as PASS, and the corrections must be applied and validated before acceptance). They are
recorded here rather than by editing producer evidence, so the producer's report stays exactly as
submitted.

**Identity safety.** Every correction below lands under `project-control/`, which
`_MANIFEST_EXCLUDE_PREFIXES` excludes from the content manifest. The reviewed content identity
`cd8f93b76116c1e43b84bb0aa54f5ad621ddc16ae5e0a932cdfe86f65a8e1665` is therefore unchanged, and no
completed gate is invalidated. Verified empirically before and after (§4).

---

## C1 — AS-12 literal containment miss. ORCHESTRATOR-AUTHORED DEFECT, not a producer escape.

**Finding.** Two files in the branch diff fall outside the packet's `allowed_paths`:

| File | Why it is there | Author |
|---|---|---|
| `project-control/reports/M0-T033-evidence-map.json` | `_directive_submit_check` **refuses an in-regime submit without `--evidence-map`**. The packet mandates the lifecycle that mandates this file, yet omits the path. | orchestrator, commit `8fd0019` |
| `project-control/state.json` | Written automatically by `sync_state()` during the orchestrator's own `submit`. The packet lists `state.json` under `forbidden_paths` while D-004-R372 mandates the lifecycle that writes it. | orchestrator, commit `1e86cd7` |

**Attribution — stated plainly.** This is a **packet-drafting defect authored by the orchestrator**,
not by the producer. The producer's own commit `6592b89` touched exactly three files, every one
inside `allowed_paths`. Three independent reviewers verified producer containment as clean. The
packet I wrote was internally inconsistent: it forbade a file the lifecycle it mandated would
necessarily write, and omitted a file the CLI structurally requires.

**Disposition.** The packet's `allowed_paths` is corrected to include the evidence map, and
`allowed_paths_note` now records both entries explicitly as orchestrator-lifecycle paths. The
`forbidden_paths` entry for `state.json` is qualified rather than deleted, so the original intent
(the producer must never write it) is preserved while the CLI's own write is acknowledged.

D-004-R342 authorizes *"M0-T033's own packet **and reports**"*, so the evidence map was authorized
by the owner's text all along; only the packet's enumeration was incomplete. Recording this rather
than letting AS-12 pass silently is the point — both reviewers were explicit that it must not pass
silently.

**Forward action (C3 of the control-plane verifier):** list the evidence-map path in `allowed_paths`
at contracting time for every future in-regime packet.

---

## C2 — Stale `tools/test_project_control.py` line citations in the producer report.

**Finding.** Citations in producer-report §§2–5 drifted when the test file grew during rework. Every
cited assertion **exists and was located by the reviewer**; no claim is false in substance, but a
pointer offered as proof should resolve when followed (D-004-R413).

Corrected anchors, as verified by the `control-plane-verifier`:

| Producer report says | Claim | Actual location |
|---|---|---|
| `:1837-1854` | ast source proof | **1881-1899** |
| `:1868-1869` | `assert "M0-T027" not in src` | **1913-1914** |
| `:1805-1815` | `gate()` regression proofs | **1841-1879** |
| `:1764-1775` | normal producer + varied `required_gates` | **1802-1810** |
| `:1718-1722` | malformed roster on the normal path | **1750-1752** |
| `:1958` / `:1968` / `:1980` | `ALL_TESTS` / S10 entry / summary print | **1959 / 1969 / 1981** |

**Disposition.** Recorded here as an orchestrator note with corrected anchors — the option both
reviewers offered — rather than editing the submitted producer report. The producer's evidence
stays byte-identical to what was reviewed and gated. Note the contrast the reviewer drew: all
`tools/project_control.py` citations and all ten `_rec` line numbers in §5A.3 are **exact**; only
the §§2–5 test-file anchors drifted.

---

## C3 — The OQ-2 whitespace-tightening description is understated.

**Finding.** Producer-report §3 describes the tightening as affecting `" orchestrator "` only. Two
reviewers independently enumerated a wider effect. The tightening also newly refuses:

- `[" backend-x "]` when the producer is `backend-x` — a whitespace evasion of the **producer**
  identity check, not just the reserved identity;
- whitespace-only reviewer names such as `[" "]` and `["  ", ""]`;
- (G5, at base) `['   ']` and `['  orchestrator  ']`, both of which **PERMITTED at base**.

Direction is unchanged — uniformly fail-closed — but the breadth is greater than stated. Real-ledger
impact remains nil: of 76 task packets, zero verdicts change for whitespace reasons.

**Disposition.** Corrected description recorded here. Both reviewers ruled the tightening ACCEPTABLE
and IN SCOPE, with the G3 reviewer noting it is not optional: without normalization,
`" orchestrator "` would count as a usable independent reviewer, which would defeat the *substance*
of D-004-R350. Stripping is what makes R350 actually hold.

---

## C4 — Carried forward, NO action in M0-T033 (out of authorized scope, D-004-R343)

Recorded so they are known chosen state rather than assumed invariants. None is a defect in this
change; all are pre-existing and verified byte-identical to base.

- **OBS-1 (control-plane-verifier).** Once `producer_agent == "orchestrator"`, a **new** G0/G7
  administrative record becomes unrecordable, because `gate()`'s administrative branch refuses
  `producer == reviewer` while G0/G7 require `reviewer == "orchestrator"`. Verified immaterial for
  M0-T027: its G0 already exists as PASS/administrative, it requires no G7, G2 is recordable, and
  G3/G5 are recordable by its three rostered reviewers. **OPTION B is structurally completable.**
  Flagged in case a future G3/G5 FAIL ever requires a re-recorded administrative gate.
- **OBS-2 (control-plane-verifier) / §3.1 (G5).** `claim()` never restricted the reserved identity:
  it sets `producer_agent = a.agent` with no check, and `_directive_claim_check` never references
  its `agent` parameter. Independently confirmed by the orchestrator. So `claim --agent
  orchestrator` was always accepted for any task type, and the new exception is **stricter** than
  the pre-existing claim path. The guard was never the sole defense.
- **OBS-3 (control-plane-verifier) / OBS-1 (G5).** `accept()` does
  `sorted(set(t.get("required_gates") or []))`, which raises `TypeError` on a non-iterable and
  enforces **zero** gates on a falsy value. Fail-loud or fail-closed, never fail-open; pre-existing
  and out of scope here. Candidate follow-up: a non-empty `required_gates` assertion in `accept()`
  and/or `new_task()`.
- **OBS-4 (control-plane-verifier) / OBS-2 (G5).** Reserved-identity comparison is exact-match, so
  `"Orchestrator"` is not recognized as reserved. Unchanged from base; `gate()` compares against the
  same exact string, so no split-brain arises.
- **OBS-1 (G3).** S10 block 6 asserts `"amend" in stderr`, which every roster refusal contains, so
  it proves fail-closed but not fail-closed-for-the-stated-reason. The reviewer demonstrated a
  mutant that reads malformed input as an empty list and still passes S10. R367's actual text
  ("fails closed WITHOUT a traceback") **is** verified, so this is a precision note, not a defect.
  Closing it would mean asserting `"malformed" in r.stderr` for the malformed cases.

---

## Convergent independent rulings (D-004-R415 satisfied)

All three reviewers ruled **independently** — the G5 reviewer explicitly recorded that it formed its
conclusion before reading the others' positions, and reached the same verdict by a different route.

| Open question | Ruling | Status |
|---|---|---|
| **OQ-1** required_gates/task_type asymmetry, R352 vs R368 | **R368 DOMINATES — leave as built** | Unanimous, 3/3, independently derived |
| **OQ-2** whitespace-stripping tightening | **ACCEPT** (proved monotonically tightening; makes R350 actually hold) | Unanimous |
| **OQ-3** AS-11 literal-grep interpretation | **ACCEPT the producer's reading**; R345 satisfied absolutely (0 occurrences of `M0-T027` in the module) | Unanimous |
| **OQ-4** 42-vs-52 derivation discrepancy | **RESOLVED**; root cause was amendment 10 landing at a child of the producer's base | Reconfirmed independently |
| Negative-control re-run at the advanced base | **NOT REQUIRED** | Unanimous; G5 matched every NC traceback line against the HEAD test file, G3 superseded them with six of its own mutants |

The strongest OQ-1 ground, from G5: extending the validation would close **zero** exploitable paths,
because the permissive outcome is reachable through a **well-formed** value — `required_gates: []`
passes `_roster_strings` as valid. A control an adversary bypasses with a well-formed value is not a
security control.

---

## Also recorded: FINDING F-1 is more severe than the producer disclosed

The producer reported that a bare-string `reviewer_agents` of `"rev-a"` iterated character-wise and
passed the base roster check. Two reviewers and the orchestrator independently established it is
worse. At base, on the reachable **non-orchestrator** path:

```
reviewer_agents = "orchestrator"   -> PASS  (fail-open)   # the very identity R350 excludes
reviewer_agents = "rev-a"          -> PASS  (fail-open)
reviewer_agents = "x"              -> PASS  (fail-open)
reviewer_agents = {"a": "b"}       -> PASS  (fail-open)
reviewer_agents = 7                -> RAISE TypeError
producer_agent  = [...] / int      -> RAISE AttributeError (uncaught traceback to the operator)
```

HEAD refuses all of them with explanatory messages. The base guard could be defeated by the exact
reserved identity it existed to exclude. Disclosing this as a finding rather than folding it
silently into the diff is the behavior the evidence regime is meant to produce, and it makes this
change a net security improvement independent of the feature it enables.

---

## 4. Identity-neutrality proof

```
content identity BEFORE corrections : cd8f93b76116c1e43b84bb0aa54f5ad621ddc16ae5e0a932cdfe86f65a8e1665
content identity AFTER  corrections : cd8f93b76116c1e43b84bb0aa54f5ad621ddc16ae5e0a932cdfe86f65a8e1665
UNCHANGED
```

`_MANIFEST_EXCLUDE_PREFIXES = ("project-control/",)`, so amending the packet and adding this record
cannot move the manifest. `tools/project_control.py`, `tools/test_project_control.py` and
`docs/GATES_AND_CHECKPOINTS.md` — the three files that actually drive the identity — are untouched
by these corrections.
