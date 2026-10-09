# M0-T106 G5 security review — DELTA round 2 (VERBATIM reviewer return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Reviewer: security-reviewer (same
agent resumed with round-1 context, 2026-08-27). Verdict returned: **PASS**.

---

# G5 Security Gate Report (DELTA re-review) — M0-T106 (D-024 Amendment 3 unit E)

**Gate:** G5 (independent security review, delta round 2)
**Reviewer:** security-reviewer (read-only)
**Verdict: PASS** (round-1 ADV-1 and ADV-2 genuinely closed; ADV-3 correctly residual; no new blocking findings)

## Frozen identity verified
- New deliverable commit: `5e60a0d39dfe4c6eaa479924e4291285f9e15f00` (confirmed via `git log --oneline -1`)
- New content_manifest_sha256: `4d31dba2e03f0644c72725010235f95d68fb034cb82c78c8f3b560d6aa123293` (recorded; identity managed by orchestrator)
- Live HEAD: `6cc9cf258fec4390c09478d99611281bac9a9581`
- Working-tree copies of all six subject files are **byte-identical** to `5e60a0d` (`git diff --quiet 5e60a0d -- <file>` clean for each).
- Applicable directive requirements unchanged: D-024-R152, D-024-R162, D-024-R174 (carried R045, R154).
- Repo PUBLIC. Forbidden-path check on the delta (`git diff --name-only c3f3768..5e60a0d | grep .claude/settings/hooks`): **NONE (clean)** — no settings.json/hooks/ORCHESTRATION_POLICY changes.

## Production-code delta (`git diff c3f3768..5e60a0d`)
Four production files changed, all additive/behavioral, no new imports, no network/exec/subprocess introduced:
- `event_bus.py`: `publish_typed` dedup key now also digests `record.measurements` (F1).
- `goal_checkins.py`: `MAX_SCHEDULE_COUNT=64` cap (F7); `IdleCapVerdict` dataclass replaces `int|None` return (F4); `record_checkin` requires a `sequence` discriminator (F2).
- `goal_outcomes.py`: measurement key `goal_token_spend` → `goal_spend_tokens` (F3).
- `goal_contract.py`: campaign-scale tripwire widened (F5).
- Test + fixture: regression coverage for each fix (F6 + F4/F5).

## Fix-by-fix security verification

### F1 — measurement-aware `publish_typed` dedup key — PASS
The key input gained `"measurements": {name: m.to_dict() for ...}`. `Measurement.to_dict()` returns only `{value, label, category, detail?}` — **no timestamp, no volatile field** — and `idempotency_key` serializes it deterministically (`json.dumps(sort_keys=True, default=repr)`). Record-level `timestamp_utc` remains **excluded** from the key.
- **No injection/collision surface:** measurements originate from the `ingest_goal_status` builder (controlled fields); a caller cannot inject a colliding structure, and sha256 collision is negligible.
- **Round-1 §3 invariants preserved on the changed path** (probed): two status snapshots that advance only their numbers **both persist** (false-dedup closed); an identical snapshot **still collapses** (dup_count=1); a UUID in a measurement-bearing status attribute is masked on disk (`raw uuid on disk: False`, `SESSION sha256` present); a bounds-exceeding typed record raises `TelemetryBoundsError` with sequence rolled back and the seen-set empty (remember-after-append intact). `_store` is unchanged in the diff.

### F2 — `record_checkin` requires a `sequence` discriminator — PASS
- **No leak in the refusal:** the raised `GoalCheckinError` message is a static string; probe with `secret_field="sk-DEADBEEF..."` and `running_tasks` confirmed neither payload value appears in the message. Nothing is persisted on refusal (`stored_records == ()`). A non-Mapping payload is also refused.
- **Fail-visible is sound for a passive observer:** a silent dedup collapse of two genuinely-distinct check-ins would undercount and defeat the idle-cap-of-3 corroboration (the G4-M1 finding); surfacing the misconfiguration is the correct direction and matches the module's documented fail-visible philosophy. The lower-level `ingest_checkin` still tolerates a missing sequence for non-persisting inspection, so the refusal is scoped precisely to the durable path.

### F3 — `goal_token_spend` → `goal_spend_tokens` (ADV-1 closure) — PASS
- **Delimited-segment analysis:** `SENSITIVE_KEY_PATTERN` = `(?i)(^|_)(...|token|...)($|_)`. In `goal_spend_tokens` the substring `token` is followed by `s`, not `$`/`_`, so `(^|_)token($|_)` does **not** match. The `_tokens` suffix is the pattern-safe family.
- **Read-back proof (probed):** the stored `goal_spend_tokens` measurement is READABLE (`value: 12345`, no `[REDACTED]`).
- **Redaction NOT weakened:** in the same record, a real secret in `last_reason` still redacts to `[REDACTED:...]` (raw `sk-ABCDEF` gone), and home paths in `condition` still mask to `[HOME]` (MLFLL gone). String-value secret/path redaction is key-name-independent, so unblinding this count does not open any leak.

