# D-066 source 001 — owner directive, interactive chat, 2026-09-17 (verbatim)

## Owner message (verbatim)

> What about the map graph I, that we built that supposedly is supposed to help the program find files much faster by grouping it into categories so it can understand, have a whole map system? I think we put in a lot of effort in building it, but to my knowledge, I don't think Codex is using it at the moment. Is there a way that we can quickly make sure that Codex gets to use it and we can do a little test while it's running to see if it, if it saved time or tokens by using it? Having Codex involved in this part by having him also run a test. But I don't want to get sidetracked. I want this as part of the next, you know what I mean? Whatever it's doing next to, to do this together.

Orchestrator findings at capture: the graph cache was STALE (query.py refused to serve);
neither the M5-T032 packet nor the Codex reviewer setup referenced the graph; after
regeneration (728 files, 15255 nodes, 6762 edges, ~18 s) a downstream query on
provenance-link.ts surfaced a consumer missing from the M5-T032 allowed_paths, which was
added the same hour.
