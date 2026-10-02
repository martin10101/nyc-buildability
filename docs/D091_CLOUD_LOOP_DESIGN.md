<!-- Committed by the orchestrator from the D-091 design robot's output (cloud-architect, 2026-10-02). Orchestrator change: the recertification (T3) runs after ALL D-091 code tasks (T1, T2, T5, T6, T7), not before T5, because every tools/agent_supervisor/** edit invalidates it. The ledger, not this file, holds task state. -->
# D-091 design — move the Codex/Claude loop to this Linux cloud server + three-model review

Scope: owner directive D-091 (`/root/project/w-directive-091/project-control/directives/D-091-cloud-loop-dual-review/`, R001–R008).
Read against primary checkout `/root/project/nyc-buildability` at head `c81ba14d`.
Plain words. Every claim carries file:line evidence. Design only — no ledger writes here.

Server: Ubuntu, 4 CPU / 8 GB, Python 3.12, test venv `/root/project/lanes-runtime/venv`.

---

## 0. One-paragraph recommendation

Port the existing controller; do not rebuild a smaller loop. Almost all of the ~59k lines
of `tools/agent_supervisor/` are plain cross-platform Python; the Windows coupling is a thin,
well-isolated seam (OS-ACL hardening, a few config paths, PowerShell launch/test scripts) plus a
fixture recapture that any platform or CLI change forces anyway. Rebuilding would throw away the
accepted fail-closed safety machinery this legally-sensitive project depends on. Add the dual
review (a fresh Claude reviewer beside the existing Codex reviewer) and a combiner stage that can
only *add or keep* findings, never weaken them. Admit Codex through the normal dependency gate at a
pinned ≥7-day version (today `0.156.1`), owner signs in last. The combiner default is Claude
Opus 5.5 (available, high-end, already allowlisted); avoid Fable (exhaustion history, B-024).
Moving here does NOT close B-026 — that blocker is about the owner's PC controller.

---

## 1. Inventory — Windows-only parts and what Linux needs

The loop was built for the owner's Windows PC. The genuinely Windows-bound pieces are few and
isolated; the state machine, tier policy, Codex reviewer, durable state, recovery, broker, and
gate wave are platform-neutral Python.

| # | Windows-only part | Evidence | Linux needs | Effort |
|---|---|---|---|---|
| 1 | OS-ACL hardening of the immutable config via `icacls` + `harden_controller_config.ps1` (owner UAC) | `tools/agent_supervisor/os_acl.py:2` ("Windows OS-ACL boundary inspection"), `:20` (icacls), `:30-34` (ps1 via UAC); it already fails closed to `UNKNOWN` off-Windows (`os_acl.py:33-34`) | A POSIX verifier: config root-owned `0444`, protected parent dir, same fail-closed verdict shape | M |
| 2 | Hardcoded Windows config paths: `C:\Program Files\SupervisorConfig\config.toml`, `%LOCALAPPDATA%\NYCBuildabilitySupervisor\…\controller_manifest.json` | `B-026…json` detail; `config.example.toml` header ("Copy it to the controller checkout as `config.toml`") | A Linux path resolver (e.g. `/etc/nyc-supervisor/config.toml` root-owned, `/var/lib/nyc-supervisor/` runtime, `~/.config` activation) | S–M |
| 3 | PowerShell test + launch scripts: `ps_tests/harness.ps1`, `run_ps_tests.ps1`, mutants; `.ps1` autostart; `Start-Process` | `tools/agent_supervisor/ps_tests/*.ps1`; CODING_RULES/B-024 launcher history | A bash shell-routing test harness + a bash/systemd launcher (shell-routing logic in `routing_probe.py` is already platform-neutral: `routing_probe.py:80-83`) | M |
| 4 | Certified against ONE exact `claude.exe` CLI identity; fixture packs captured on Windows CLI 2.1.247→2.1.281 | `claude_runner.py:1049` (`executable_identity(...,name="claude")`); `fixtures/capability_probe_live_*`, `shell_routing_*`, `native_runtime_detection_*` | Recapture the whole fixture pack at the Linux `claude` CLI identity; same recert flow as M0-T159 | M–L |
| 5 | `DISABLE_AUTOUPDATER` machine-scope env belt for the two bare version/help probes | runbook §13 `:349-352`, `:366-373`, `:390-394`; `native_runtime.py:101` (`env=None`), `capability_probe.py` (~`:99`) | Set it in the Linux service unit / probe env; per-child injection already in `process.py::claude_child_env` is platform-neutral | S |
| 6 | Single-instance lock | `locking.py:75` (`_probe_windows`), `:144` (`os.name=="nt"`) | None — already has a POSIX branch; cross-platform by design (`locking.py:2`) | none |

