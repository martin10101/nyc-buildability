# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff - seq 101: 186 accepted; M0-T156 (D-040-R003) ACCEPTED - control-plane CI red RETIRED; D-041 C1 is the product priority

Generated 2026-09-12 ~06:15 ET by the same orchestrator session (seq-100 continuation). Root
`C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `candidate/D-024-mrl-option-b`, HEAD
`c4dbe854` **pushed**. `main` untouched at `d8b3899f`. PR #241 OPEN - NEVER merge.

## STATE (verify live; ledger wins)

1. **Accepted = 186.** M0-T156 (D-040-R003 directive-digest CRLF/LF normalization) ACCEPTED
   end-to-end this session: normalization primitive `sha256_text_artifact` adopted at exactly
   the three registry-integrity sites (c2 source / c14 requirements-body / migration-manifest;
   `sha256_file` raw-identity path UNTOUCHED), six manifest digests re-stamped append-only with
   audit_log entries, sources byte-immutable. **CI run 34685572048: control-plane job SUCCESS -
   the standing red is RETIRED**; the ONLY red on the branch is owner-gated
   web-dependency-security (Next.js RCE, D-040-R004). Arc: first-push CI green -> submit
   (identity 73d2a750) -> G1/G4/G5 wave all PASS with ZERO required corrections -> gates at
   3714c1a8 -> DCV rows (D-040 R003 PASS + D-001 empty-set) at 16a2261e -> accept c4dbe854.
   Reports under `project-control/reports/M0-T156-*`.
2. **D-041 captured (peer session, 2fa8c332): gap-list C1 is the owner's TOP product priority**
   ("Yes but I approve c1 lets do it"). C1 = explicit remaining-development-rights line:
   existing built floor area vs draft residential FAR cap, own labeled line, honest negative
   remainder -> professional-review flag (never clamped/hidden), missing inputs -> standard
   unsupported treatment (never estimated). Cite `D-041:D-041-R001`; four-case scenario pack
   required (normal / over-built negative / missing existing-area / missing FAR rule). R003
   scope limit: C1 ONLY - no other Part-4 gap-list item may cite D-041.
3. **C1 design inputs (owner-supplied Codex research, `docs/design/astra-presentation-research.md`
   at fd73a020) MUST fold into the packet:** (a) §3.1 precise-noun rule - label what the engine
   computed (e.g. "unused draft zoning floor area (FAR-derived)"), never "maximum buildable
   area"; scope note that geometry/height/yards are NOT assessed; (b) ZR 12-10 - carry the
   explicit MACHINE-READABLE assumption "treats the selected tax lot as the zoning lot" in the
   API document, not display-only; (c) §3.3 honest-result-states table feeds the scenario list.
4. **D-040 queue after C1:** R002 flag unification (INTERNAL_RULE_EVAL_UI vs
   INTERNAL_RULE_EVAL_ENABLED; Render env-var rename = owner return item), then R001 Packet-3
   lot outline (official-source research on MapPLUTO FIRST; MapLibre needs /dependency-security
   admission + age gate; hold rule §2.1 releases ONLY this increment).
5. **Owner works in the SAME checkout in parallel** (docs/design commits kept landing mid-arc:
   ui-prototype copy, the research doc, MVP_ARCHITECT_REVIEW_QA). Verify every foreign commit
   touches nothing in an in-flight task's allowed_paths; their pushes preempt in-flight CI
   (cancel-in-progress); HOLD pushes while a needed run is in flight.
6. Non-blocking follow-up backlog from the M0-T156 wave (advisories only, no task yet): G5 F-1
   bare-CR rejection hardening; G1 A1 manifest audit_log key drift vs schema; G1 A2
   status_projection normalizer divergence; G4 LOW migration-manifest flip test.

## NEXT ACTION (in order)

1. Contract D-041 C1 via /start-controlled-task citing `D-041:D-041-R001`: server-side
   deterministic subtraction (draft FAR-derived cap MINUS PLUTO existing built floor area)
   surfaced in the scenario document with per-fact provenance, the machine-readable
   tax-lot-as-zoning-lot assumption, precise-noun labeling, and the four honest states
   (terrain exploration for the packet may already be in flight - check).
2. UI rendering of the C1 line (own labeled line + professional-review routing + missing
   states) - same task or a follow-on packet, orchestrator's call per modularity.
3. Then D-040 R002 (flag unification), then R001 (Packet 3, research first).
4. Do not self-assign beyond D-040/D-041 scope (Part-4 gap list awaits owner triage).

## STANDING RESTRICTIONS (unchanged)

NEVER merge PR #241. Supervisor frozen/SHADOW-ONLY (changes need cited D-024-R###). Expansion
hold except the §2.1 lot-outline release. No bare `git stash`. No new packages without
/dependency-security admission (MapLibre for R001 WILL need G5 provenance review + age gate).
No hosted web deploy before the Next.js RCE fix (owner-gated). API URL private; Geoclient key
ONLY in owner env + Render dashboard. Thin client. G6 on M4-T001 = owner-only. Stop-and-ask
only for credentials/payments/legal (D-008). Bootstrap Gate 0 before any write.

## AUTHORITATIVE FILES (smallest set)

`project-control/state.json` + `directives/D-041-c1-development-rights/` (the priority) +
`directives/D-040-scoped-unblocks/` (the queue) · `docs/design/astra-presentation-research.md`
§3.1/§3.3 (C1 output contract) · `tasks/M0-T156.json` + `reports/M0-T156-*` (latest full-arc
pattern incl. DCV row shapes) · `.claude/rules/expansion-agent-dispatch-hold.md` §2.1 ·
`CLAUDE.md` · this file.

## COPY INTO THE NEW SESSION

resume from handoff seq 101: work from durable repository evidence. Verify root/branch/HEAD
(expect C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 on candidate/D-024-mrl-option-b), Bootstrap
Gate 0, read CLAUDE.md + docs/SESSION_HANDOFF.md, run `python tools/project_control.py status`,
reconcile vs live git/CI (origin may have advanced; ledger and CI win). 186 accepted; M0-T156
done, control-plane red retired. Execute NEXT-ACTION item 1: contract D-041 C1
(remaining-development-rights line) citing D-041:D-041-R001, folding in
docs/design/astra-presentation-research.md §3.1 precise-noun labeling + ZR 12-10
machine-readable tax-lot-as-zoning-lot assumption + §3.3 honest states; four-case scenario
pack; normal gates. Then D-040 R002 -> R001. Report READY TO RESUME or BLOCKED before changing
anything. Stop only for owner-only items (credentials/payments/legal, PR #241, Next.js
upgrade/deploy, Supabase, G6).
