# D-050 source-003 (amendment 2, verbatim) — owner directive, interactive chat (companion session), 2026-09-13

Amends D-050 by adding an IMMEDIATE-UPDATE + COMPACT-CLOSURE lifecycle and a phone-access
guarantee for the research queue. Context: the owner operates from their phone (Remote Control)
while the PC is elsewhere, and cannot open repository files locally.

## owner-message-verbatim

> My problem is that I am running it on my phone and my pc is a different spot how do I have
> access to the research file and on one other note, the research file needs to be updated as
> soon as I bring back the results. And if it's satisfied with the research, everything checks
> out, then that part of the research should be taken off. And you know basically, so it doesn't
> get bloated with stuff that 's already figured out

## capture-context

- ACCESS: the canonical phone-readable copy of the queue is the PUSHED branch file rendered by
  GitHub (repository is public):
  https://github.com/martin10101/nyc-buildability/blob/candidate/D-024-mrl-option-b/docs/RESEARCH_REQUESTS.md
  Therefore every queue update must be committed AND pushed promptly — a dirty-local or
  unpushed queue file is invisible to the owner. The owner can also always ask the companion
  session (from the phone) to read out open requests or take dictated results.
- IMMEDIATE UPDATE: when the owner returns results (to either session), the receiving session
  updates the entry to ANSWERED (date + named verification target) and commits+pushes in the
  same working step — never batched for later.
- COMPACT CLOSURE: when a request is SATISFIED — the answer verified/consumed and everything
  checks out — its full entry is REMOVED from the active queue and collapsed to a ONE-LINE row
  in a "Closed" register at the bottom of the file (id — one-line outcome — closed date — where
  the answer now lives, e.g. the source capture / report / architect-doc entry). Full historical
  text remains in git history; the active file never accumulates figured-out material.
- Adds requirement D-050-R006. All prior D-050 rules unchanged (non-blocking; leads-never-
  sources; interpretation routing; active notification R005).
