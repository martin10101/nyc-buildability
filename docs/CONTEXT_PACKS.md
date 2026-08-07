# Bounded context packs (`tools/context_pack.py`)

`tools/context_pack.py` builds the **smallest complete packet** an agent needs to
work on, review, or control one task — under explicit byte and estimated-token
bounds, with full provenance and no silent truncation. It implements D-010
source-001 **Section 12** (bounded context-pack builder) and the **0A.4** budget
ceilings. It is stdlib-only and path-safe on Windows and Linux.

> Trust model for graph hints: the code-navigation graph is **advisory**. A query
> result points at likely locations; the packet records the exact bounded queries
> used but never embeds the whole graph, and the copied **source excerpts** — not
> the graph — are the authority a reviewer verifies against. *Graph points; source
> decides.*

## CLI

```bash
python tools/context_pack.py \
  --task <TASK_ID> \
  --role worker|reviewer|controller \
  --provider claude|codex \
  --max-bytes <BOUND> \
  --out <DIR>
```

Optional knobs (all recorded in `context.meta.json`):

| Flag | Default | Purpose |
|---|---|---|
| `--repo` | `.` | repository root |
| `--context-window <tokens>` | none | reported model context window, for the 20% relative ceiling (§0A.4) |
| `--include <path>` (repeatable) | — | explicit source file(s) — the "explicit source files" input (§12.1) |
| `--ci-summary <file>` | none | inject a CI summary; **never** fetched from the network |
| `--diff-base <ref>` | `HEAD` | git ref to diff against for changed hunks |
| `--graph-limit <n>` | `20` | per-query line cap for bounded code-graph queries |
| `--target-tokens` / `--ordinary-ceiling-tokens` / `--relative-ratio` / `--bytes-per-token` | 32000 / 64000 / 0.20 / 4.0 | budget overrides (§0A.4) |

### Examples

Worker packet for a task, honoring a 200k model window:

```bash
python tools/context_pack.py --task M0-T043 --role worker --provider claude \
  --max-bytes 200000 --out /tmp/pack --context-window 200000
```

Reviewer packet (needs primary-source changed hunks) with injected CI:

```bash
python tools/context_pack.py --task M0-T043 --role reviewer --provider codex \
  --max-bytes 200000 --out /tmp/pack --ci-summary ci.txt --context-window 200000
```

Exit codes: `0` success (within bound, possibly after summarizing non-material
logs); `2` **fail-closed** — a material source does not fit even after
summarization, so a split proposal is emitted instead of a quietly smaller packet.

**Exit-0 byte-bound guarantee.** Whenever the process exits `0`
(`overflow.resolved` is `within_bound` or `summarized`), the **real emitted
`context.md` — footer included — is `≤` the effective byte bound.** The bound
decision is *footer-aware*: the builder renders the actual footer (omitted
categories, role sufficiency, overflow block) and iterates its self-referential
size to a fixpoint before deciding, so what is measured against the bound is
exactly what is written. When that cannot be achieved without reducing *material*
content, the builder takes the fail-closed exit-`2` split path instead — it never
emits an over-bound packet at exit `0`. (The exit-`2` split *report* is a bounded
diagnostic and is exempt from this guarantee.)

## Output (§12.3)

```
<out>/context.md         the packet, human-readable, deterministic section order
<out>/context.meta.json  the machine record (all §12.3 fields)
<out>/evidence/          copied source excerpts / changed hunks / preserved originals
```

## Inputs gathered (§12.1)

In deterministic section order: task packet (`project-control/tasks/<TASK>.json`);
current ledger state (`state.json`); git diff (changed **hunks**) and changed
paths; bounded **advisory** code-graph queries; the authoritative routing table
(the `CLAUDE.md` on-demand-routing section); relevant contracts (only when the
task's paths touch `packages/contracts/**`); the latest checkpoint (highest
`checkpoints/CP-*.json`); relevant blockers (any blocker whose record references
the task id); latest CI (injected via `--ci-summary`; if absent, recorded as an
explicit omission — the builder never calls the network); explicit source files
(`--include`); and the previous handoff (newest `reports/session-handoff-*.json`,
else the current block of `docs/SESSION_HANDOFF.md`).

## Default exclusions (§12.2)

Never embedded by default; each is recorded as an omitted **category** in the meta
(`default_exclusion: true`):

- `entire_prd`
- `entire_directive_registry`
- `all_historical_reports`
- `old_session_transcripts`
- `unrelated_task_packets`
- `full_generated_artifacts`
- `full_city_datasets`
- `whole_code_graph`

