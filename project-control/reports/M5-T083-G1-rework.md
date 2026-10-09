# M5-T083 — G1 fresh self-contained re-verification vs ISO 32000-1 after the rework (data-contract-verifier "dc-pdf", read-only)

> Transmission history: requested by SendMessage after the G5 FAIL rework (5467318e, cherry-pick of
> wt-m5t083 b07a4aaa) as a FRESH, self-contained report; pinned at 10def4ef (sheet_reader.py 63a992ca,
> sheet_primitives.py a3659c55 verified); delivered as four SendMessage parts (1/4..4/4) ending with
> END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). The first G1 (PASS, advisories F1-F7) stays in M5-T083-G1.md unchanged.

---

M5-T083 G1 RE-VERIFICATION (fresh, self-contained) — architect-sheet PDF reader (sheet_reader.py + sheet_primitives.py) vs ISO 32000-1:2008 (PDF 1.7).

PIN VERIFIED: ctl24 HEAD=10def4ef106396b15f62284a7dc122d0d1186d67; blob sheet_reader.py=63a992ca, sheet_primitives.py=a3659c55 (both match). Rework 5467318e present. Primary source: Adobe PDF32000_2008.pdf, read at the cited section pages. READ-ONLY (no repo/ledger/memory writes).

PART 1/4 — (A) Operator table [operator | module:line | ISO section | verdict]

MATRIX ALGEBRA
- apply_matrix | prim:51-54 | §8.3.4 p.120 | CORRECT (x'=a·x+c·y+e, y'=b·x+d·y+f, exact).
- concat_matrix=m×ctm | prim:36-48 | §8.3.4 p.120 | CORRECT (premultiply "M′=M_T×M").

CTM / GRAPHICS STATE
- cm (CTM'=M×CTM) | reader:805-810 | Table 57 §8.4.4 p.127 | CORRECT.
- q now saves (CTM, font_size, leading) | :791-798 | Table 57 + Table 52 p.121 | CORRECT — text state (font/leading) IS graphics state, so saving them is spec-correct (see F3, part 3).
- Q restores (CTM, font_size, leading) | :799-804 | CORRECT; refuses unbalanced Q.
Note: Tm/Tlm correctly NOT saved (text-object state, §9.4.1, not graphics state).

PATH CONSTRUCTION (Table 59 §8.5.2 p.132-133) — points now stored POST-CTM (device space)
- m | _op_m :822-826, _moveto :697-705 | CORRECT; maps via CTM, refuses non-finite.
- l | _op_l :828-832, _lineto :707-717 | CORRECT.
- c | :834-839, _curveto :719-751 | CORRECT (ctrl1,ctrl2,end).
- v | :841-847 | CORRECT — ctrl1_is_current=True ⇒ p1=current device point (Fig 17 "first control coincides with initial point").
- y | :849-854 | CORRECT — ctrl2=end (Fig 17 "second control coincides with final point").
- h close | :856-860, _close :753-757 | CORRECT (current←subpath_start).
- re → m/l/l/l/h | :862-874 | CORRECT — exact Table 59 expansion; propagates non-finite refusals.

Curve start p0 = self._current (device) at :724 — a mid-path cm no longer re-derives it from stale user coords (F6, part 3). de Casteljau midpoint subdivision is exact; flattening is now budget-bounded (prim:94-129) and refuses over MAX_PATH_POINTS instead of materializing 2^24 leaves.

Continues part 2/4.

---

M5-T083 G1 RE-VERIFICATION — PART 2/4 — (A) Operator table (cont.)

PATH PAINTING (Table 60 §8.5.3 p.135)
- S s f F f* B B* b b* n | sets reader:131-134, _paint :765-778 | CORRECT. stroke/fill/close-first membership all match; s=hS, b=hB; n = paint no-op surfaced as geometry (stroked=filled=False).
- W W* clip: ignored, path retained for next paint | :146 | §8.5.4 p.137 | semantics OK; clip NOT applied — now DOCUMENTED (F1, part 3).

FORM XOBJECT — Do (§8.10.1 p.217-218, Table 95 p.218)
- form Matrix concat: form_ctm=form_matrix×CTM | _place_form :1057 | CORRECT (Do task b).
- Matrix default identity | :1045 | CORRECT (Table 95).
- Resources: own else inherit parent | :1058-1062 | CORRECT (Table 95 legacy/independent).
- text state inherited (font_size, leading) into form | :1064-1072 | §8.10.1 "initial graphics state...inherited from the state at Do" | CORRECT (F3, part 3).
- depth cap 8 + ancestor-cycle refusal | :1037-1040 | safe. Decode memoized per ref key | :1042 | CORRECT (decode once; interpretation still per placement).
- /BBox clip NOT applied | (no BBox key) | now DOCUMENTED (F1).

IMAGE XOBJECT — Do (Table 89 p.206-207, §8.3.2.4 p.116)
- matrix=CTM maps unit square→user space | _place_image :1021 | CORRECT.
- Width/Height ("in samples"), BitsPerComponent (bits/comp), ColorSpace (name; array→None) | :1022-1025 | CORRECT field meanings/units; samples NEVER decoded | CORRECT.

TEXT (§9.4; Tables 107 p.248 / 108 p.249-250 / 109 p.250-251)
- BT (Tm=Tlm=identity, no nesting) / ET | :877-891 | CORRECT.
- Td/TD (Tm=Tlm=[1 0 0 1 tx ty]×Tlm; TD also TL=-ty) | :908-918 | CORRECT.
- Tm (REPLACE, not concat) | :919-925 | CORRECT.
- T* (=0 -Tl Td) | :926-931 | CORRECT.
- Tj / ' (=T* Tj) / " (=aw Tw ac Tc string ') / TJ | _show :934-971 | anchor=apply(Tm×CTM,0,0), non-finite-guarded | CORRECT (§9.4.1/9.4.2). aw/ac/TJ-numbers consumed & ignored (advance) — documented (F2).
- Tf (sets size; refuses show-before-Tf) | :892-897,961 | CORRECT.
- TL leading | :898-903 | CORRECT.

