---
name: field-label-review-technique
description: How to G3-verify FIELD_LABELS provenance (M2-T002 S5/D1) and the one defect class that survives programmatic checks
metadata:
  type: project
---

FIELD_LABELS in `apps/web/src/lib/format.ts` is verifiable programmatically: extract keys by regex and diff against the official 108-column inventory in `services/api/tests/fixtures/pluto/F08_api_views_columns_snapshot.json` (JSON at `response_body_raw` → `columns[].fieldName`). M2-T002 result: exact bijection, 108/108.

**Why:** the inventory check catches missing/extra keys but NOT semantic drift. The defect class that survives it is a label that ADDS a semantic word beyond the official field name (found: `zmcode` → "Zoning map change code"; official ZMCode is a zoning-map border indicator, "change" is invented and untraceable to `docs/research/pluto-mappluto-2026-07-16.md`). Producer-disclosed non-verbatim expansions (facilfar/appbbl/edesignum/DCAS/MAS/RPAD) were all defensible; the undisclosed one was the defect.

**How to apply:** in label reviews, run the bijection check first, then hand-audit every label whose wording contains words absent from the camel-case field name; demand a committed-research citation for each added word. Also note: `api.test.ts` contains a raw NUL byte (control-char laundering test) so git flags it binary — expected, not corruption.
