import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { SUPPORTED_CONTRACT_VERSIONS } from "@/lib/contract";

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

  it("currently derives exactly 1.0.0 / 1.1.0 / 1.2.0 / 1.3.0 — nothing after 1.3.0 is published", () => {
    expect([...SUPPORTED_CONTRACT_VERSIONS]).toEqual([
      "1.0.0",
      "1.1.0",
      "1.2.0",
      "1.3.0",
    ]);
    expect(SUPPORTED_CONTRACT_VERSIONS).not.toContain("1.4.0");
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