PAGE / UNITS
- UserUnit: positive, default 1.0, leaf-only (non-inheritable), recorded not applied | :435-443 | Table 30 p.79 | CORRECT.
- MediaBox / Resources inheritance | :399-400 | Table 30 | CORRECT (MediaBox still recorded un-normalized — see F7).
- Contents single-or-array (newline join) | _decode_contents :265-290 | Table 30 | CORRECT.

Every operator the profile implements is spec-correct in semantics, order, and units. Continues part 3/4.

---

M5-T083 G1 RE-VERIFICATION — PART 3/4

(B) REWORKED BEHAVIORS — now spec-correct?

F3 (text state on q/Q + form inheritance) — SPEC-CORRECT. q saves (CTM,font_size,leading); Q restores (reader:796,802). Per Table 52 p.121 text state IS graphics state; the profile models the two params that affect its output (font_size reported, leading drives T*/'/") and now saves/restores exactly those. Forms inherit font_size/leading via interpret kwargs (:1070-1071) per §8.10.1 "initial graphics state inherited from the state at Do." Changes inside a form don't leak to the parent (child holds its own copy = the implicit q/Q around Do). Tm/Tlm correctly NOT inherited (reset by BT). ✓

F5 (h/re/close then a segment op) — SPEC-CORRECT. _open_after_close (:690-695) starts a new subpath at the current point when l/c/v/y find cur_points=None but current≠None (:713-714, :734-735). Matches Table 59 h: "Appending another segment...shall begin a new subpath, even if it begins at the endpoint reached by h." After a PAINT (current=None) a bare segment op is still refused — also correct (§8.5.2.1: after painting the current point is undefined ⇒ error). ✓

F6 (mid-path cm corrupting a curve start) — SPEC-CORRECT. Current point & subpath start are stored POST-CTM (device) in _moveto/_lineto/_curveto/_close; _curveto uses p0=self._current directly (:724), never re-mapping stale user coords; v uses p1=p0 (:847). Traced `10 10 m / 2 0 0 2 0 0 cm / 20 20 l` ⇒ line (10,10)→(40,40) device (each point under the CTM in force at its operands) — correct; the old wrong re-derivation is gone. ✓

(C) NEW DOCSTRINGS — accurate?

- cubic_flat (prim:72-86): claims a PERPENDICULAR/cross-track bound only, both-control-points (`and`) necessary, midpoint subdivision exact, NOT a distance-to-segment bound under along-chord overshoot. VERIFIED accurate: projecting E(t)=b1·d1+b2·d2 onto the chord normal, the control points' along-chord offsets cancel, so |E·n|≤(3/4)·max(h1,h2)≤tol when both ≤tol; `or` would leave the far control point unbounded. ACCURATE.
- SheetTextRun (prim:150-162): anchors exact only for the first show after a positioning op (Td/TD/Tm/T*/'/"); later same-line Tj/TJ un-advanced. ACCURATE (matches the no-advance model; '/" reset the line origin before showing, so their own show is exact).
- Module + _place_form docstrings (reader:28-31,1033-1036): W/W* and form /BBox NOT applied (over-inclusion by design). ACCURATE.
- Interpreter/doctrine docstrings (:33-39,468-473): per-document byte/op/point budgets, per-page output reset, top-level backstop. ACCURATE.

Continues part 4/4 (findings + verdict).

---

M5-T083 G1 RE-VERIFICATION — PART 4/4 — Findings + verdict

RESOLVED since first G1 (all confirmed at this pin):
- F3/F5/F6 → fixed and spec-correct (part 3).
- F1 (clip/BBox) & F2 (text advance) & F4 (Bézier bound) → design choices now DOCUMENTED accurately; no behavior owed.
- Bonus fix: per-page primitive isolation. The original reused one interpreter across pages WITHOUT resetting output lists, so page N leaked into page N+1. The depth-0 reset (reader:532-535) fixes this; multi-page reads are now correct. (Not in my earlier F-list; noting it as verified-correct now.)

RESIDUAL / NEW (all ADVISORY; none blocking):
G1-R1 (ADVISORY) Budgets are DOCUMENT-wide, not per-page: point_count (500k), op_count (200k), decoded_bytes (128MB) accumulate across all pages and Form recursion (reader:481-495). Defensible DoS design and documented, but a very large legitimate multi-page sheet set could refuse on the SUM. Generous for architect sheets; flag only so downstream knows the bound is per-document.
G1-R2 (ADVISORY, informational) Inline images (BI/ID/EI) still hit the unsupported-operator refusal (whole-doc) — safe (scan stops before binary data); /Rotate not applied and MediaBox recorded un-normalized — both consistent with the documented "page default user space, later stage" contract. Unchanged from first G1 (was F7).
G1-R3 (trivial doc nit, non-blocking) apply_matrix/Matrix cite "§8.3.3"; the row-vector multiply equation is actually §8.3.4 p.120 (§8.3.3 is the common-transform array forms). Markers are "[recalled - verify]"; semantics are correct.

Hardening verified safe (no semantic change): top-level exception→refusal backstop (type name only), non-finite coordinate guards (_map/_map_via/flatten output), per-ref Form decode memoization (charges bytes once for work done once), attacker-token preview truncation. Budget-threaded flattening traced: a single curve cannot exceed the page's remaining point budget before refusing.

Basis: every implemented operator matches ISO 32000-1 in semantics/order/units; the three reworked behaviors (F3/F5/F6) are now spec-correct; the new docstrings are accurate; the multi-page bug is fixed; remaining deviations are documented simplifications or conservative refusals that never silently emit wrong geometry. (Harness/CI evidence — ruff, pytest, modularity — is CI's job at this head; not run locally per thin-client rules.)

M5-T083 G1 VERDICT: PASS
END-OF-REPORT
