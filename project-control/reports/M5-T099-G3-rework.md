# M5-T099 — G3 DELTA re-review after the FAIL (code-reviewer "cr-t099", the SAME reviewer, read-only)

> Transmission history: requested by SendMessage after the orchestrator's tagged [ORCH-CORRECTED] commit 78eb0269 and the
> re-freeze (identity f46e45de); pinned at 2ce49ba7; delivered as two parts (1/2, 2/2) ending with END-OF-REPORT; no
> truncation. Joined verbatim (transport wrapper tags removed only). B1 RESOLVED: every open DB-053..DB-062 sub-item now
> maps once; no allowed_paths or batch disjointness changed. The first-round report stays at M5-T099-G3.md.

---

M5-T099 G3 DELTA re-review (code-reviewer, read-only) — part 1/2. PIN: HEAD 2ce49ba7 at start. Delta = one docs-only commit 78eb0269 (parent 2f8d0892), plan file only; producer report unchanged. Confirmed the plan at HEAD == plan at 78eb0269 (no other commit touched it). Reviewed `git diff cd04fddb 78eb0269 -- <plan>`.

1) B1 RESOLVED. The 7 previously-unmapped sub-items are now in §6, and I re-enumerated every open DB-053..DB-062 item — each maps exactly once:
- DB-053 (i) -> PKT-G Option 1 (argues necessity per dep-security policy §5 + maintainer assessment over all six provenance fields; moot under Option 2) — accurate vs backlog:182.
- DB-053 (j),(k) -> by note (j contingent: ezdxf not proposed; k moot under R12/AC1009, no OBJECTS section) — accurate.
- DB-055 (f) -> PKT-K (truncate the XObject /name echo via _preview); (j) -> by note (evidence-map wording nit) — accurate; the PKT-K "Riders closed" cell and the new mandatory PKT-K criterion both now carry (f).
- DB-061 (h) -> a derivation packet, referenced-not-created; (i) -> SAFETY, attached to PKT-D, PKT-E and PKT-F (off-event-loop cancellable job + per-request deadline + per-caller rate limit), with PKT-H verifying on every route before mount. §2, §2.1, §4 (PKT-F) and the §5 packet table all carry DB-061 (i) consistently.

DB-061 (i) on D+E+F is NOT a defective double-map: it is a per-route control each exposing route independently needs — mapping it to only one route would leave the other two uncontrolled. Same legitimate multi-enforcement-point pattern as DB-058 (a) (PKT-C source + PKT-E/I render-escape). No conflicting double-maps were introduced anywhere in §6.

Part 2/2 next (G5 edits + advisory 2 + scope + verdict).

---

M5-T099 G3 DELTA re-review — part 2/2.

2) G5-driven edits — accurate, and NO change to any packet's allowed_paths or to batch disjointness. Only the "Riders closed" and label cells changed; every file-path column is byte-unchanged, so PKT-A/C/K stay disjoint, PKT-D/E/F stay disjoint new-modules, and PKT-H stays main.py-only:
- Filename allowlist (G5 F1): server-side `<token>` = only `[A-Za-z0-9._-]` (CR/LF/quote/`;` dropped), length-capped, from validated bbl + deterministic generated_at, RFC 6266/5987 `filename*`, plus an injection test. Accurate header-injection defense; the Content-Disposition example was updated to `<token>` (which the new bullet defines). PKT-D acceptance criterion.
- PKT-K inflated-bytes cap + inflate-ratio guard (G5 F2a): accurate zlib zip-bomb defense on PDF 1.5+ object/xref streams — charged before materialization, sharing the doc-wide decoded-bytes budget, each with a reddening mutation.
- PKT-F import controls (G5 F2 b-e): accurate — raw HTTP upload ceiling BEFORE buffering (the DxfLimits clamp fires only inside read_dxf, after buffering; confirmed dxf_reader.py:461/:469), content-type + magic-byte check (ASCII DXF only; binary sentinel refused), and a no-persistence/no-RLS framing (in-memory DRAFT; any future store is its own gated packet with private bucket + tenant RLS + size cap).
- Viewer CSP (G5 F3): accurate — self-contained server GLB (one embedded binary buffer; verified the writer emits a single BIN chunk), connect-src limited to the app's own API origin, GLTFLoader configured to fetch no external resource, and wasm-unsafe-eval flagged only if Option 1's physics WASM is ever loaded (an input to the PKT-G owner decision).
- Label fixes (G5 F4): §4 import side "PKT-E" -> "PKT-F" and §2.1 mount "until PKT-F" -> "until PKT-H" correct GENUINE internal inconsistencies in the original doc (import is PKT-F, the mount is PKT-H). Grep confirms no stray "until PKT-F" / "Import side (FUTURE - PKT-E)" / "PKT-E maps closed rings" remain.

3) Advisory 2 RESOLVED: §2 now states the writer-side DB-059 (a) fix lands in PKT-B1 and the export-service cap is defense-in-depth — no ambiguous double-owner.

Scope: docs-only, exactly the plan file; producer report unchanged; no forbidden path. No new inaccuracy introduced by the delta.

M5-T099 G3 VERDICT: PASS

END-OF-REPORT
