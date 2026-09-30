---
name: wide-street-display-gating-test-adequacy
description: How to judge test adequacy for the wide-street DB-025 determination_state display gating (CalculationEvidence/DevelopmentLimits/ReportView) — the queries that are and aren't vacuous
metadata:
  type: feedback
---

When reviewing the wide-street display-gating tests (DB-025 a-c; components
CalculationEvidence.tsx / DevelopmentLimits.tsx / ReportView.tsx):

- **The not-within-vs-within label test is the one that TRULY forces
  determination_state gating.** Both `within_100ft_of_wide_street` and
  `not_within_100ft_of_wide_street` carry a NON-null `governing_max_residential_far`,
  so a legacy null-FAR heuristic cannot distinguish them — only
  `determination_state` can. A test asserting not-within shows "Governing
  floor-area ratio" (never "Wide-street conditional FAR") is therefore a genuine
  determination_state proof. The within-vs-review pair alone does NOT distinguish
  determination_state gating from a null-FAR heuristic (they agree via the server
  invariant review⟺null-FAR⟺far_row=none).

- **Scope status-label assertions to the section testid.** CalculationEvidence has
  an ALWAYS-ON panel banner `Draft · Professional review required` (top of the
  component). A `.not.toHaveTextContent("Professional review required")` on the
  whole render would be vacuous. The correct DB-025(a) test scopes to
  `getByTestId("wide-street-provenance")` before the negative assertion.

- **`{hidden:true}` heading queries in ReportView are non-vacuous and regression-
  safe.** ReportView nests CalculationEvidence in a CLOSED `<details id="brief-
  calculations">`, so the provenance `<h3>` is outside the a11y tree. The tests
  use `within(provenance).getByRole("heading", { name: "...", hidden: true })`
  (positive) PAIRED with `queryByRole(..., wrong-name, hidden:true)).toBeNull()`
  (negative). If the heading text regresses, the positive getByRole THROWS and the
  negative queryByRole finds-instead-of-null — both fail. CI green proves the
  positive query actually matched a real element (not silently passing).

**Why:** M5-T040 G4 review. These three patterns separate the adequate tests from
the vacuous ones for this feature; the null-FAR-vs-determination_state distinction
is the crux of the DB-025 correction (two surfaces previously gated differently,
agreeing only via a server invariant).

**How to apply:** On any future wide-street/FAR display-gating review, confirm (1)
a not-within case with non-null FAR asserts the conservative label, (2) section-
scoped negative label assertions, (3) paired positive+negative heading queries for
closed-`<details>` content. See [[m5t040-named-street-wiring-gate]].
