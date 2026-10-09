# M5-T099 — G5 DELTA re-attestation (security-reviewer "sec-t099", the SAME reviewer, read-only)

> Transmission history: requested by SendMessage after the orchestrator's tagged [ORCH-CORRECTED] commit 78eb0269 and the
> re-freeze (identity f46e45de); pinned at 2ce49ba7; delivered as three parts (1/3..3/3) ending with END-OF-REPORT; no
> truncation. Joined verbatim (transport wrapper tags removed only). F1 and F2(a) are now MANDATORY tested acceptance
> criteria for PKT-D / PKT-K; F2(b)-(e), F3, F4 carried. The first-round report stays at M5-T099-G5.md.

---

G5 DELTA RE-ATTESTATION — M5-T099 — Part 1/3. Read-only. HEAD pinned 2ce49ba7. Confirmed: ONE docs-only commit 78eb0269 (parent 2f8d0892) touches only docs/design/d087-export-and-3d-viewer-plan.md; producer report unchanged. Reviewed via git diff cd04fddb 78eb0269.

F1 (Content-Disposition filename injection) — ADEQUATE, carried. §2 drops the caller-interpolated filename for filename="site-plan-<token>.dxf" and adds a MANDATORY PKT-D criterion: <token> is built server-side from an allowlist ([A-Za-z0-9._-] only; CR/LF, quote, `;` and everything else dropped), length-capped, derived from the validated bbl + deterministic generated_at; raw caller text NEVER reaches a header value; RFC 6266/5987 filename*=UTF-8''… for non-ASCII; and a test proves `"`, `;`, CR/LF or non-ASCII cannot break/split/spoof the header. The PKT-D row now carries "the §2 filename-safety criterion (mandatory, G5 F1)". Meets every remediation point I named; `/` and `\` are not in the allowlist, so no path-separator vector.

F2(a) (PDF decompression bomb, PKT-K) — ADEQUATE, carried. §5 adds a MANDATORY PKT-K criterion: an ABSOLUTE inflated-bytes cap AND an inflate-ratio guard on every object/xref stream, charged BEFORE the inflated bytes are materialized, sharing the document-wide decoded-bytes budget, each with a reddening mutation; plus truncation of the XObject /name echo in refusal details via _preview (DB-055 (f)). PKT-K's rider row adds (f). Complete.

(continues Part 2/3)

---

G5 DELTA — M5-T099 — Part 2/3.

F2(b)-(e) (import parse-time controls, PKT-F) — ADEQUATE, carried. §4 adds PKT-F acceptance criteria: (b) a raw HTTP upload ceiling via the T053 bounded-streaming primitives BEFORE the body is materialized; (c) off-event-loop cancellable parse under a per-request wall-clock deadline + route rate limit (DB-061 (i)); (d) a content-type + magic-byte check (ASCII DXF only, binary-DXF sentinel refused); (e) persists NOTHING (in-memory proposal draft; no storage/RLS surface; any future persistence = its own gated packet with a private bucket + tenant RLS + size cap). PKT-F's rider row is updated accordingly.

F3 (viewer CSP + external resources) — ADEQUATE, carried. §3 adds PKT-I CSP (script-src, worker-src, and connect-src limited to the app's own API origin), self-contained server GLBs (one embedded binary buffer; no external buffer/texture URIs), and GLTFLoader barred from fetching external resources. Both §3 and the §3.1 Option-1 CON now connect the rapier3d WASM to a wasm-unsafe-eval CSP relaxation, feeding the PKT-G owner decision.

F4 (packet labels) — ADEQUATE, carried, and more: §4 import label fixed PKT-E→PKT-F; and §2.1 "No live exposure" was ALSO wrong ("until PKT-F") and is now fixed to "until PKT-H (the mount packet)". Both mislabels corrected.

(continues Part 3/3)

---

G5 DELTA — M5-T099 — Part 3/3.

OTHER TAGGED (G3) EDITS — no new security concern; all security-neutral or POSITIVE:
- Export §2 and scene §2.1 now require an off-loop cancellable job, a per-request deadline, and a per-caller RATE LIMIT (DB-061 (i)); PKT-H verifies DB-061 (i) on every route before mounting. Strengthens DoS / resource-exhaustion defense across all three routes.
- Rider-map additions are honest and correctly routed: DB-053 (i) → PKT-G Option-1 necessity + provenance argument (a dep-security G5 item); DB-053 (j),(k) → ezdxf is NOT proposed (any future add = full G5 admission), and the R12/AC1009 target has no OBJECTS section (supply-chain-minimal); DB-055 (f) → name-echo truncation in PKT-K; DB-061 (h) → bounded-today derivation item referenced, not created here.

Nothing I previously verified was relaxed: the unmounted max-envelope route and its preconditions (§7), the flag-gating / write-import double-flag, and the generic-404 sentinel are untouched by this diff.

Optional NON-BLOCKING nit (for the PKT-D test, not a gate item): also cover the degenerate case where sanitization yields an empty or `.`/`-`-only token — fall back to a server default (e.g. the correlation id) so no filename="site-plan-.dxf" can slip through.

RULING: all BLOCKING items (F1, F2(a)) are now mandatory, tested acceptance criteria; all advisory items (F2(b)-(e), F3, F4) are carried; the corrections only strengthen the security posture and relax nothing.

M5-T099 G5 VERDICT: PASS

END-OF-REPORT
