# D-024 Amendment 8 — Codex discussion channel + Telegram notifications before activation; re-certification sequencing (owner instruction 2026-08-28)

Captured: 2026-08-28 UTC by the orchestrator (Fable 5), verbatim from the owner's mid-turn
interactive message (channel: Claude Code interactive session, user message delivered mid-turn
during M0-T096 unit-I implementation; the harness's standard mid-turn delivery note is framing,
not owner text, and is excluded from the verbatim block). Base identity at capture: branch
`control/D-024-fable-codex-loop`, unit-I deliverable committed at
`5ff7f0887f8a1ab833c386e675d97a59ef0efb13`, M0-T096 claimed/in_progress (pre-submit).
Amends: `source-001.md` (owner directive v4). Requirement IDs assigned: D-024-R231..D-024-R249.

Reconciliation (the determination the message itself orders, recorded before any scope change):

- **A NEW AMENDMENT IS REQUIRED.** The two capabilities (persistent same-terminal Codex-only
  discussion channel; Telegram notification sink), their closed disposition vocabulary, the
  secrets/one-way/failure-isolation rules, the /btw honesty prohibition, and the
  post-addition re-certification sequencing are NOT present in R001–R230. Overlaps exist but
  none covers the new obligations: R083/R084/R088/R089 built the `/loop-*` operator surface
  and its honest interception limits (reused, not equivalent); R093/AD-083 bound review
  packets (reused by R237); R146 lists prohibitions (R248 restates and ADDS "modify global
  Claude settings"); the prior notification posture (terminal sink only; email/remote
  owner-gated) is NARROWED by this amendment's explicit one-way Telegram authorization with
  its own owner-gated live-send canary (R245).
- **M0-T096 scope is UNCHANGED** (the message's own instruction): the claimed unit completes
  as contracted; the new rows bind to the NEW tasks (M0-T108 Codex discussion channel,
  M0-T109 Telegram sink, M0-T110 final golden re-certification), never onto the already
  claimed packet.
- **Activation-package presentation moves behind R247:** the M0-T096 activation-package
  DOCUMENT remains a unit-I deliverable, but presenting the R187/R595 activation package now
  requires the re-run golden certification at the FINAL frozen identity after both additions.

Forward trace: opening paragraph → R231; "I require two additional capabilities" → R232;
/btw paragraph → R233; CODEX DISCUSSION list 1 (command surface) → R234; interception
paragraph → R235; fresh-invocation context list → R236; never-send/reuse paragraph → R237
(sentence 1–2), R238 (sentence 3); disposition paragraph → R239; promotion/queueing
paragraph → R240; TELEGRAM sink list → R241; one-way sentence → R242; secrets sentence →
R243; redaction/retries/dedup/isolation sentence → R244; live-send sentence → R245;
SEQUENCING paragraph sentence 1–2 → R246, sentence 3 ("must be completed before
continuous-mode activation") → R232; certification paragraph → R247; prohibitions
paragraph → R248; "First report" list → R249.

---VERBATIM-BEGIN---
OWNER DIRECTION — capture this verbatim as the next D-024 amendment before further activation work. Reconcile it against the live ledger and current M0-T096 state before changing scope.

I require two additional capabilities before continuous-mode activation:

1. A persistent same-terminal Codex-only discussion channel.
2. Telegram notification delivery for stuck/approval/completion conditions.

Do not represent a custom Claude Code command as equivalent to built-in /btw without measured proof. Official Claude Code behavior currently says ordinary commands submitted while Claude is responding are queued until the turn ends, while /btw is a special built-in command. Preserve that limitation honestly.

CODEX DISCUSSION REQUIREMENTS

Provide a user-invoked same-terminal command surface such as:
- /loop-codex new <question>
- /loop-codex continue <thread-id> <message>
- /loop-codex show <thread-id>
- /loop-codex promote <message-id>
- /loop-codex close <thread-id>

Use the existing user-only skill and UserPromptSubmit interception architecture. A successfully intercepted Codex discussion command must be blocked and erased before Fable receives it. Prove zero Fable-context pollution on the installed Claude Code version. The response must be displayed to me in the same terminal.

A fresh Codex invocation must not start from the beginning or scan the complete repository. Every turn must receive:
- A bounded durable discussion summary.
- A bounded number of recent discussion exchanges.
- Fresh current supervisor/campaign/task/checkpoint/health state.
- Relevant repository evidence references.
- Read-only access for deeper inspection when required.

Never send the full Claude transcript, full repository, all source code, full logs, or unrelated history. Reuse the existing evidence-packet, redaction, token-budget, frozen-identity and read-only Codex machinery. Prefer commit SHAs, content digests, changed paths, diff hunks, symbols, tests and graph references over unstable bare line numbers.

The discussion must not automatically alter Fable’s instructions. Codex responses require an explicit disposition:
ADVICE_ONLY, QUEUE_NEXT_BOUNDARY, REVISE_CURRENT_TASK, PROPOSE_NEW_TASK, URGENT_PAUSE, or STOP_FOR_OWNER.

Only existing authorized repair findings may enter the current Fable task through the existing review route. New features, changed priorities or expanded scope require my explicit promotion/approval and durable directive/task capture. Queue nonurgent information for the next safe boundary. Pause only for genuine safety/integrity urgency.

TELEGRAM REQUIREMENTS

Add a bounded Telegram notification sink for:
- STOP_FOR_OWNER
- approval waiting
- circuit-breaker/open stuck state
- repeated CI failure
- unrecovered controller/session failure
- quota/refusal hold
- golden-run completion
- campaign completion

Start one-way only. No Telegram approvals, merges, code execution or configuration changes in this unit. Store the bot token and chat identifier only in an approved local secret mechanism, never Git, packets, logs, telemetry, reports or messages. Apply redaction, bounded retries, deduplication and failure isolation so Telegram downtime cannot stop the coding loop. A real Telegram send remains an owner-gated exact-command canary.

SEQUENCING AND CERTIFICATION

Do not silently broaden the currently claimed M0-T096 contract. Determine the safest bounded task sequence and capture it durably. These capabilities must be completed before continuous-mode activation.

Any supervisor or operator-channel change after a golden-run identity invalidates the affected final certification. Therefore run the required affected/full golden certification again after both additions, against the final frozen code identity, before presenting the R187/R595 activation package.

Do not activate continuous mode, enable the live 4.8 bridge, touch PR #241, admit the Agent SDK, add MCP servers, modify global Claude settings, or cross another owner-only boundary.

First report:
1. Whether the direction is already authorized or requires a new amendment.
2. The proposed bounded task sequence.
3. Which existing components will be reused.
4. The exact official Claude Code limitation on same-terminal mid-turn custom commands.
5. What certification must be rerun after these additions.
Then proceed through all non-owner-gated work.
---VERBATIM-END---
