# M0-T041 G5 security review — verdict preserved verbatim

**Reviewer:** security-reviewer (independent, read-only). **Recorded by:** orchestrator (producer backend-engineer ≠ reviewer).
**Reviewed:** HEAD `9a063d66d8d7233d5e65c36089f98c9cb56044ff` (producer code commit `cdab33d`; base `f65d716`). **Result: PASS — zero defects at any severity; INFO-1 advisory for the R595 activation gate.**

---

# G5 SECURITY GATE REPORT — M0-T041

## VERDICT: PASS
No critical/high/medium/low security defects. All six mandated security invariants hold, independently reproduced at HEAD.

## Scope verification
Producer commit `cdab33d` touches exactly 7 files, all in allowed_paths (3 modified supervisor modules, new sampler, 3 new test modules). The D-010 v4 requirement edits came from the separate orchestrator control-plane commit `a2a8cda` (directive-tracking files, not dependency manifests).

## Per-check results (all PASS)
1. **Fail-closed classifier integrity:** `QUOTA_EXHAUSTION_SIGNAL_VERIFIED=False` (derived from the corpus so flag and corpus cannot drift); classifier requires `verified_live AND matches`; the empty-shape guard makes a shapeless fixture match NOTHING (`matches` ends `return bool(self.return_codes) or self.stderr_regex is not None`); non-str stderr → False; exceptions → "". Reproduced live: every probe (documented candidate prose, 429 prose, unknown, non-str, verified-empty) returns "".
   **Honest blast radius:** the classifier is the sole producer of `quota_exhausted`, but it can never open an availability path — `available=True` is set only when a real process reports the exact model id; the classifier is consulted solely on the unavailable branch to name why. Even if `quota_exhausted` were returned, the switch is bounded by five constraints: orchestrator-role only; safe rotation seam only; walks the FIXED owner-configured immutable model chain; relaunches only on an entry that actually launches on that exact id; chain exhaustion = full STOP + owner notify. Net production blast radius today: **zero** (all fixtures unverified → classifier always ""; byte-identical to the prior unwired seam; loop SHADOW-ONLY). Prompt-injection defense: stderr passes `neutralize_untrusted` + 2000-char cap before the classifier; regex is simple word-boundary alternation, length-capped input — no ReDoS.
2. **Sampler attack surface:** stdlib-only (dataclasses/os/shutil/typing); no shell/network/env/secret access; size metadata only (`shutil.disk_usage`, `os.stat().st_size`), never content; paths supervisor-config-derived, not worker-influenced; `value=int(fn())` with conversion failure → outage → conservative pause, so no type-confusion route can make a trip comparison silently False; gauge names exactly match GAUGE_LIMITS.
3. **pending_prompt replay/forgery:** consumed marker drops the digest → resume guard (`not pending.get("digest")`) fails closed; only two writers of the record exist (legitimate WAIT parking + consume marker); no CLI/API can re-forge a digest; consume runs after the durable transition + audit event (CLI) and after the successful forward (loop) — no approval recorded without its authorized effect; same `journal.set_state` discipline.
4. **Privilege/activation surface:** no new activation path (switch machinery pre-existing; this task wires a fail-closed classifier into the existing seam); SHADOW-ONLY + R595 untouched; added-line scan for subprocess/socket/urllib/git/gh/shell=True → nothing; doctor disclosure interpolates static gauge-name lists only; resource-trip and outage resolve to fail-closed pause/stop, never a new dispatch.
5. **Supply chain:** zero new dependencies; stdlib-only import lists verified per file; no manifest/lockfile edit by the producer.
6. **Secrets/PII:** full-diff pattern scan → only the word "credential(s)" in explanatory comments; no keys, tokens, connection strings, or PII.

## Reproduced test evidence
24/24 new tests OK (fail-closed derivation, empty-shape guard, both resource-gate directions, structural-unknown non-pause, no-sampler compat, consumed-record-not-re-approvable).

## Findings
**INFO-1 (advisory for the future R595 activation gate; not a defect).** The seeded fixtures are DOCUMENTED-CANDIDATE shapes, source-controlled (flipping `verified_live=True` requires a reviewed code change — not runtime-configurable). The `rate_limit_429_prose` fixture matches transient rate-limit prose; the R595 activation review must confirm captured live bytes represent TRUE account-quota exhaustion (especially vs transient 429s) before flipping any fixture, to avoid a premature chain switch. Currently locked fail-closed by `test_documented_candidate_match_still_returns_unknown`; no action now.

**G5 SECURITY VERDICT: PASS.** Classifier and sampler wired but provably fail-closed; digest guard defeats replay/forgery; no new activation, external-effect, or supply-chain surface.
