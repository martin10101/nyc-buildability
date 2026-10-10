# Wave 20 - concurrency record (orchestrator, 00:00 UTC on 2026-10-09)

Three tasks on one branch (`task/wave20-presentation-slice`, from the main line `0bb6acb2`), reviewed at one head and merged as one pull request (owner rows R773 and source-079):
- M5-T148, shared presentation: part A (tokens) and part B (adapters), two builders side by side;
- M5-T150, the parcel's own outline (server only), one builder, beside M5-T148: three builders at once, the owner's limit;
- M5-T149, the website slice: parts A, B and C, three builders side by side, after M5-T148 is integrated.

No two tasks and no two parts share a file or folder (checked by script at the contract: every allowed path of each task against every other, as exact paths and as folder prefixes). Heavy runs and merges one at a time; the browser tests are run by the orchestrator only, because they use the owner's preview ports. Builders' run times are added to the producers' reports afterwards.
