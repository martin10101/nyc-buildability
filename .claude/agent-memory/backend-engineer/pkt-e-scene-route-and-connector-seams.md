---
name: pkt-e-scene-route-and-connector-seams
description: D-087 PKT-E scene assembler/route build - reusable seams for threading a deadline into the shared transport without editing it, the substring claim-word matcher, the missing route rate-limit primitive, and unmounted-route test mechanics
metadata:
  type: project
---

Built M5-T107 (D-087 PKT-E): `services/api/app/scenario/scene_assembler.py` (pure section-2.1
scene payload) + `services/api/app/api/v1/scene_api.py` (UNMOUNTED flag-gated route) + the
building-footprint connector's DB-073 (a)-(g) pre-consumption riders.

**Why:** these are non-obvious seams and gotchas that recur across the D-087 wiring packets
(PKT-D/PKT-F/PKT-H all need the same job/deadline/rate-limit safety, DB-061 (i)).

**How to apply:**

- Thread a caller deadline into the SHARED transport WITHOUT editing `app/resilience/transport.py`
  (a forbidden path in most packets): `request_with_retry` calls the INJECTED `sleep(delay)`
  OUTSIDE its try (only `transport()` is wrapped), so a deadline-aware sleep wrapper that raises a
  typed connector error propagates cleanly into the connector's fail-closed refusal path. In
  building_footprints_arcgis I pass `sleep=self._sleep_within_deadline` (checks `_check_deadline`
  then `self.sleep`). Deadline comparisons need a tz-AWARE datetime; validate up front
  (tz-naive -> typed disallowed_request) or `_check_deadline` raises TypeError -> internal_error.

- `app/cad/claim_words.contains_claim_word` (the shared D-083 screen) is a blunt SUBSTRING test
  (`claim_key(word) in claim_key(text)`), so honest negations trip it: "not a **legal**
  determination" matches "LEGAL"; "permitting" is safe (not a superstring of "PERMITTED"), but
  "MAXIMUM ALLOWED" only matches when both words are adjacent ("cantilevers are allowed" is fine).
  Keep the barred words (PERMITTED/APPROVED/CERTIFIED/COMPLIANT/LAWFUL/LEGAL/ENTITLEMENT/
  GUARANTEED/MAXIMUM ALLOWED/AS OF RIGHT) out of OUR OWN disclosure prose, even negated.

- There is NO route-level per-caller rate-limit primitive in the repo - the routes' `rate_limited`
  states are UPSTREAM connector-throttle states only. DB-061 (i) requires a per-caller route limit;
  I implemented a minimal stdlib sliding-window in scene_api (keyed by `request.client.host`; no
  auth yet). Consider extracting a shared route rate-limit helper (and bounding the number of
  tracked keys) before PKT-H mounts anything. See [[env-producer-sandbox-no-exec]].

- Unmounted-route pattern (mirror `max_envelope_api` / M5-T059): route module ships with
  `include_in_schema=False`, flag-gated on `INTERNAL_RULE_EVAL_ENABLED`, absent/unknown flag ->
  generic 404 `{"detail":"Not Found"}` (no correlation header). Reuse the accepted bounded-stream
  body primitives from `proposal_validation` (`MAX_BODY_BYTES`, `_declared_content_length`,
  `_read_body_within_ceiling`, `_bounded_message`). Off-loop cancellable job =
  `asyncio.wait_for(run_in_threadpool(work), timeout=...)` -> typed 504 on `TimeoutError` (the
  OS thread cannot be force-killed; the connector's own deadline + internal bounds stop it).
  Tests mount `router` on a fresh `FastAPI()` and assert the path is absent from `app.main`'s
  routes AND OpenAPI. `catch TimeoutError` (ruff UP041 bars `asyncio.TimeoutError`).

- Replacing a grep-for-the-literal "not wired" test on WIRING (DB-073 e): use an import-graph/AST
  walk from `app.main` (follow `app.*` ImportFrom/Import edges, resolve `module.py` or
  `pkg/__init__.py`) and assert the connector + the unmounted route are unreachable, and that the
  one intended consumer (the assembler) imports it. Survives wiring by design.

- Committing to a PEER worktree (wt-m5t107) from this isolated session: `cd <wt> && git add <files>`
  and `git commit -F <msgfile>` WORK, but a complex Bash heredoc append was REFUSED ("too complex
  to verify it stays inside the worktree") - use the Edit tool to append to files and keep git
  commands simple/separate. Reinforces [[env-producer-sandbox-no-exec]].
