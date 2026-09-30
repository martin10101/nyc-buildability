---
name: telemetry-redaction-latent-gaps
description: Two non-blocking latent gaps in the D-024 Phase B telemetry redaction/accumulator subsystem (M0-T088) that B2 (M0-T089+) must close before ingesting transcript/SDK/subagent structures
metadata:
  type: project
---

Found during G4 QA of M0-T088 (D-024 B1 telemetry core, frozen SHA 23f0d80). Both are
ADVISORY / non-blocking for B1 (no B1 record reaches either path) but become live risks the
moment B2 ingestion of transcript/message/subagent structures lands.

1. **Prompt-like KEY with a list/dict value is NOT digest-withheld.**
   `telemetry_redaction.sanitize_structure` (`telemetry_redaction.py` ~L152-158) withholds
   prompt-like keys (`prompt`/`conversation`/`instructions`/...) only when the value is a
   `str`. A prompt-like key holding a LIST or DICT of short (<512 char) message strings is
   walked and stored verbatim (only escape/path/secret/bound applied). Verified:
   `{'conversation': ['hello secret worker text', ...]}` stored verbatim. Long-text (>512)
   bounding is the only backstop. §5.3/R044 wants "summaries and references, not
   prompts/transcripts". **Fix before B2:** recurse withholding into list/dict values under a
   prompt-like key; add a test with list- and dict-valued prompt keys.

2. **UsageAccumulator.snapshot reports a never-observed per-step token field as 0, not unknown.**
   `telemetry_ingest.py` ~L284-292: once `_steps_ingested>0`, any step field never present in
   any step reads `_step_totals.get(name,0)` -> value 0, label `provider-exact`, detail "sum of
   deduplicated per-step usage" WITHOUT the lower-bound caveat (that caveat is gated on
   `_malformed_steps`, not per-field absence). Defensible (absent Anthropic cache field
   conventionally = 0; it is a SUM of observed contributions, not a point snapshot) and thus
   NOT a correctness defect, but it is philosophically inconsistent with the status-line
   "absent -> unknown" rule and is untested for the fully-absent-field case. The tests always
   pass explicit `0` cache fields so the path is never exercised.

**Why:** these are exactly the kind of thing that passes B1 (correct for B1 records) yet leaks
or misreports under B2 payload shapes.
**How to apply:** when gating M0-T089+ telemetry ingestion, treat closing #1 as a redaction
requirement (with a red/green test) and re-decide #2's 0-vs-unknown for real provider payloads.

Reusable teeth technique that worked: copy the whole `tools/agent_supervisor` package + the
test file into OS temp (namespace package, no `tools/__init__.py`), run baseline, then apply
one string-replace mutation per guard test and assert the node goes red. 7/7 guard tests
(dedup, counter high-water, category cross-label, atomic write, unknown-not-zero, torn-line
count, matrix==live drift) flipped red -> real teeth. Repo files never touched.
