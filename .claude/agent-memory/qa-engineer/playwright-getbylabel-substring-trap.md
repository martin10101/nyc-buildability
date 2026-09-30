---
name: playwright-getbylabel-substring-trap
description: Playwright getByLabel matches case-insensitive SUBSTRING by default — pass {exact:true} AND scope to the form container to avoid strict-mode ambiguity in the address flow
metadata:
  type: feedback
---

Playwright `page.getByLabel("Borough")` matches a case-insensitive **substring** of the
accessible name by default, so it collides with any other label containing that text. In the
address flow (`apps/web/src/components/address/AddressForm.tsx`) this bit twice on M5-T023:
1. an OUTER provenance label "Borough (source code)" (from `format.ts`) — fixed by scoping to
   `page.getByTestId("address-form").getByLabel(...)`.
2. an IN-FORM label "ZIP code (alternative to borough)" (AddressForm.tsx:131) — form-scoping did
   NOT fix this; only adding `{ exact: true }` to each `getByLabel` pinned the unique labels.

**Why:** two CI e2e failures (runs 34735243173 unscoped, 34735830129 form-scoped) both traced to
this before `{ exact: true }` closed it at 3ff94619. Testing-Library's `getByLabelText` (vitest)
is exact-by-default, so this trap is Playwright-only.

**How to apply:** for any Playwright form locator, prefer `getByTestId`; when you must use
`getByLabel`, scope to the form container AND pass `{ exact: true }`, and confirm the exact label
text is unique inside that scope. The current AddressForm exact labels: "House number", "Street",
"Borough", "ZIP code (alternative to borough)".
