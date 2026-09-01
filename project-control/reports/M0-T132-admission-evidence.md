# M0-T132 — admission preflight + live-drift findings + STOP assessment (D-024 Amendment 34, R437..R445)

Executed by the orchestrator in the primary control checkout `ctl24`, 2026-09-01. This report is the
ONE consolidated system-level assessment R394 requires: the fresh preflight PASSED, the three
owner-named fixtures were captured live and show only benign version-string drift, and then a live
blocking condition (the Fable 5 seven-day usage cap) made the owner's **one combined recert at one
final frozen identity** requirement (R441/R442) impossible to satisfy honestly right now. Nothing was
repinned, no recert ran, the supervisor journal is untouched, and the working tree is clean.

## 1. Fresh preflight — PASS (Bootstrap Gate 0 + R438)

| Check | Result |
|---|---|
| Root / branch / HEAD | `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, `control/D-024-fable-codex-loop`, HEAD `1d4a6212`, local == origin, tree clean |
| `/mcp` (`claude mcp list`) | no servers configured |
| `DISABLE_AUTOUPDATER` (this process) | `1` (inherited) |
| `DISABLE_UPDATES` | unset everywhere (R280 honored) |
| `claude --version` | `2.1.252 (Claude Code)` |
| On-disk `~/.local/bin/claude.exe` identity | `e713c5a6c8bc71af...` (sha256_head+size), 217,406,624 B — **byte-identical** to `versions/2.1.252` |
| Old renamed binary | `claude.exe.old.1788206208678` = `d6f6c29a...`, 217,360,032 B (the obsolete 2.1.251 pin) |
| Running orchestrator process (PID 13960) | on the 2.1.252 image (`~/.local/bin/claude.exe`, 217,406,624 B) — this fresh session did settle onto the new image |
| Newer version installed/staged? | none — versions dir = 2.1.248 / 2.1.251 / 2.1.252 only; downloads empty |

**R433 re-verification passes: 2.1.252 (`e713c5a6`) remains the settled admission target, unmoved.**

## 2. The three owner-named fixtures — captured live, benign version-only drift

All three surfaces are **byte-identical** between 2.1.251 and 2.1.252; only the version string changed.
Captured with bounded no-write probes (`--version` / `--help`) and the official hooks docs.

| Fixture | 2.1.251 → 2.1.252 finding | Instrument |
|---|---|---|
| **capability_probe** | `claude_version` first_line `2.1.251` → `2.1.252` (sha `1aaadbe0…` → `075f89d9…`); **`claude_help` sha UNCHANGED `83af8a9a7edc…`**; claude_flags / codex_flags unchanged; codex-cli 0.146.0 unchanged; **no FAILED probe rows** | `python -m tools.agent_supervisor.capability_probe` |
| **event_bus / hook_event_catalog** | official docs (`code.claude.com/docs/en/hooks`, re-fetched 2026-09-01) enumerate the **same 33 events** as the 2.1.251 catalog — **no hook-event drift**; only `claude_version` stamp would change | official docs (documentation-confidence, unchanged method) |
| **native_adapter / native_runtime_detection** | `detect_native_capabilities()` live: `claude_version` `2.1.251` → `2.1.252`; **flags, verbs, `background_host_ready=True`, `background_gaps=()` all identical** | `native_runtime.detect_native_capabilities()` (bounded --help) |

Conclusion on the drift itself: **2.1.252 is a benign patch bump** — identical CLI capability surface,
identical hook-event set, identical native background surface. The measured capture succeeded; the
generated fixture files were then removed from the tree because the admission is being held (see §3–§4)
and their content is trivially reproducible from the commands above.

## 3. LIVE BLOCKER — the Fable 5 seven-day usage cap is rejecting model calls

The fourth evidence piece, **shell-routing** (`shell_routing/v1`, R292/R295), is a *behavioral* probe:
it runs the installed `claude` under a bounded deny-everything harness and observes whether the worker
routes to native tools (`native_preferred`) vs shell. Two consecutive bounded runs at the 2.1.252
executable returned `verdict=no_tool_observed` (0 tool uses). Instrumenting one run showed the cause is
**not** routing drift and **not** the model declining tools — it is a hard usage cap:

```
rate_limit_event  { "status": "rejected", "rateLimitType": "seven_day_overage_included", ... }
assistant (text)  "You've reached your Fable 5 limit. Switch to another model, or manage usage
                   credits at claude.ai/settings/usage..."
