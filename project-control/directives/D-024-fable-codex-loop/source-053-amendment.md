# D-024 Amendment 53 — Owner resolves B-021: Codex reviewer at MAX effort + fallback ladder + unavailability notification + easy model swap (owner directive, 2026-09-04)

- **Directive:** D-024 (fable-codex-loop campaign)
- **Kind:** amendment (append-only; amends source-001.md; follows source-052-amendment.md)
- **Issued by:** owner (interactive session, 2026-09-04, resolving blocker B-021 and expanding the
  Codex-reviewer directive)
- **Context:** the orchestrator raised B-021 — D-024 Amendment 52 (Codex reviewer max effort)
  conflicts with the permanent owner prohibition D-004-R159 ("no effort key ever written / the
  supervisor never passes effort"). The owner now explicitly lifts that blocker for the Codex
  reviewer and adds a fallback ladder, an unavailability notification, and an easy-model-swap
  requirement. Verified read-only (official sources): the GPT-5.6 codex family is Sol (flagship),
  Terra (balanced), Luna (volume/low-end); `gpt-5.6-luna` is a real model but is NOT in the
  current codex allowlist (config.toml allowed_models = [gpt-5.6-sol, gpt-5.6-terra]). The
  reasoning-tier ceiling is contested across sources (authoritative config reference:
  minimal/low/medium/high/xhigh with xhigh the ceiling; other sources claim max/ultra above it);
  a wrong value fails closed under --strict-config, so "max" resolves to the VERIFIED ceiling
  xhigh. GPT-6 Astra released 2026-09-03 with gated availability (~20 partner orgs).
- **Base identity at capture:** ctl24 `candidate/D-024-mrl-option-b` HEAD `8247c550` (local only),
  tree clean; origin/main `d8b3899f`; installed controller frozen `3f4cee86`.

## Verbatim owner directive

> When I call something, Max, of course, Max means whatever the top, um, is called over there. I don't need to quote the exact name of it if it's x high or whatever the name is called. You should understand by itself that Max goes to the highest ceiling of, uh, the model is able to do, like, in terms of thinking and so on. So, um, I don't know who plays that blocker over there, but there shouldn't be any blocker. Um, you should be able to set that the codex should use the max thinking ability. The max, uh, model, um, smartness. So, yes, go ahead. Said that because Codex is not going to be using that up. My biggest problem with general models for this... for the Fable and Opus four point eight was that it was using up tokens a lot. So that's why I said the main to Fable five. And on x high effort, that is... that in in only falls back if it's not available, like, if the tokens got used up or something like that, then it falls back to Opus four point eight x high. But then the sub agents as well, the the important sub agents is four point... is... I'm sorry. Can also use Fable five only for the very important sub agent. But the regular, the standard sub agents is four point eight. Again, that you don't need to charter the moment. But for Seoul... I'm sorry. For a codex, it's it's it's important to use the max. because in... this is the one who is going to review everything. But since he doesn't... it's not a lot of context that he uses up, you gotta stick to the max on that x high, whatever it's called. And, obviously, if it's not available, it gets used up, then we can downgrade it to to medium. And then if it's... if that is not available, I'm not... we should go to Luna. Luna is a very low end model, so I should be getting a a notification or something, or the the CLI should tell me that Codex is not available. a codec sole five point six is not available. Also, it should be easy to change because soon there's gonna be a new model that comes out. I think it's called Astra, but it's... it should be coming out today or tomorrow, and I would like the main codecs agent to be changed over to that model. Again, that's only gonna happen when it comes out, but it should be easy to... I should be able to just say, hey. Switch the main reviewer from codecs to that model, and it should do it.

## Decomposition (orchestrator, D-001; ACTIONABLE-NOW vs DEFERRED marked)

**Codex reviewer — ACTIONABLE NOW (bound to M0-T146, expanded):**
- Owner explicitly authorizes lifting D-004-R159's effort prohibition FOR the supervisor-set
  Codex reviewer reasoning effort ONLY ("there shouldn't be any blocker … go ahead"). B-021
  RESOLVED via this authorization. User-injected `--effort`/`--reasoning-effort` argv flags stay
  hard-denied; the Claude/Fable effort prohibition is unchanged for now.
- "Max" = the highest reasoning tier, resolved by the orchestrator to the verified ceiling
  (`xhigh`); the owner delegated exact naming ("whatever it's called").
- Reviewer effort AND model are single config values so the owner can switch with one plain
  command ("switch the main reviewer to <model>").
- Fallback ladder when Sol is unavailable/exhausted: `gpt-5.6-sol @ xhigh` → `gpt-5.6-sol @
  medium` (effort downgrade) → `gpt-5.6-luna` (low-end model); add `gpt-5.6-luna` to the codex
  allowlist (live-acceptance verified on first fallback, like xhigh).
- The owner is NOTIFIED (CLI/foreground surfacing) when `gpt-5.6-sol` is unavailable and which
  fallback engaged.
- Value validation fails closed against the codex effort enum; xhigh/luna live-acceptance is
  model-dependent and confirmable only on a live call (owner-gated).
- Frozen-supervisor feature exception (qualifying evidence: this amendment's Codex requirement
  IDs) → R247 recertification at the new identity + the ≥1165-test freeze baseline; recert +
  controller reinstall + live confirmation are owner-gated (no session-launched live review).

**Future — owner-triggered, NOT now:**
- GPT-6 Astra (`gpt-6-astra`, released 2026-09-03, gated): do NOT switch now. The easy-swap
  requirement above is what lets the owner later say "switch the main reviewer to gpt-6-astra"
  and have it done, subject to the model being in the owner's codex allowlist/available.

**DEFERRED — explicitly "you don't need to change at the moment" (recorded, NOT implemented):**
- Main Claude model policy: Fable 5 @ xhigh, fallback Opus 4.8 @ xhigh; important subagents =
  Fable 5, standard subagents = Opus 4.8. Implementing the Claude-side effort requires a separate
  explicit D-004-R159 supersession for Claude effort and its own recert; deferred per the owner.
