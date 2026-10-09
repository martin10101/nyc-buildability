import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { SUPPORTED_CONTRACT_VERSIONS } from "@/lib/contract";
import { validateRuleEvaluationDocument } from "@/lib/rule-evaluation-contract";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import {
  condoUnresolvedDoc,
  draftApplicableDoc,
  substitutionStampDoc,
} from "@/test-support/rule-evaluation-fixtures";

/**
 * Task M2-T010 (CT-S1/CT-S2): the client's runtime supported-contract-version
 * list is a GENERATED block derived from the canonical schema enum by
 * packages/contracts/scripts/generate_ts_types.py. This suite is the in-web
 * half of the drift protection (the contracts-typegen CI job byte-checks the
 * generated block itself):
 *
 *  - positive lock: the runtime list equals the canonical schema enum
 *    EXACTLY (same members, same order) — so a schema-published version
 *    missing from the client list turns `npm test` red in the web and
 *    web-e2e CI jobs too, independently of the typegen job;
 *  - negative regression: the exact detector used by the positive lock is
 *    proven to flag a simulated schema-ahead fixture loudly (the CI-red
 *    path is exercised, not assumed).
 *
 * The schema is read via node:fs at TEST time only — nothing outside
 * apps/web enters the Next.js bundle (type-only import discipline intact).
 *
 * Resolution note: the vitest environment is jsdom, where `import.meta.url`
 * is NOT a `file:` URL, so `fileURLToPath()` throws ERR_INVALID_URL_SCHEME.
 * CI runs vitest with working-directory `apps/web` (.github/workflows/ci.yml),
 * so the canonical schema is resolved from `process.cwd()` (= apps/web)
 * two levels up into the monorepo `packages/` tree.
 */

const SCHEMA_PATH = path.resolve(
  process.cwd(),
  "../../packages/contracts/schemas/v1/property_profile.schema.json",
);

function canonicalSchemaEnum(): string[] {
  const schema = JSON.parse(readFileSync(SCHEMA_PATH, "utf-8")) as {
    properties: {
      profile_version: {
        properties: { contract_version: { enum: string[] } };
      };
    };
  };
  return schema.properties.profile_version.properties.contract_version.enum;
}

/** Schema-published versions the client runtime list omits (must be none). */
function omittedVersions(
  published: readonly string[],
  client: readonly string[],
): string[] {
  return published.filter((version) => !client.includes(version));
}

describe("SUPPORTED_CONTRACT_VERSIONS derivation (single canonical source)", () => {
  it("equals the canonical schema contract_version enum exactly (members and order)", () => {
    expect([...SUPPORTED_CONTRACT_VERSIONS]).toEqual(canonicalSchemaEnum());
  });

  it("omits NO schema-published version (silent-omission drift is impossible)", () => {
    expect(omittedVersions(canonicalSchemaEnum(), SUPPORTED_CONTRACT_VERSIONS)).toEqual(
      [],
    );
  });

  it("currently derives exactly 1.0.0 / 1.1.0 / 1.2.0 / 1.3.0 / 1.4.0 — nothing after 1.4.0 is published", () => {
    expect([...SUPPORTED_CONTRACT_VERSIONS]).toEqual([
      "1.0.0",
      "1.1.0",
      "1.2.0",
      "1.3.0",
      "1.4.0",
    ]);
    expect(SUPPORTED_CONTRACT_VERSIONS).not.toContain("1.5.0");
  });
});

describe("drift regression — schema-ahead fixture fails loudly (CT-S2)", () => {
  it("detects a simulated schema-published version missing from the client list", () => {
    // Fixture: the schema publishes 9.9.9 but the client list does not carry
    // it. The SAME detector the positive lock uses must flag it — this is
    // the red path the positive assertions rely on.
    const schemaAheadFixture = [...canonicalSchemaEnum(), "9.9.9"];
    expect(omittedVersions(schemaAheadFixture, SUPPORTED_CONTRACT_VERSIONS)).toEqual([
      "9.9.9",
    ]);
    // And the exact-equality lock would fail on the same fixture:
    expect([...SUPPORTED_CONTRACT_VERSIONS]).not.toEqual(schemaAheadFixture);
  });

  it("also detects reverse drift (client version the schema never published)", () => {
    const clientAheadFixture = [...SUPPORTED_CONTRACT_VERSIONS, "9.9.9"];
    expect(clientAheadFixture).not.toEqual(canonicalSchemaEnum());
    expect(omittedVersions(clientAheadFixture, canonicalSchemaEnum())).toEqual([
      "9.9.9",
    ]);
  });
});