Conditional omissions (e.g. `git_diff` on a clean tree, `latest_ci` when not
injected, `contracts` when the task doesn't touch them) are recorded alongside
these with `default_exclusion: false` and a reason — so **every** omission is
visible, never a silent gap.

## 0A.4 budget table

The byte size of `context.md` is converted to an estimated token count and checked
against a three-tier ceiling. Numbers are **engineering policy, not billing
claims**.

| Tier | Default | Meaning |
|---|---|---|
| target | ≤ 32,000 est. tokens | the size a packet should aim for |
| ordinary hard ceiling | ≤ 64,000 est. tokens | the absolute per-packet cap |
| relative hard ceiling | ≤ 20% of the reported model context window | scales with the provider window (only applied when `--context-window` is given) |
| **effective** hard ceiling | **the lower** of ordinary and relative | the one enforced |

The token estimate is deterministic: `ceil(bytes / bytes_per_token)` with
`bytes_per_token = 4.0`. When no context window is reported, the relative ceiling
cannot be computed and is **not** applied — the ordinary ceiling stands, recorded
honestly (`relative_applied: false`; a window is never fabricated).

The **effective byte bound** actually enforced is
`min(--max-bytes, effective_ceiling_tokens × bytes_per_token)`. Enforcement is
**footer-inclusive**: the size compared against this bound is the full emitted
`context.md` (header + source blocks + the real footer), resolved to a fixpoint —
not a footer-less estimate. So an exit-`0` packet is guaranteed to sit at or under
the effective byte bound.

These constants and the estimate are a **local mirror** of
`tools/agent_supervisor/review_packet.py` (the shadow-only supervisor's review
budget). A drift-lock test (`test_drift_*`) imports that module and asserts the
constants, the byte→token estimate, and the effective-ceiling logic are identical,
so the two can never diverge silently. The runtime keeps its own copy so it does
not depend on the frozen shadow-only tree.

## `context.meta.json` field reference

| Field | Meaning |
|---|---|
| `schema_version` | meta schema version |
| `task_id`, `repo_sha` | the task and the repository SHA (the time anchor) |
| `role`, `provider` | requested role and provider |
| `generated_from` | every input knob (repo, diff base, includes, ci summary, graph limit) |
| `budget` | target/ordinary/relative/bytes-per-token + model context window used |
| `bounds` | `max_bytes`, the four token bounds, `effective_ceiling_tokens` + basis, `effective_bound_bytes` |
| `actuals` | `context_md_bytes`, `estimated_tokens`, and `within_*` booleans (max bytes / effective bound / target / effective ceiling) |
| `included_files[]` | per source: `source_id`, `group`, `category`, `origin`, **`sha256`**, `bytes`, `estimated_tokens`, `material`, `truncated`, `truncation`, `evidence_path` |
| `omitted_categories[]` | the 8 default exclusions plus every conditional omission, each with a reason |
| `graph_queries[]` | each bounded advisory query run (`subcommand`, `arg`, `limit`, `ok`, `lines_returned`) |
| `truncated_any`, `truncations[]` | whether any source was summarized, and for each: original digest + bytes, summarized bytes, method, preserved artifact |
| `sufficiency` | role-sufficiency flag: `sufficient`, `reason`, required/present/missing source groups |
| `overflow` | `triggered`, `resolved` (`within_bound` \| `summarized` \| `split_required`), guidance, and the split proposal when fail-closed |

Every included source is digested with SHA-256 over the exact bytes placed in the
packet; when a source is summarized, the meta additionally records the **original**
digest and byte count and the path to the preserved full artifact.

## Overflow, summarize, and split behavior (§12.4 / AD-046)

When the assembled `context.md` exceeds the effective byte bound:

1. **Summarize non-material logs.** Reducible sources (advisory code-graph output,
   injected CI summary, previous handoff) are replaced in the packet by a
   deterministic head-of-file summary plus an **exact artifact reference**; the
   full original is written to `evidence/<id>.orig.<ext>` and its digest recorded.
   Nothing is dropped — the summary points at the preserved original.
2. If the packet now fits → `resolved: summarized`, exit `0`, with every
   summarization recorded in `truncations[]`.
3. **A material source is never silently truncated.** If material still does not
   fit, the builder **fails closed**: it emits a deterministic **split proposal**
   (exact source lists per sub-packet, each within the bound; any single
   oversize material source is flagged with advice to split the *task* so it
   shrinks), writes a bounded overflow *report* as `context.md` (digests + split
   plan, **not** the giant material body), preserves the full material under
   `evidence/`, and exits `2`. It never emits a quietly smaller packet.

### Reviewer packets carry primary source

A `reviewer` packet must include enough **primary source** (changed hunks,
authoritative excerpts) to verify a worker's claim — never merely the worker's
summary (§12.3). The role-sufficiency flag is `false` (with a reason) when a
reviewer packet lacks changed hunks, so an under-provisioned review is visible
rather than silently accepted.

## Determinism guarantee

Given the **same repository state and the same arguments**, `context.md` and
`context.meta.json` are **byte-identical** across runs. There are no wall-clock
timestamps (the repository SHA is the only time anchor), every path list and JSON
object is sorted, and recorded paths use POSIX separators on every platform. A
build-twice byte-equality test (`test_determinism_byte_identical`) proves it.