Everything else in `tools/agent_supervisor/` (policy engine `policy.py`, `state_machine.py`,
`codex_reviewer.py`, `durable_state.py`, `recovery.py`, `broker.py`, `gate_wave.py`, argv built
`shell=False` `claude_runner.py:1213`) is stdlib Python and runs on Linux unchanged.

Recommendation: **port**. The Windows coupling is 5–6 modules/scripts behind a small platform
seam; the safety guarantees are already built, reviewed and accepted. A rebuild re-opens risk the
project cannot take. Rough size: one platform-seam task set + one recertification ≈ the existing
M0-T159 recert plus a handful of bounded Linux tasks (see §7).

---

## 2. The three-model review flow

Today the loop has ONE independent reviewer (Codex) and Claude is the worker; there is no
Claude-reviewer path (grep of `tools/agent_supervisor/*.py` finds none). D-091 adds a second
independent reviewer and a combiner.

**Flow (per finished piece of work, at one frozen head):**

```
producer (Claude worker, writes the work)
        │  freeze head  H
        ├────────────► Codex review      (fresh read-only process, sees H + packet, NOT the Claude review)
        └────────────► Claude review      (fresh instance ≠ producer, sees H + packet, NOT the Codex review)
                               │
                               ▼
                    combiner (higher-end model, §4)
                    reads BOTH reviews + the diff at H
                               │
                               ▼
                    one combined review  ──► orchestrator records the gate (ADR-005)
```

- **Independence.** Both reviews run on the same frozen SHA and neither sees the other
  (`ORCHESTRATION_POLICY.md:85` frozen-SHA rule; `:165`/`GATES_AND_CHECKPOINTS.md:165`
  producer ≠ reviewer). Codex is read-only by construction — `--sandbox read-only`,
  `codex_reviewer.py:15`, `:58`. The Claude reviewer is a fresh instance under the read-only
  reviewer discipline (`project-control.md`; `ORCHESTRATION_POLICY.md:45`).

- **Combining rules (never weaken a review).** The combined review is a **union, not an
  intersection**:
  1. Every finding either reviewer raises **stays** unless the combiner cites concrete evidence
     that refutes it.
  2. Conflicts between the two reviews are resolved only with evidence (file/line, command output,
     SHA), never by preference.
  3. Every surviving point keeps its **source tag** (`codex` / `claude`) and its evidence.
  4. The combined **verdict is the worst unrefuted verdict**: if either reviewer has an unrefuted
     blocking defect, the combined verdict cannot be PASS. The combiner can never upgrade a FAIL to
     PASS — it can only assemble and adjudicate with evidence.
  5. The combiner is **never the producer** (R003) and is a fresh instance that authored neither
     review.
  These rules make the combiner monotone: it can add detail or drop only evidence-refuted noise.

