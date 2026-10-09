# M5-T142 producer report

Producer: frontend-engineer (an AI agent). Not a human or professional review. Read-only of the
ledger; this report and the seven source files are the only writes.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a2c693d2163da91dc`
Base (claim-seam head, reset --hard): `a1859c23edcc40fb84ca7a497bf2fba1851f70ec`

The results screen now shows each condition of a figure as its own line under a visible marker word
`Conditional`, sets a withheld result's reason and its kind-of-gap line apart, and announces a new
result and each failure to screen-reader users. One representation of the conditions (ruling L1):
the per-line list replaces the old joined line; `ShownValueView.condition` (string|null) is gone and
`ShownValueView.conditions: readonly string[]` is populated in the existing `shownView`.

## The two texts the website adds (ruling L3), and where

- `Conditional` — the state marker, a new const `CONDITIONAL_MARKER` in `AnswerCard.tsx`. Rendered
  in `ConditionBlock` beside/under every conditional figure (headline and each row), normal weight,
  plain text, read out with the figure it marks. Never an image, never colour alone.
- `Development results are ready.` — the AT-only success announcement, a new const
  `RESULTS_READY_ANNOUNCEMENT` in `ResultsPanel.tsx`, set on the polite live region on a success.

Reused unchanged (no new text): `Not known`, `Not available`, the extracted `NOT_CONNECTED_TITLE`
("Results are not connected yet", now shared by the not-connected card and its announcement so they
cannot drift), and each failure notice title.

## Table of states -> what the user sees/hears -> the test that pins it

| S | State | What the user sees / hears | Test (id + file) |
|---|---|---|---|
| S1 | settled value | the figure alone: no `Conditional`, no condition line, no `Not known` | `S1: a settled value shows the figure alone` (three-answers-panel.test.tsx) |
| S2 | conditional, 2 conditions | `Conditional` marker + exactly 2 `<li answer-condition>`, each the assumption verbatim, normal weight | `S2: a conditional value shows exactly its conditions, each verbatim, under the marker` (three-answers-panel) |
| S3 | conditional, 1 condition | `Conditional` marker + one line equal to the assumption | `S3: a single-condition value shows one line...` (three-answers-panel) |
| S4 | conditional headline | the large number renders with the adjacent `Conditional` marker (never alone) and the list below | `S4: a conditional headline figure renders with the marker; the number never renders alone` (three-answers-panel) |
| S5 | withheld (journey envelope) | each: `Not known` + reason (normal weight) + the kind-of-gap line as its OWN element, no figure, not inline-joined | `S5: each withheld envelope value shows 'Not known' + reason + its own kind-of-gap line...` (three-answers-panel) |
| S6 | settled+conditional+withheld in one card | told apart by the page text (`Conditional`, `Not known`, neither), asserted on textContent only | `S6: settled, conditional and withheld in one card are told apart by the text, not by colour` (three-answers-panel) |
| S7 | success fetch | live region reads `Development results are ready.` | `S7: a successful result announces the fixed ready sentence` (results-panel.test.tsx) |
| S8 | each failure outcome (10) | live region reads the SAME title the notice shows | `S8: <outcome> announces the notice's own title` x9 table + `S8: client_timeout...` (results-panel) |
| S9 | 404 not connected | live region reads the not-connected card's own title | `S9: a 404 announces the same title the not-connected card shows` (results-panel) |
| S10 | request in flight | live region is `''` while busy; announced only on arrival | `S10: the live region is '' while a request runs` (results-panel) |
| S11 | retry fails the same way | region clears to `''` between, so the identical title announces again | `S11: a retry that fails the same way clears to '' between...` (results-panel) |
| S12 | 2 conditions, one already 'If ' and one not | two lines; first verbatim, second prefixed 'If '; neither holds the other's text (L1) | `S12: 'If ' is put in front per entry only when the entry does not already begin with it` (three-answers.test.ts) |

Reader-layer shape also pinned in three-answers.test.ts: a settled value's `conditions` is `[]`;
two conditions become two entries (none joined). Existing reader test updated from
`shown.condition` to `shown.conditions`.

## The red proof (before the fix), one line