### F4 — `IdleCapVerdict(cap, known)` — PASS
New frozen dataclass separating documented-uncapped (`cap=None, known=True`) from version-unknown (`cap=None, known=False`) — closes the ignorance/no-cap conflation. **Public-interface change is safe:** the only consumer of `idle_checkin_cap` in production is its own definition; the sole other consumer is the test file (`git grep` confirmed). No external module breaks. No security surface (pure data).

### F5 — widened campaign-scale tripwire — PASS (1 informational note)
Added alternations for the four proven-slip verb phrasings and "the rest of the …". This is a **fail-closed-biased widening** (R152: refusing more campaign-scale phrasings is the safe direction). The regex uses simple bounded alternations with no nested quantifiers over overlapping classes → **no ReDoS**, and runs on the ≤4000-char condition. Tests add all four phrasings; all refused.
- *Informational (non-blocking):* the widening may also refuse some legitimate single-task phrasings that contain "complete/finish/deliver the project|milestone|…" — this is the documented fail-closed bias ("a rare false refusal beats a campaign-wide goal"); the caller rewrites the wording. Availability tradeoff, not a security defect.

### F7 — `MAX_SCHEDULE_COUNT=64` cap (ADV-2 closure) — PASS
Probed: `count=64` returns 64 offsets; `count=65` raises `GoalCheckinError: count 65 exceeds the schedule bound 64` (fail-visible). The prior unbounded-`count` advisory is closed with a defensible defense-in-depth bound.

### F6 — added coverage — PASS
Test-only additions (constraint-poison R045 path; `reason_excerpt` ≤160 bound) re-assert behavior verified in round-1. No production change.

## Delta-scope conclusions (as requested)
1. **ADV-1 genuinely closed** (F3 — readable read-back proven, secrets/paths still redact). **ADV-2 genuinely closed** (F7 — cap + fail-visible proven). **ADV-3 correctly residual** — `publish_typed`'s key now digests attributes AND measurements, both sourced from controlled ingest builders that never inject the reserved `idempotency_key`/`bus_sequence` keys, and `_store` overwrites those on store; the theoretical metadata-poisoning path remains unreachable in practice. No action required.
2. **No new surface in the diff:** no new imports (IdleCapVerdict uses the already-imported `dataclasses`; the measurement digest uses `record.measurements`/`Measurement.to_dict`, no new import), no network/exec/subprocess, and no unbounded growth (F7 *adds* a bound; the measurement digest is bounded by the fixed ingest schema).
3. **Packs re-run green:** `test_agent_supervisor_goal_integration.py` + `test_agent_supervisor_event_bus.py` → **76 passed**; reused security modules (`bounded_contracts` + `telemetry_core`) → **106 passed**. No regression from the additive/behavioral changes.
4. **Fresh leak scan (changed bytes):** subject production files + fixture are **clean** (the `@dataclasses.dataclass` hits are email-regex false positives; the fixture is clean); the test file carries only the intended `"MLFLL"/"Users"` masking-assertion needle.

## Informational (non-blocking) — report-file path exposure
The changed review-report artifacts under `project-control/reports/` (e.g. `M0-T106-G5-security.md`, G3/G4 reports embedding my round-1 output) contain absolute `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\...` paths and the deliberately-fake probe strings (`sk-ABCDEF…`, AWS's documented `AKIAIOSFODNN7EXAMPLE`, the invented `C:\Users\MLFLL\secrets\prod.env`). These are control-plane evidence files, not the production subject files; the exposed username is already pervasive across dozens of committed repo files (pre-existing pattern), and no real secret is present. This does not affect the G5 verdict but is flagged for hygiene: reviewers/producers should prefer repo-relative paths in committed reports for a PUBLIC repo. <!-- secretscan:allow reviewer adversarial demo value; AWS documented example key AKIAIOSFODNN7EXAMPLE, fake/elided, gate-report evidence -->

## Requirement security-obligation status (unchanged from round-1, re-confirmed)
- **R045** (carried): worker-facing condition text fully validated by `assert_worker_text_clean`; constraint-embedded quota now has explicit regression coverage (F6). PASS.
- **R152**: one-task binding + widened campaign tripwire + foreign-task detection. PASS (stronger than round-1).
- **R154** (carried): passive controller-side check-in math; no worker messaging/pings into Fable context; no worker token quotas. PASS.
- **R162**: `is_turnover_seam_trigger` = context-overflow emergency-buffer turnover; no statusLine/cache code altered. PASS.
- **R174**: bounded condition + no-progress structural handling + background check-ins (now with a fail-visible discriminator contract) + no worker token pressure. PASS.

(Full requirement-to-evidence verification remains the directive-compliance-verifier's `verification.json` pass — producer ≠ verifier.)

**Verdict: PASS.** The correction round closes both round-1 advisories with proven, security-safe behavior; every round-1 §3 invariant holds on the modified `publish_typed` path; no new security surface, no regression, subject files leak-free. One informational availability note (F5 fail-closed bias) and one informational report-hygiene note — neither blocks acceptance.
