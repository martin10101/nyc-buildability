---
description: Route to the project's engineering-reliability standard — debugging method, change sizing, red/green and mutation proof, async/idempotency/retry design, error surfaces, verification contexts, defect triage, and the frozen-benchmark rule. Invoke before changing production behavior; when debugging a defect, a flake, or an incident; when designing or reviewing an async, concurrent, network, or background-job flow; when building a retry, replay, resume, or idempotency surface; when shaping a user- or caller-visible error path; when reviewing another identity's work; and before claiming a task is complete, faster, cheaper, or more reliable. Manually invocable as /engineering-reliability.
---

This is a router, not a copy of the standard. The authoritative text is
`docs/ENGINEERING_RELIABILITY_STANDARD.md`. Read the sections your work triggers — not the whole file.

## Route by trigger

| Your work | Read |
|---|---|
| Any behavior change to production code | §2 smallest fitting change, §3 behavior proof, §8 verification contexts, §9 triage |
| Debugging a defect, a flake, or an incident | §1 debugging discipline, §3, §8, §9 |
| Async, concurrent, network, or background-job flow | §4 async flows, §5 idempotency, §6 retries, §7 errors, §8 |
| Retry, replay, resume, or idempotency surface | §5, §6, §8 |
| User- or caller-visible error path | §7, §3 |
| Reviewing another identity's work | §8, §9 |
| Claiming done / faster / cheaper / more reliable | §3, §8, §10 measured claims |

The standard's §0 lists rules that live elsewhere (gates, acceptance scenarios, modularity, typed
errors, secrets, dependency security). Follow the citation to the canonical document; do not restate
a rule in a report, a packet, a comment, or a new document.

## Rules of engagement

- **The standard is engineering guidance, not authority.** It does not override `CLAUDE.md`, the
  gates (`docs/GATES_AND_CHECKPOINTS.md`), authority and lifecycle
  (`docs/PROJECT_CONTROL_PROTOCOL.md`, ADR-005/ADR-006), or any active owner hold. It never accepts a
  task, waives a gate, authorizes a merge, or releases a hold.
- **Cite the section you applied**, with its number, in the task evidence or gate report — not
  "followed the reliability standard".
- **A triggered section is mandatory, not advisory.** If a section applies and you did not satisfy
  it, record that as an open item; do not submit past it silently.
- **Reviewers:** an unsatisfied triggered section is a finding under §9, classified with a stated
  severity and a named consequence — never a blanket FAIL citing the standard as a whole.
- **This skill adds no scripts, assets, agents, or dependencies**, and adopts no third-party
  framework or plugin. If a section needs new tooling, that is a separate scoped task.
- **No claim about this standard's own effect** on defect rate, speed, token use, or cost (§10.8).
