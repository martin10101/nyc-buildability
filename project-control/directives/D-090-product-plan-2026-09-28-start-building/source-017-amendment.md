# D-090 source 017 — owner amendment, interactive chat (cloud session 0ba6d6a3), 2026-10-04 (verbatim)

Captured 2026-10-04 by the orchestrator (Claude Code session 0ba6d6a3-f9a0-4ebc-95d9-610739d030b5, model claude-fable-5-1) from the saved session transcript `~/.claude/projects/-root-project-nyc-buildability/0ba6d6a3-f9a0-4ebc-95d9-610739d030b5.jsonl` (line 2556, uuid `3a9e0840-f6fb-48de-b4b4-9ff2cecb613a`). A script copied the input's raw text; nothing was retyped. It is complete and byte-identical to the transcript except for the blockquote prefix ("> " on every line, ">" alone on an empty line); the raw text's SHA-256 is `d00d0360594fc4d97b44ccf58d7d43fbbccbd189c8dd58702e2ff1b1b2d72b88`. Times are the transcript's UTC timestamps. Message numbers continue from source-016 (message 43). Frozen base at capture: integration head `63fe1c51e6f73c36c20d517e68dc3edf8e835484` (origin/candidate/D-024-mrl-option-b, the merge of PR #383, the walkthrough record).

Message 44 (2026-10-04T01:33:34.527Z, SHA-256 `6409fd6b91676973c4a9d52e541076d1ed8a134790fe7aeac40b619eb1df0d87`) asked for the full walkthrough report to consult with the owner's consultant; it was answered by publishing the record as a private page (https://claude.ai/artifact/YGK2dU26Z9NVKEdenhmsU2) and carries no standing requirement.

## Owner message 45 — 2026-10-04T01:50:38.574Z, session 0ba6d6a3 {#owner-message-45-verbatim}

> The walkthrough makes the remaining gaps clear. Please act on these findings:
>
> 1. Describe the demonstrated progress accurately. This proves several components work together with test inputs. It does not yet demonstrate a complete address-to-screen workflow. Correct wording that suggests otherwise.
>
> 2. Investigate the height discrepancy first. The sample building is 20 feet tall, while the report lists a 30-foot minimum wall height. Check the applicable rules and any exception. Either document why this particular sample complies or fix the generator and add a meaningful test. Also show the qualifying-housing heights clearly as 30 / 45 / 65 feet.
>
> 3. Put the scope beside the numbers. The headline cards and exported drawings must visibly say “Tax-lot-only estimate,” identify lot 70, and disclose the assumed corner conditions. Keep whole-site and remaining capacity unconfirmed. Preserve our settled wording:
>    “Remaining development capacity: Not confirmed.”
>    “Needs verified zoning-lot boundaries and existing zoning floor area.”
>
> 4. Prioritize one complete working journey: real address → selected lots and sourced facts → study → calculation engine → actual screen → available exports. Reuse the existing work. Identify the smallest remaining tasks and dependencies, including the keep/remove choice and existing zoning floor area. Demonstrate what works and clearly identify every remaining assumption or missing connection.
>
> 5. Explain the pending approvals together. For #369, #377 and #382, give one plain sentence describing each change, its review/test status, and why it needs my approval. This message does not approve those merges.
>
> 6. Tighten the CI proposal. Separate measured duplication from the unproven claim that it caused the Windows failures. State exactly which runs disappear and how required testing and the existing security policy remain satisfied.
>
> Continue already-authorized development under the existing review rules. Keep production switches off. Return one consolidated update with findings, completed fixes and genuine decisions needed from me.

## Context (orchestrator notes; the owner text above is the authority)

- The message responds to the 215-16 Northern walkthrough (D-090-R101; PR #383, merged 63fe1c51) and its page. Clause map:

  | Clause | Row |
  |---|---|
  | "1. Describe the demonstrated progress accurately. This proves several components work together with test inputs. It does not yet demonstrate a complete address-to-screen workflow. Correct wording that suggests otherwise." | R106 (new) |
  | "2. Investigate the height discrepancy first. The sample building is 20 feet tall, while the report lists a 30-foot minimum wall height. Check the applicable rules and any exception. Either document why this particular sample complies or fix the generator and add a meaningful test. Also show the qualifying-housing heights clearly as 30 / 45 / 65 feet." | R107 (new; sequencing "first") |
  | "3. Put the scope beside the numbers. The headline cards and exported drawings must visibly say “Tax-lot-only estimate,” identify lot 70, and disclose the assumed corner conditions. Keep whole-site and remaining capacity unconfirmed. Preserve our settled wording: “Remaining development capacity: Not confirmed.” “Needs verified zoning-lot boundaries and existing zoning floor area.”" | R108 (new); R038/R039 (in force: the settled capacity wording) |
  | "4. Prioritize one complete working journey: real address → selected lots and sourced facts → study → calculation engine → actual screen → available exports. Reuse the existing work. Identify the smallest remaining tasks and dependencies, including the keep/remove choice and existing zoning floor area. Demonstrate what works and clearly identify every remaining assumption or missing connection." | R109 (new) |
  | "5. Explain the pending approvals together. For #369, #377 and #382, give one plain sentence describing each change, its review/test status, and why it needs my approval. This message does not approve those merges." | R110 (new, return) + R111 (new, prohibition: no merge of #369/#377/#382 on this message); R021/R029 (in force) |
  | "6. Tighten the CI proposal. Separate measured duplication from the unproven claim that it caused the Windows failures. State exactly which runs disappear and how required testing and the existing security policy remain satisfied." | R112 (new); R104/R105 (in force) |
  | "Continue already-authorized development under the existing review rules." | R113 (new); R103, R020 (in force) |
  | "Keep production switches off." | R114 (new); R102, R048, R058 (in force) |
  | "Return one consolidated update with findings, completed fixes and genuine decisions needed from me." | R115 (new, return); R097 (in force) |

- **Orchestrator's readings (not owner wording), recorded in the rows:** (1) R107 "first" orders the Lane A engine work: the height investigation precedes the scope-disclosure engine change (both touch the generator). (2) R108 needs a contract slot (Lane C), the engine to fill it (Lane A), the cards (Lane D) and the drawings (Lane E) to show it — four lane PRs in dependency order, each green on its own. (3) R109 is first a plan (the smallest tasks and their dependencies, committed as a record) and then execution of the items that are already authorized under the lane plan; items that need a new owner decision are listed as such, not started. (4) R111 is read strictly: #369, #377 and #382 stay open until a later explicit yes per PR.
