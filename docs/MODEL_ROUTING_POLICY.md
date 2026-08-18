# Model Routing Policy (M0-T074, D-017-R114..R123)

Deterministic complexity-based model routing: the model executing or reviewing a
piece of work is chosen by **measured task complexity, risk, and required
capability** — never by a model choosing itself. Implementation:
`tools/model_routing.py`; frozen proof corpus: `tools/model_routing_corpus.json`;
CI: `model-routing` job.

## Who consumes it

The **orchestrator**, when dispatching workers and reviewers. The supervisor
stays frozen (defect-only lane); any supervisor-side integration is its own
qualifying-evidence task. The router only ever READS the protected controller
configuration (through the frozen supervisor's own loader, recording the config
bytes' SHA-256 as evidence); it never writes `config.toml` or
`model_selection.toml`, and no worker can add or authorize a model.

## Complexity bands

| Band | Work shapes |
|---|---|
| LOW | repository census, formatting, mechanical documentation, deterministic lookups, simple isolated tests |
| MEDIUM | bounded single-subsystem implementation, ordinary debugging, focused refactoring, test creation |
| HIGH | cross-subsystem architecture, difficult debugging (≥2 failed attempts), migrations, concurrency, performance, graph/schema changes |
| CRITICAL | security, authorization, protected configuration, legal/numeric correctness, destructive operations, control-plane changes, final independent acceptance |

## Deterministic signals (`Signals`, typed and closed)

files affected; subsystems affected; dependency-graph spread; security and
authorization impact; protected-configuration impact; destructive operations;
control-plane change; legal/numeric correctness; external side effects;
schema/migration impact; concurrency/performance; ambiguity or missing
evidence; prior failed attempts; required reviewer roles; estimated context
size; task-packet risk classification. Unknown signal names are a `TypeError`
— an ungrounded classification cannot be constructed. Every verdict carries
`determining_signals`. **Ambiguity raises the band by one (fail-up), never
lowers it.**

## Routing rules

1. Route only within the protected allowlist; empty allowlist or a model with
   no entry in the deterministic tier table → `RoutingError` (never guess
   strength or cost).
2. LOW/MEDIUM → the lower-cost permitted model. HIGH/CRITICAL → the stronger
   permitted model. `security-reviewer`, `directive-compliance-verifier`, and
   `final-acceptance` roles → the strongest permitted independent reviewer.
3. **Single-model honesty (R118):** when a provider permits exactly one model
   (today: `claude: ["claude-opus-4-8"]`), `adaptive_available` is False and
   the record says routing is UNAVAILABLE — selection is never simulated.
4. Failed LOW/MEDIUM work may escalate **one** level with the reason recorded;
   HIGH/CRITICAL work is never re-routed, downgraded, or shuffled to save
   tokens (no API exists to choose below the deterministic pick).
5. Quota fallback (`record_quota_fallback`) is a SEPARATE decision class,
   recorded separately, restricted to permitted models, and refused without a
   reason. It never merges into a routing decision.

## Decision records (R121)

Every decision is appended (JSONL, append-only) to the accepted per-checkout
runtime directory (`durable_state.runtime_dir_for(checkout)/model_routing.jsonl`
— outside the repository), carrying: task ID, complexity band, determining
signals, chosen model, permitted-model evidence (allowlist + config SHA-256),
fallback status, estimated context size, result, and telemetry where available.
Telemetry fields are **nullable — a missing value is never fabricated as zero.**

## Current honest state

The protected allowlist permits `gpt-5.6-sol` / `gpt-5.6-terra` (Codex; sol
stronger, terra lower-cost) and exactly one Claude model. Adaptive Codex
routing is ACTIVE; adaptive Claude routing is **unavailable and reported so**.
Enabling meaningful Claude routing requires an owner change to the protected
allowlist via the established protected-config update procedure — the router
never requests or performs it, and repository implementation completes first
(D-017-R123).

## Proof (R122)

`tools/model_routing_corpus.json` freezes 15 cases (LOW stays on the lower-cost
model; HIGH/CRITICAL always take the stronger; ambiguity promotes).
`tools/test_model_routing.py` (CI `model-routing` job) additionally proves: an
unauthorized model cannot be chosen; no self-selection parameter exists; an
unrecorded fallback is refused; an ungrounded classification is unconstructible;
single-Claude honesty; HIGH/CRITICAL no-downgrade; append-only records with
null-not-zero telemetry.
