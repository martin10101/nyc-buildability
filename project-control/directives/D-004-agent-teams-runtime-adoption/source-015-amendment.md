# D-004 — source-015 (owner amendment 14, verbatim)

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `421265709f81a40e20f3d890609907ed932967dd`.

Head at capture time: `task/M0-T027-closeout-phases-3-4` =
`f4c7c3be0e45c125c2bf1bf4790fc8e5ab053424`; `origin/main` =
`11f3540c602849f4100517f35b7b93eca6742a8d` (unchanged).

Requirement IDs added by this amendment start at `D-004-R568`; no existing source file or
requirement row is edited.

## Scope

Per the owner's standing instruction for execution authorizations in this arc
(`source-013-amendment.md`), every row below carries `task_ids: ["D-004-OPTIONB"]` — the session
sentinel. This is execution authority, not new M0-T027 task-content. Verified after the write:
M0-T027's resolver-derived applicable set remains **233** and no row of this amendment enters it.

## R024 redaction inside owner-verbatim text (owner-approved, 2026-07-30)

**Two substitutions were applied to the verbatim owner message below:**

| occurrences | substitution |
|---|---|
| 2 | truncated session-id prefix -> `<REDACTED-SESSION-ID>` |

Both sit **inside owner-verbatim text**, applied only on the owner's explicit approval rather than
on the orchestrator's judgement. As in `source-014-amendment.md`, **the original text at both
positions named the identifier being redacted** — the owner was specifying which string to remove
and which string to grep for — so both lines now read self-referentially. Nothing else in the
capture was altered: no instruction, constraint, prohibition, deferral, or ordering was changed,
added, or removed.

## Supersession note

Item 3 of the message below states that `source-014-amendment.md` "won't be committed. No action."
The orchestrator reported back that this could not hold, because `manifest.json` already recorded
that file as `sources[14]` with a content digest and `requirements.json` already carried rows
R553–R567 whose `source_ref` points at it — so a fresh checkout would fail
`tools/validate_directive_compliance.py` on a cited-but-missing source. The owner then **approved
Option 4** (commit the capture with the identifier redacted and annotated), which supersedes item 3.
The item is preserved verbatim below as issued; the supersession is recorded here rather than by
editing the captured text.

---

## Owner message (verbatim, complete as received, with the two disclosed redactions)

Two more redactions, then stop.

1. Truncated prefix <REDACTED-SESSION-ID> in M0-T027-dcv-verification.md — redact it too,
   → <REDACTED-SESSION-ID>, same convention and inline annotation as the others.
   Consistency is worth more than the 8-vs-10-char threshold; I don't want a
   "why is this one different" question later.

2. Email myhappybook212@gmail.com in G5 — LEAVE it. It's already in every commit
   trailer, so redacting one report body is cosmetic and doesn't un-publish it.
   Log it under R561 as part of the systemic PII question for my later decision,
   alongside the 4 pre-existing files on main that carry it.

3. source-014-amendment.md — untracked, verbatim capture of my own message, won't be
   committed. No action.

After the item-1 redaction: STOP, still uncommitted. Show me (a) the one-line diff for
the dcv file, and (b) re-run grep confirming the full session id AND the truncated
prefix <REDACTED-SESSION-ID> both return zero matches across tracked files. Then wait.

Do not commit, submit, push, merge, accept, or rebuild verification.json yet. R024
stays "remediated, pending independent verification" — I'll release the verifier pass
in a later turn after I've seen the final grep.