With `conditionList` reverted to join the assumptions into one item (today's behaviour), the card
test S2 expected 2 `answer-condition` items and got 1 (`expected [ <li> ] to have a length of 2 but
got 1`); reader tests S12 and "two conditions become two lines" also red; `VITEST_EXIT=1`.

## Mutation proofs (applied in place, test run RED, reverted exactly)

- Reader joins the conditions again (`conditionList` returns one joined item) -> RED: S2 card
  (got 1 item), S12 and reader "two conditions" (`[Array(1)]` vs 2). Reverted.
- Card drops the marker on a conditional headline (`<ConditionBlock conditions={[]}>` on the
  headline) -> RED: S4 (`Unable to find [data-testid="answer-conditional-marker"]`). Reverted.
- Kind-of-gap line joined inline again (re-add `{" "}` before the gap span) -> RED: S5
  (`gap.previousSibling` is a whitespace node, not the reason element; full-row text mismatch).
  Reverted.
- Panel announces nothing on a success (success branch returns `""`) -> RED: S7
  (`expected '' to be 'Development results are ready.'`). Reverted.
- Panel announces a title different from the card's (failure branch returns a fixed string) -> RED:
  all 10 S8 cases (announcer != the rendered notice title). Reverted.
- Region not cleared while busy (drop the `busy ||` guard) -> RED: S11 (the region never returns to
  `''` during the retry, so the re-announce never fires; waitFor timed out). Reverted.

After every revert the full touched suite is green again (`VITEST_FINAL_EXIT=0`, 485 passed).

## What is NOT changed

No file under services/, packages/, .github/, tools/ or .claude/. No dependency or lockfile change.
No e2e spec and no harness file (`results.flag-on.spec.ts`, `results.spec.ts`,
`e2e/harness/fixture_api.py` untouched — their condition checks are `toContainText` substrings each
within a single assumption, so splitting into list items does not break them; I read
`results.flag-on.spec.ts` in full and no assertion breaks). No switch turned on. No second standing
label. No results-document word retyped (every assumption/reason rendered verbatim). No new
top-level symbol in `three-answers.ts` and no scope-view split (DB-206 d stays a separate follow-up).
`ResultsForm.tsx`, `OutcomeAnnouncer.tsx`, `ThreeAnswersPanel.tsx`, `ScopeSummary.tsx`,
`ResultsStatusStrip.tsx` are read-only and untouched (the panel imports the existing
`OutcomeAnnouncer` with `testId="results-announcer"`).

## Checks a-g (direct exit codes; `echo $?` immediately after)

- a. `npx --yes npm@11.18.0 ci --no-audit --no-fund` (in apps/web, once): exit 0.
- b. `npm run lint`: exit 0 (2 pre-existing warnings in untouched files `lot-site-setup.test.tsx`,
  `study-vocabulary.test.ts`; 0 errors).
- c. `npm run typecheck` (`tsc --noEmit`): exit 0.
- d. `npx vitest run src/lib/architect/__tests__ src/components/architect/answers/__tests__
  src/components/architect/__tests__/results-panel.test.tsx`: exit 0; Test Files 23 passed (23),
  Tests 485 passed (485).
- e. `python3 tools/modularity_check.py --check` (repo root): exit 0; before and after both
  `failures 0; warnings 30`; byte-identical (no NEW warning). `three-answers.ts` keeps its
  pre-existing `symbol_ceiling` warn, unchanged.
- f. red proof `VITEST_EXIT=1` and six mutation proofs each `*_EXIT=1` then reverted (above).
- g. `git status --porcelain` and `git diff --name-status <base> HEAD`: only the allowed paths (the
  seven source/test files above plus this report).

The whole unit suite, the build and the whole browser suite are NOT run here (ruling L2: the owner's
test preview holds the ports); they run in CI on the pushed head and are read there before any gate.

## For a reviewer of the running screen

- A conditional figure: the big number is immediately followed by the plain word `Conditional`
  (normal weight, muted) and a bulleted list with one condition per line; confirm it no longer reads
  as confirmed and the two long "If ..." conditions no longer run together.
- A withheld value: `Not known — <reason>` in normal weight, then the kind-of-gap line on its own
  line below it.
- Screen reader: on pressing Show results, a success says "Development results are ready."; a 404
  says "Results are not connected yet"; each failure says the same title shown on the card; nothing
  is announced while the request is running, and a retry that fails the same way announces again.
- CSS carries the weights/spacing (`.ta-conditional-marker`, `.ta-condition` normal weight;
  `.ta-withheld-reason` weight 400; `.ta-gap-kind` display:block + top margin); jsdom cannot assert
  computed weight, so the "set apart / not inline-joined" guarantees are pinned structurally
  (separate sibling elements, no joining whitespace node). A real-browser/contrast pass is owed to a
  G3 walkthrough.
