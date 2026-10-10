import { describe, expect, it } from "vitest";
import {
  NO_SCOPE_REASON,
  identitiesMatch,
  resultIdentity,
} from "@/lib/architect/result-identity";
import type { Results } from "@/lib/architect/three-answers";
import { loadResultsFixture } from "@/test-support/results-fixtures";

/**
 * M5-T148 part B scenario S8: the result identity carries the lot, the results id and a short
 * revision fingerprint; another lot is a mismatch; a document without a scope gives an unknown
 * identity, never a guessed one. Every value is read from the document.
 */

const BENCHMARK = "recorded_215_16_northern_journey";
const NO_SCOPE = "synthetic_all_answers_available";

function withLot(doc: Results, bbl: string, display: string): Results {
  if (!doc.scope) throw new Error("fixture changed: benchmark should carry a scope");
  return { ...doc, scope: { ...doc.scope, lot: { ...doc.scope.lot, bbl, display } } };
}

describe("resultIdentity / identitiesMatch (scenario S8)", () => {
  it("carries the lot, the results id and a fingerprint, all read from the document", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const identity = resultIdentity(doc);
    expect(identity.kind).toBe("known");
    if (identity.kind !== "known") throw new Error("known expected");
    expect(identity.lotBbl).toBe(doc.scope?.lot.bbl);
    expect(identity.lotDisplay).toBe(doc.scope?.lot.display);
    expect(identity.resultsId).toBe(doc.results_id);
    expect(identity.revisionFingerprint).toMatch(/^[0-9a-f]{8}$/);
    // Deterministic: the same document yields the same fingerprint every time.
    const again = resultIdentity(doc);
    if (again.kind !== "known") throw new Error("known expected");
    expect(again.revisionFingerprint).toBe(identity.revisionFingerprint);
  });

  it("matches a document against itself, but another lot is a mismatch", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const self = resultIdentity(doc);
    expect(identitiesMatch(self, resultIdentity(doc))).toBe(true);
    const otherLot = resultIdentity(withLot(doc, "4000010001", "Manhattan block 1, lot 1"));
    expect(otherLot.kind).toBe("known");
    expect(identitiesMatch(self, otherLot)).toBe(false);
  });

  it("treats a different revision of the same lot as a mismatch (stale export caught)", () => {
    const doc = loadResultsFixture(BENCHMARK);
    const current = resultIdentity(doc);
    const bumped = resultIdentity({ ...doc, revision: doc.revision + 1 });
    expect(bumped.kind).toBe("known");
    if (current.kind !== "known" || bumped.kind !== "known") throw new Error("known expected");
    expect(bumped.revisionFingerprint).not.toBe(current.revisionFingerprint);
    expect(identitiesMatch(current, bumped)).toBe(false);
  });

  it("gives an unknown identity when the document carries no scope, never a guessed lot", () => {
    const doc = loadResultsFixture(NO_SCOPE);
    expect(doc.scope ?? null).toBeNull();
    const identity = resultIdentity(doc);
    expect(identity).toEqual({ kind: "unknown", reason: NO_SCOPE_REASON });
    // An unknown identity never matches anything, including another unknown document.
    expect(identitiesMatch(identity, resultIdentity(doc))).toBe(false);
  });
});