result            stop_reason "stop_sequence"
```

(A preceding `rate_limit_event` showed `seven_day` utilization `0.78`, status `allowed_warning`.) The
bare `claude` invocation resolves to the default model (Fable 5, per `settings.json`), so the routing
probe is capped and **cannot produce a truthful `native_preferred` measurement** at the new digest
right now. The `no_tool_observed` fixture it did emit is a capped-model artifact, not routing evidence;
it was deleted (it carried `measured:true` + `cli_identity:e713c5a6`, and the start-gate probe accepts
any *measured* fixture for the identity regardless of verdict — committing it would have **false-greened**
the shell-routing gate, which is worse than the honest fail-closed state).

## 4. Why this blocks the owner's *one combined recert at one final frozen identity*

- **shell-routing is digest-keyed and folded into `cli_capability_manifest`** (R295; `FOLDED_PROBES`).
  `probe_shell_routing_evidence` matches on the executable **digest** when the start gate supplies one.
  After a repin to `e713c5a6`, a real commissioning start needs fresh `e713c5a6` routing evidence; the
  existing evidence is `d6f6c29a` (2.1.251) and would return `routing_evidence_stale` → the folded
  `cli_capability_manifest` step fails closed → **the start still refuses**. So a repin now would trade
  today's fail-closed refusal (unpinned/mismatched identity) for a *different* fail-closed refusal
  (stale routing), not clear it.
- **R247 + R441/R442 interaction (decisive):** the owner authorized **ONE** combined recert at **ONE**
  final frozen identity. R247 says any later supervisor-evidence change invalidates that certification
  and forces a re-run. A shell-routing recapture at `e713c5a6` is exactly such a change (it edits
  committed `tools/agent_supervisor/**` fixture evidence, moving the tree hash). So doing the recert
  now — before routing can be captured — **guarantees a second recert later**, structurally violating
  "one combined recert at one final frozen identity."
- **R220/R221:** the missing piece needs a working model, which the seven-day cap is rejecting. R221
  forbids consuming owner allowance to work around / provoke a quota event; R220 forbids blocking
  otherwise-provable work on it. The doc/help-based work *did* proceed (that is §2); it is only the
  model-dependent routing capture that is blocked.
- **Genuine scope ambiguity (directive-compliance §3.9):** the owner authorized "the **three** affected
  live capability fixtures." shell-routing is a **fourth**, digest-entangled one. Its *behavior* is
  unchanged (identical --help bytes), but its *evidence* is invalidated by the digest change, so a real
  start fails closed on it. Whether it is "affected" (must be recaptured before the single recert) or
  out of scope (routing behavior demonstrably unchanged → proceed with three) is an owner call I must
  not resolve silently — either silent path is wrong: excluding it presents "certified start commands"
  that would fail closed; including it forces capped-model spend (R221) or a blocking wait (R220).

## 5. What was and was NOT done (preservation)

- **Done (read-only / bounded):** identity re-verification (§1); three-fixture live capture (§2);
  routing-cause diagnosis (§3). Provider calls consumed: the two routing runs + one 1-call diagnostic
  (most turns were *rejected* by the cap). No further probe runs will be made (R221).
- **NOT done:** no manifest repin, no `--repin-cli-identity`, no recertification, no re-pointing of any
  fixture pointer or test, no supervisor start, no journal read-beyond/write, no reset, no PR #241
  action. Generated fixtures removed → **tree clean**.
- **Preserved unchanged:** journal HALTED (transitions 35, audit 85); `wt-m0t107` `c5c6ff7` + its two
  untracked journey-4 drafts; `wt-m0t109` `1c06957`; queue digest `11eaa5a7`; owner-touch 3-of-2;
  budgets; every owner gate; PR #241 OPEN.

## 6. Recommendation (for the owner)

Hold the repin + combined recert until the shell-routing evidence at `e713c5a6` can be captured, so a
single recert lands at one truly commissioning-ready identity — consistent with R441/R442. Concretely,
choose one (details + exact lines in the blocker `B-020` and the seam presentation):

- **OPTION A (recommended):** wait for the Fable 5 seven-day cap to reset (its `resetsAt` is recorded),
  then run the full M0-T132 lane in one pass: three fixtures + shell-routing recapture at `e713c5a6` +
  repin + **one** combined R247 recert at the one final identity. No allowance is spent provoking
  anything; nothing is certified twice.
- **OPTION B:** authorize a bounded routing recapture on a non-capped worker model (e.g. `--model
  claude-opus-4-8`) — this is a deviation from the M0-T120 default-model capture methodology and needs
  an explicit owner decision (it is arguably an R221-adjacent workaround), so it is presented, not taken.
- **OPTION C:** rule that shell-routing is out of the "three affected fixtures" scope (routing behavior
  is demonstrably unchanged); then M0-T132 proceeds with the three fixtures + repin + one recert now,
  and the certified-start commands are presented **with the standing shell-routing fail-closed caveat**
  (the next start refuses at the shell-routing fold until routing is recaptured). This resolves the
  ambiguity by owner ruling rather than silent interpretation.

Until the owner rules, M0-T132 is **blocked** (`B-020`); the settled admission target and all three
benign-drift findings above stand and are reusable the moment the lane resumes.