- **How it feeds the gates / authority.** The combined review is *advisory input* to G3
  (human-style walkthrough, `GATES_AND_CHECKPOINTS.md:59`) and G4 (integration/regression, `:74`),
  exactly as a single reviewer's report is today. The **orchestrator alone records the gate and
  merges** (`ORCHESTRATION_POLICY.md:73`; ADR-005). An existing owner-gated verdict→gate recorder
  already exists as DEFAULT-OFF scaffold (`gate_wave.py:1-33`, R595 activation pending); the
  combined verdict would feed that same recorder when the owner activates it — until then the
  orchestrator records gates manually from the combined review. This keeps **D-024-R003**
  intact: Codex (and the combiner) only review; neither produces, merges, or records a gate
  (`D-024 requirements.json:103` "never a second producer"; `codex_reviewer.py:7-17` read-only argv).

---

## 3. Codex admission

- **Package.** `@openai/codex` on npm (official GitHub README: `npm install -g @openai/codex`;
  Linux x86_64 binary also `codex-x86_64-unknown-linux-musl.tar.gz`). Admit the npm package so the
  dependency gate can exact-pin + integrity-match it (`DEPENDENCY_SECURITY_POLICY.md:27-31`).

- **Version + age (verified from `registry.npmjs.org/@openai/codex`, fetched 2026-10-02):**
  `latest = 0.160.0` published 2026-10-01 (**age 0.15 d → FAILS** the 604800 s / 7-day rule,
  `DEPENDENCY_SECURITY_POLICY.md:24`). Recent stable X.Y.Z ages today:
  `0.156.0` 9.17 d PASS, `0.156.1` 8.89 d PASS, **`0.157.0` 6.89 d FAILS**, `0.157.1` 5.95 d FAIL,
  `0.158.0`–`0.160.0` all <4 d FAIL. The package also publishes hourly alpha builds — ignore them.
  **Candidate: `0.156.1`** (newest stable that currently clears ≥7 days); `0.157.1` clears on
  2026-10-03 and would be the better pick if admission runs then. Pin whatever is newest-and-≥7-days
  at admission time.

- **Advisories.** Must be advisory-free at every severity, audited fail-closed
  (`DEPENDENCY_SECURITY_POLICY.md:20-22, 40-42`). I could NOT run `npm audit`/OSV here (read-only,
  no npm) — the admission task runs it; a single finding fails closed.

- **G5 provenance (new package → G5 review required, CLAUDE.md §15):** record registry origin,
  exact `dist.integrity` match, publish timestamp ≥7 d, and re-verify the reviewer flags on the
  *installed* binary (`codex exec --help`) rather than trusting this doc — the repo already learned
  flags differ by version (D-007 `source-001.md:115`, flags adopted at codex-cli ≥0.146.0; the loop
  last probed 0.153.4, `fixtures/capability_probe_live_2026-09-06_d032_codex_0_153_4.json`).

- **Where the owner token lives (never in the repo).** Owner signs in with
  `codex` → "Sign in with ChatGPT" (or an API key), per the official README. The credential lives
  in the owner's home config (`~/.codex/`), **outside the repo and outside git**; the supervisor
  invocation already passes `--ignore-user-config` so the owner's personal config never leaks into
  a review (`codex_reviewer.py:8,17`). The exact auth-file path must be confirmed from
  `developers.openai.com/codex/auth` during admission — not guessed.

- **The one owner action:** run the Codex sign-in on the server, once, when everything else is
  ready (R006). The orchestrator never handles the credential.

---

## 4. Combiner model options

The combiner reads both reviews and the diff and emits one combined review. It must be a fresh
high-end instance that authored neither review.

| Option | Independence | Quality | Cost | Availability | Verdict |
|---|---|---|---|---|---|
| **Claude Opus 5.5** (D-085, allowlisted) | Same provider as the Claude reviewer, but a distinct fresh instance/model | High reasoning | Opus-tier | Good — already the worker/subagent pin | **Recommended default** |
| Codex on a higher-end OpenAI model | Cross-provider vs the Claude reviewer; same provider as the Codex reviewer | High | Codex/ChatGPT plan | Needs the §3 admission + sign-in first | Good alternative; pick if the owner wants cross-provider adjudication |
| Fable 5 | Same provider as Claude reviewer; fast not deep | Lower for deep adjudication | Cheapest | **Poor — exhausted account-wide**, `B-024` (resolved by moving off Fable), `D-060`; `D-064-R004` made Opus the standing pin | Not recommended |