describe("rule_evaluation contract-version admission (M5-T037: 1.0.0 + additive 1.1.0)", () => {
  const block = {
    determination_state: "within_100ft_of_wide_street",
    far_row: "wide_street_row",
    governing_max_residential_far: 3.44,
    coverage_hint: "conditional",
    exceptions_checked: true,
    named_street_override_pending: false,
    policy_decision_states: ["wide"],
    original_labels: ["80"],
    source_versions: ["2026-03-26"],
    matched_geometry_refs: ["OBJECTID=12345"],
    interpreted_bounds_summaries: ["mapped width 80 ft (>= 75 ft, wide)"],
    classification_reasons: ["DCM effective_disposition=wide; ambiguity_class=none"],
    draft_label: "DRAFT — not a verified legal determination",
    fallback_direction_note: "On uncertainty the higher wide-street FAR is withheld.",
    reason: "Wide-street row governs; DRAFT pending G6.",
  } satisfies NonNullable<RuleEvaluation["wide_street"]>;

  it("keeps a 1.0.0 document valid (no block) — the recorded web-e2e fixtures stay green", () => {
    const doc = draftApplicableDoc();
    expect(doc.contract_version).toBe("1.0.0");
    expect(validateRuleEvaluationDocument(doc).ok).toBe(true);
  });

  it("accepts a 1.1.0 document carrying the optional wide_street block", () => {
    const doc = draftApplicableDoc();
    doc.contract_version = "1.1.0";
    doc.wide_street = structuredClone(block);
    const result = validateRuleEvaluationDocument(doc);
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.document.wide_street?.governing_max_residential_far).toBe(3.44);
    }
  });

  it("accepts a 1.1.0 document with NO block (the serializer emits 1.1.0 for every body)", () => {
    const doc = draftApplicableDoc();
    doc.contract_version = "1.1.0";
    expect(validateRuleEvaluationDocument(doc).ok).toBe(true);
  });

  it("rejects a contract_version outside the published enum", () => {
    const doc = draftApplicableDoc();
    (doc as unknown as Record<string, unknown>).contract_version = "2.0.0";
    expect(validateRuleEvaluationDocument(doc).ok).toBe(false);
  });

  it("enforces the wide_street block shape when present (malformed block fails total validation)", () => {
    const doc = draftApplicableDoc();
    doc.contract_version = "1.1.0";
    const bad = structuredClone(block) as unknown as Record<string, unknown>;
    bad.determination_state = "definitely_wide"; // not in the enum
    bad.governing_max_residential_far = "3.44"; // string, not number | null
    (doc as unknown as Record<string, unknown>).wide_street = bad;
    const result = validateRuleEvaluationDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some((p) => p.startsWith("wide_street.determination_state"))).toBe(true);
      expect(
        result.problems.some((p) => p.startsWith("wide_street.governing_max_residential_far")),
      ).toBe(true);
    }
  });
});

