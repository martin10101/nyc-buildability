# M5-T066 — G5 Security review record (security-reviewer return, VERBATIM)

[Orchestrator record header — not part of the reviewer return: fresh security-reviewer
dispatched 2026-09-21 ~06:14 UTC at frozen 84132df56047bae7097b4172575ef75099f8a43e per the
seq-124 handoff (the pre-handoff wave never dispatched SEC). Return received COMPLETE in one
part with the required END-OF-REPORT marker present; transport entity-decoding only. Verdict
PASS; two advisories (A1 pre-existing NaN forward on the keyboard path — same family as the
HJ-2 advisory; A2 style note), zero blocking findings.]

---

Review complete. All eight review-surface items verified at the frozen head. Returning the gate report.

---

**VERDICT: PASS**

**G5 Security/Privacy Gate — M5-T066 (map-CLICK interaction slice)**

Reviewed at frozen head `84132df56047bae7097b4172575ef75099f8a43e` (submit seam over material `abfd182b`). Source blobs are byte-identical (LF-normalized) between material and frozen head for all 6 changed source files; the frozen span adds only ledger/state files on top of material (no source delta). CI SUCCESS recorded at `2578329c`.

**Identity / scope (verified)**
- Frozen head is the submit-seam child of material `abfd182b` (parent `2fbaaf53`). Confirmed via git plumbing.
- Forbidden paths untouched in material and across the frozen span: `AddressConfirmCard.tsx`, `PropertyOverview.tsx`, `outline-bridge-api.ts`, `e2e/helpers.ts`, `services/api/`, `packages/contracts/` — none appear in the diff.
- No dependency manifest changed: no `package.json` / lockfile / `.npmrc` in the material or frozen span. New imports are all internal (`react`, `@/components/address/LotOutlineMap`, `./ProposalOutlineMap`, `@/lib/architect/proposal-draft`) — zero new packages (item 2).

**Blocking findings: NONE.**

**Per-surface results**
1. Pointer input → state (`ProposalOutlineDraw.tsx:103-104,114-118`; `ProposalOutlineMap.tsx:86-89`; `LotOutlineMap.tsx:491-522`): clicked `lngLat.lng/lat` are numeric coordinates written straight into `points` state; no string parsing, no injection vector. Real MapLibre `lngLat` is always finite, and the overlay builder (`ProposalOutlineMap.tsx:44-46`) filters non-finite via `Number.isFinite` before rendering. Selection index comes from feature `properties.index` guarded by `typeof … === "number"` (`LotOutlineMap.tsx:514`) and is only used for array indexing — no out-of-bounds write. Early-click hit-test is guarded by `getLayer` (`LotOutlineMap.tsx:509`) so it cannot trigger the `failRender` teardown path. No typing/bounds gap introduced.
2. Zero new deps — confirmed (see scope).
3. No client-side CRS math — grep-provable clean; every `2263`/`4326`/`EPSG` occurrence in the packet is a comment/doc or the pre-existing numeric-authority serialization (`proposal-draft.ts:209`), not a transform. Clicked positions stay display-4326 until the server bridge (AS-5).
4. e2e bridge stubs (`e2e/proposal-editor.spec.ts`): all `/api/v1/outline-bridge` and `/api/v1/proposal-checks` traffic is fully intercepted via `page.route`; no real network egress, no credentials/secrets, no API keys. Only canned correlation-id strings (`e2e-corr`/`e2e-bridge`/`e2e-drawn`) and fake BBLs in fixtures.
5. Forbidden paths untouched — confirmed (see scope).
6. XSS/DOM injection: no `dangerouslySetInnerHTML` in any changed file. All new copy/labels/warnings interpolate numbers (`selectedIndex`, `points.length`, `MIN_DRAWN_VERTICES - drawnCount`) or internally-generated wall IDs (`danglingWallIds().join(", ")`, `ProposalEditor.tsx:123-127`) as React text nodes — auto-escaped. The one `innerHTML` reference (`LotOutlineMap.tsx:220` comment / `:729` attribution) is pre-existing and untouched by this diff.
7. Additive-optional prop: interaction is gated purely by `interactive = onOutlineMapClick != null` (`LotOutlineMap.tsx`); absent → no click listener attaches and the overlay effect returns early (no source/layers). Both display-only consumers pass no interaction props — `AddressConfirmCard.tsx:305`, `PropertyOverview.tsx:382` — so the accepted display surface is byte-equivalent (AS-3). `interactive` is stable per consumer, so its addition to the effect deps causes no churn.
8. Logging: no `console.*` added anywhere; no coordinate/user-data spray.

**Standard G5 checklist:** cross-tenant isolation, service-role secrecy, private storage, SSRF, upload controls, prompt-injection, log redaction — all N/A to this slice (pure client-side UI; `bbl` passed through unchanged; the only outbound calls are the pre-existing forbidden/untouched relative `/api/v1/*` routes with fixed paths — no user-controlled URL, no server fetch, no secrets, no storage, no AI path). Least privilege upheld: the interaction capability is opt-in and the display path is unchanged when absent.

**Advisory (non-blocking, out of this slice's scope)**
- A1. `convert` still forwards keyboard-added-but-untyped rows (`{lng: NaN, lat: NaN}`) into `drawn_vertices` (`ProposalOutlineDraw.tsx:151`). This is pre-existing and unchanged by this diff; `JSON.stringify` emits `null` and the server bridge validates. The new map-click path only ever writes finite values, so it introduces no NaN. No action required here; track as bridge-request robustness if desired.
- A2. `interactionRef.current` is reassigned in the component render body (`LotOutlineMap.tsx`), an idiomatic latest-callback ref pattern; noted for style only, no security impact.

END-OF-REPORT M5-T066-SEC
