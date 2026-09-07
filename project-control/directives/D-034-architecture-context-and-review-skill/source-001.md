# D-034 — Architecture context + repo-local review skill (owner, 2026-09-07)

- **Captured:** 2026-09-07 (UTC), session_01WBbzN5Rx17CBSjky5uKmnY, channel: owner terminal
  prompt with 9 attached screenshots of social-media posts describing Claude Code practices.
- **Base identity at capture:** worktree `ctl24`, branch `candidate/D-024-mrl-option-b`,
  HEAD `20f6c81e`.

## Verbatim owner text

```
can u implementat it
```

## Attached-content transcription (the "it"; recorder's faithful summary of the 9 screenshots)

1. **PyTorch-style repo-local PR-review skill** — a review skill kept inside the repository,
   focused on what CI cannot judge: (1) CODE QUALITY — does the implementation make sense
   (unnecessary complexity, duplicated logic, bad abstractions, maintainability), not just
   "does it compile"; (2) TEST COVERAGE — do the tests actually cover the behavior that
   changed, not just "are there tests"; (3) SECURITY — review the diff for new trust
   boundaries, unsafe inputs, permissions, vulnerabilities; (4) BACKWARD COMPATIBILITY —
   could this silently break existing users or APIs. Invocable as `/pr-review <PR#>` or
   `/pr-review branch`. Prompt discipline: "Only report actionable problems. For every
   problem, point to the relevant code and explain the failure scenario."
2. **Evidence-before-DONE protocol** — five pieces of evidence before accepting DONE from an
   agent: (1) REQUIREMENT — show which requirement was actually implemented; (2) TEST —
   actually run the test that proves the requested behavior; (3) REGRESSION — what existing
   behavior could this change have affected and how it was checked; (4) DIFF — explain every
   changed file and why it was necessary; (5) UNPROVEN — explicitly state what could not be
   verified. "Never report DONE from implementation alone. Report DONE from evidence.
   Anything you couldn't verify must be explicitly marked UNPROVEN."
3. **ARCHITECTURE.md** — not a tour of every file; architecture context answering what is
   hard to infer safely: (1) WHAT EXISTS — the high-level system map; (2) WHO OWNS WHAT —
   which component owns each responsibility; (3) WHAT MAY DEPEND ON WHAT — boundaries plus
   explicitly documented forbidden paths; (4) HOW DOES DATA MOVE — the critical flows;
   (5) WHAT MUST STAY TRUE — architectural invariants (secrets server-side, domain logic has
   one owner, boundaries not bypassed, no new architectural patterns introduced silently);
   (6) WHEN SHOULD CLAUDE STOP — if a task requires breaking an architectural boundary:
   STOP → explain conflict → show impact → propose smallest change.

Screenshot files (session uploads, referenced not committed):
`C:\Users\MLFLL\.claude\uploads\0a3cc68b-...\{6f5f6bba,7c030337,9e8ed56e,bdd917a5,131f96d8,28d0fe20,44205a5b,598e799d,a8609b00}-image.jpg`.

## Capture context (recorder's note)

The evidence-before-DONE protocol (item 2) is ALREADY repository law here in stronger form
(gates G0-G7, producer-cannot-self-accept, independent verification, UNVERIFIABLE status,
/engineering-reliability completion-claim rules); implementation must NOT duplicate that law —
it folds the UNPROVEN-marking vocabulary into the new artifacts and cites the existing
mechanisms. Items 1 and 3 are genuinely new artifacts for this repo.
