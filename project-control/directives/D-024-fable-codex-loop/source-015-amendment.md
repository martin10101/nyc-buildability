# D-024 Amendment 15 — M0-T113 completes first; cycle-2 continuation protocol (owner instruction 2026-08-30)

Captured: 2026-08-30 UTC by the orchestrator (Fable 5), verbatim from the owner's interactive
message (typed after the seq-33 live-proof report: dispatch + Fable 5 + first checkpoint
achieved; certified HALT_UNSAFE from the independent Codex review; cycle-2 command handed
over). Base identity at capture: branch `control/D-024-fable-codex-loop`, HEAD
`3a83a3c49ad83cbe3dfc5449147bb8c55b992f2e` (local == origin; clean tree). Amends:
`source-001.md` (owner directive v4). Requirement IDs assigned: D-024-R298..D-024-R301.

Reconciliation: the owner sequences the M0-T113 closure BEFORE their cycle-2 continuation
(R298), requires the pre-continuation report of the clean pushed tip and the at-rest
journal (R299), and sets the cycle-2 stop protocol: on another counted stop there is NO
further restart (R300 — extends the R270 no-restart-loop rule to the cycle-2 outcome
specifically), all evidence is preserved, and the independent Codex review failure is
diagnosed as a SEPARATE bounded defect task (R301 — AD-093 defect lane; the task id is
allocated only if the condition fires; R301 binds to M0-T113 for verification of the
protocol's recording, and the future defect packet will cite this row on creation). No
owner gate is loosened; the cycle-2 start itself remains the owner-typed act.

Forward trace: sentence 1 ("Complete M0-T113 through its gates and acceptance first.") →
R298; sentence 2 ("Report the clean pushed tip and confirm the journal remains at rest
with zero open requests.") → R299; sentence 3 ("Then I will execute the supplied cycle-2
command.") → context anchoring R298/R299 sequencing (the owner's own act, no agent row);
sentence 4 ("If cycle 2 produces another counted stop, do not restart again; preserve all
evidence and diagnose the independent Codex review failure as a separate bounded defect.")
→ R300 (no restart + preserve evidence) + R301 (separate bounded defect diagnosis).

Anchors: #t113-first (s1), #pre-continuation-report (s2), #owner-runs-cycle2 (s3),
#cycle2-stop-protocol (s4).

---VERBATIM-BEGIN---
Complete M0-T113 through its gates and acceptance first. Report the clean pushed tip and confirm the journal remains at rest with zero open requests. Then I will execute the supplied cycle-2 command. If cycle 2 produces another counted stop, do not restart again; preserve all evidence and diagnose the independent Codex review failure as a separate bounded defect.
---VERBATIM-END---