Recommendation: **Opus 5.5**, because it is available now, high-end, already owner-approved, and
needs no extra admission. Trade-off: it shares the Anthropic provider with the Claude reviewer, so
full cross-provider independence is not achieved — mitigate by (a) running the combiner as a fresh
instance that saw neither review's process, (b) making the Claude *reviewer* a different Claude
model than the combiner, and (c) the source-tagging + evidence-to-drop rules in §2, which make the
combiner auditable regardless of provider. If the owner prizes cross-provider adjudication over
simplicity, choose "Codex higher-end" after §3. **R008 is an open owner choice; this is the
recommended default.**

---

## 5. Resource fit — 5 lanes on 4 CPU / 8 GB, memory under 70%

- 70% of 8 GB ≈ **5.6 GiB** working ceiling; ~1.1 GiB per lane if all five run flat out.
- Each lane = one Claude worker (node CLI, ~0.3–0.7 GiB) plus bursty Codex-review / Claude-review /
  combiner processes. Five workers steady-state fit; the risk is **simultaneous review+combine
  spikes** across lanes and OOM.
- The config limits are whole-box and were sized for one PC: `max_memory_bytes = 8589934592` (8 GiB),
  `max_cpu_percent = 90`, `max_processes = 24` (`config.example.toml` `[limits]`). They need
  re-tuning for a shared 4-CPU/8-GB box.
- Mitigations (a tuning task, §7 T7): set the global pause ceiling to ~5.6 GiB; add a **global
  review/combine semaphore** (≤2 concurrent review-or-combine processes across all lanes) so the
  five workers never all spike at once; cap per-lane turn concurrency; keep the existing fail-closed
  CPU/memory/process gauges but at the re-tuned numbers.
- Concurrency note: 5 writers exceeds the policy's "normal max 3 writers" (`ORCHESTRATION_POLICY.md:77`).
  It is allowed only because lanes are genuinely independent, non-overlapping worktrees (`:17`, `:81`),
  which is the lane model's whole point.

---

## 6. B-026 on Linux — what honestly closes, what stays open

B-026 is a **PC-controller** blocker: CLI 2.1.281 was never admitted to the certified *Windows*
controller and the controller manifest still binds the pre-B-025 `C:\Program Files\…\config.toml`
(`B-026…json` title + detail). Its closing condition is owner-typed **Windows** commissioning
(runbook §12; `B-026 scope_corrections[0]`).

- Moving the loop here does **not** close B-026. A Linux loop is a *new, separately certified*
  runtime; its certification evidence is about the Linux controller, not the PC one. Closing B-026
  with Linux evidence would be dishonest, and the rules forbid closing a blocker to get past it
  (source reply, `source-001.md:21`).
- What the Linux loop *does* achieve for R004: it removes the **dependency** of cloud loop
  operation on B-026. After the Linux loop is certified and running, cloud work no longer waits on
  the PC. Record that as a scope note on B-026 (not a closure).
- B-026 closes only when either (a) the owner does the Windows recommission (recert + `--repin-cli-identity`
  + lane-1 canary, runbook §13 `:381-388`), or (b) the owner decides to **retire** the PC loop in
  favour of the cloud loop. That disposition is an owner decision (§8 OD-D).

---

## 7. Task breakdown (orchestrator-designed `M<x>-T<n>`, cite D-091)

All are M0-class controller work. `tools/agent_supervisor/**` changes invalidate the frozen-identity
certification, so T1–T3 are batched under **one** recertification window (runbook note `:441-445`).
Producers in isolated worktrees; orchestrator records gates/merges (ADR-005).