describe("rule_evaluation contract-version admission (M5-T058: additive 1.2.0 substrate_substitution)", () => {
  const substitution = {
    entered_bbl: "3022647515",
    analyzed_bbl: "3022640032",
    note:
      "This analysis runs on the recorded base tax lot for the entered condominium " +
      "billing lot; the entered billing lot and the analyzed base lot are recorded as " +
      "entered versus analyzed, a record and not a computed allowance.",
    condo_key: "301313",
    resolution_path: "dof_dtm_condo",
    source_id: "nyc-dof-dtm-condo",
    dataset_ids: ["dtm-condo-2026-07"],
    retrieved_at: "2026-09-06T00:00:00Z",
    mixed_substrate: {
      lot_facts_substrate: "analyzed_base_lot",
      identity_facts_substrate: "entered_billing_lot",
      note:
        "The lot area and geometry describe the analyzed base lot; the PLUTO identity " +
        "facts describe the entered billing lot.",
    },
  } satisfies NonNullable<RuleEvaluation["substrate_substitution"]>;

  it("accepts a 1.2.0 document carrying the optional substrate_substitution block", () => {
    const doc = substitutionStampDoc();
    expect(doc.contract_version).toBe("1.2.0");
    const result = validateRuleEvaluationDocument(doc);
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.document.substrate_substitution?.entered_bbl).toBe("3022647515");
      expect(result.document.substrate_substitution?.analyzed_bbl).toBe("3022640032");
      expect(result.document.substrate_substitution?.mixed_substrate.lot_facts_substrate).toBe(
        "analyzed_base_lot",
      );
    }
  });

  it("accepts a 1.2.0 document with NO block (the block is optional; the serializer omits it off-path)", () => {
    const doc = draftApplicableDoc();
    doc.contract_version = "1.2.0";
    expect(doc.substrate_substitution).toBeUndefined();
    expect(validateRuleEvaluationDocument(doc).ok).toBe(true);
  });

  it("keeps a 1.0.0 document valid with no substrate_substitution block (old documents stay valid)", () => {
    const doc = draftApplicableDoc();
    expect(doc.contract_version).toBe("1.0.0");
    expect(doc.substrate_substitution).toBeUndefined();
    expect(validateRuleEvaluationDocument(doc).ok).toBe(true);
  });

  it("admits the new condo_base_lot_unresolved fail-safe reason", () => {
    const doc = condoUnresolvedDoc();
    expect(doc.fail_safe_reason).toBe("condo_base_lot_unresolved");
    expect(validateRuleEvaluationDocument(doc).ok).toBe(true);
  });

  it("rejects a fail_safe_reason outside the documented enum", () => {
    const doc = condoUnresolvedDoc();
    (doc as unknown as Record<string, unknown>).fail_safe_reason = "condo_substrate_missing";
    const result = validateRuleEvaluationDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some((p) => p.startsWith("fail_safe_reason"))).toBe(true);
    }
  });

  it("enforces the substrate_substitution block shape when present (malformed block fails total validation)", () => {
    const doc = substitutionStampDoc();
    const bad = structuredClone(substitution) as unknown as Record<string, unknown>;
    bad.entered_bbl = 3022647515; // number, not a non-empty string
    (bad.mixed_substrate as Record<string, unknown>).lot_facts_substrate = ""; // empty string
    (doc as unknown as Record<string, unknown>).substrate_substitution = bad;
    const result = validateRuleEvaluationDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some((p) => p.startsWith("substrate_substitution.entered_bbl"))).toBe(
        true,
      );
      expect(
        result.problems.some((p) =>
          p.startsWith("substrate_substitution.mixed_substrate.lot_facts_substrate"),
        ),
      ).toBe(true);
    }
  });

  it("does not reject a document only because it carries an extra top-level key beside the stamp (positive-shape)", () => {
    const doc = substitutionStampDoc();
    (doc as unknown as Record<string, unknown>).server_only_future_field = "ignored-by-the-client";
    expect(validateRuleEvaluationDocument(doc).ok).toBe(true);
  });
});

describe("DB-025(e) — positive-shape validator: unknown keys are not rejected", () => {
  // Backs the corrected module wording: the client checks DOCUMENTED keys
  // positively and does NOT enforce additionalProperties — the server owns the
  // closed schema. An unknown/extra top-level key must NOT fail total validation
  // (a forward-compatible server field the client does not yet model still
  // renders), and every recorded fixture stays valid.
  it("accepts an otherwise-valid document carrying an unknown/extra top-level key", () => {
    const doc = draftApplicableDoc();
    expect(validateRuleEvaluationDocument(doc).ok).toBe(true); // baseline stays valid
    (doc as unknown as Record<string, unknown>).server_only_future_field =
      "ignored-by-the-client";
    expect(validateRuleEvaluationDocument(doc).ok).toBe(true);
  });
});