| T | Scope (allowed paths) | Gates | Reviewers | Order | Owner touchpoint |
|---|---|---|---|---|---|
| T1 Platform seam | `tools/agent_supervisor/{os_acl.py,config.py,process.py,+posix_acl.py}` + tests | G0,G2,G3,G4,G5 | code-reviewer, security-reviewer, control-plane-verifier | 1 | none |
| T2 Linux launch + shell-routing harness | `scripts/lanes/**`, `tools/agent_supervisor/launch_seam.py` wiring, bash analog of `ps_tests/**` | G0,G2,G3,G4 | code-reviewer, ci-evidence-verifier | 2 | none |
| T3 Linux CLI identity + fixture recapture + recert | `tools/agent_supervisor/fixtures/**`, manifest binding, cert report | G0,G2,G3,G4,G5 | control-plane-verifier, security-reviewer | 3 | none (cert is orchestrator-executable; D-017) |
| T4 Codex admission (dep-security + G5) | lockfile/manifest for `@openai/codex` pin, provenance report | G0,G5 (+ dependency-security gate) | security-reviewer | parallel to T1–T3 | none for admission |
| T5 Claude independent-reviewer path | `tools/agent_supervisor/{+claude_reviewer.py,review_cadence.py,review_packet.py}`, schemas, tests | G0,G2,G3,G4,G5 | code-reviewer, control-plane-verifier | 4 | none |
| T6 Combiner stage | combiner module + `gate_wave.py` wiring, schema, tests | G0,G2,G3,G4,G5 | code-reviewer, security-reviewer | 5 | OD-B model choice before build |
| T7 Resource-fit / 5-lane tuning | `config.*`, `resource_sampling.py`, `run_budget.py` | G0,G2,G3,G4 | ci-evidence-verifier | 6 | none |
| T8 Commissioning + sign-in + certified start | runbook/docs + owner-typed start | certification evidence, lane-1 canary | control-plane-verifier (verify stored evidence) | last | **codex sign-in; supervised-mode prompt-digest start approval** |

Owner-typed steps (never agent-run): the Codex sign-in (T8, R006) and the live certified start /
supervised prompt-digest approvals (runbook §12 `:334-338`). Optional owner UAC-equivalent:
root-owning the Linux config for T1 hardening.

---

## 8. Risks and the smallest set of owner decisions

**Risks**
- **Codex version churn.** `latest` (0.160.0) is 0.15 d old and hourly alphas publish constantly;
  the age gate fails closed. Pin the newest stable ≥7 d (0.156.1 today) and re-verify flags on the
  installed binary.
- **8 GB / 5 lanes OOM** from synchronized review+combine spikes — mitigated by a global
  review-process semaphore and a ~5.6 GiB pause ceiling (§5).
- **Fable combiner exhaustion** (B-024 account-wide, D-060) — avoided by defaulting to Opus 5.5.
- **Recertification scope creep** — every `tools/agent_supervisor/**` edit invalidates the frozen
  cert; batch T1–T3 into one recert window.
- **Combiner weakening reviews** — prevented by union-not-intersection, evidence-to-drop,
  worst-verdict-governs, source tags, combiner ≠ producer, and orchestrator-records-gate (ADR-005).
- **Independence ceiling** — the combiner shares a provider with one reviewer; mitigated by fresh
  instances, distinct models, and auditable source-tagged findings.
- **B-026 honesty** — the Linux loop does not close the PC blocker; only a scope note is recorded.

**Smallest set of owner decisions**
1. **OD-B — combiner model (R008):** approve **Opus 5.5** (recommended) or pick Codex-higher-end.
2. **OD-C — Codex sign-in (R006):** owner runs the sign-in on the server, once, at T8.
3. **OD-D — B-026 disposition:** keep the PC loop (recommission later) or retire it in favour of
   the cloud loop (this is the honest path to "resolving" R004).
4. Ongoing (not one-time): the supervised-mode certified-start approval and prompt-digest approvals.

(The move itself, R001, is already authorized by D-091.)
