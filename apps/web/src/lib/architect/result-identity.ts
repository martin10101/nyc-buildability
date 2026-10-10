// Presentation adapter: the identity of one result document — the lot, the results id and a short
// revision fingerprint (M5-T148 part B; presentation contract §8 "Screen and export must use the
// same revision; prevent stale export when property/scenario inputs change"; acceptance UX-05).
// Pure. It decides no law and recalculates nothing (ruling V2): the lot is READ from the document's
// scope, never guessed. A document without a scope gives an unknown identity, never an invented lot.
//
// The fingerprint is a deterministic digest of the document's own identity fields (results id,
// study id, option id, revision, computed-at). It is a label for "which revision is this", not a
// zoning value: two outputs built from the same document share it, and any change to those fields
// changes it, so a screen and an export built from different revisions can be told apart.

import type { Results } from "./three-answers";

/** The identity-bearing fields of a results document (a thin read over the generated contract). */
export type IdentityInput = Pick<
  Results,
  "results_id" | "study_id" | "option_id" | "revision" | "computed_at" | "scope"
>;

/** A known identity: the lot (from the document's scope) plus the document's result identity. */
export interface KnownIdentity {
  kind: "known";
  /** The lot's BBL, read from the document's scope. */
  lotBbl: string;
  /** The human lot label, read from the document's scope (e.g. "Queens block 7334, lot 70"). */
  lotDisplay: string;
  resultsId: string;
  /** A short deterministic digest of the identity fields; it changes when the revision changes. */
  revisionFingerprint: string;
}

/** A document with no scope cannot be tied to a lot; its identity is unknown, never guessed. */
export interface UnknownIdentity {
  kind: "unknown";
  reason: string;
}

export type ResultIdentity = KnownIdentity | UnknownIdentity;

/** Shown when the document carries no scope — the lot is not identified, and none is invented. */
export const NO_SCOPE_REASON = "The lot is not identified in this document.";

// FNV-1a over the UTF-16 code units of the identity string, rendered as 8 lower-case hex digits.
// A small, dependency-free, deterministic digest — it is an identity label, not a security hash.
function fingerprint(parts: readonly (string | number)[]): string {
  let hash = 0x811c9dc5;
  const text = parts.join("\u0000");
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193);
  }
  return (hash >>> 0).toString(16).padStart(8, "0");
}

/**
 * The identity of a results document. When the document carries a scope, the identity is known: the
 * lot from the scope and a fingerprint of the identity fields. When the document carries no scope
 * (a 1.0.0 document, or a 1.1.0+ document with scope null), the identity is unknown — the lot is
 * never guessed from any other field.
 */
export function resultIdentity(results: IdentityInput): ResultIdentity {
  const scope = results.scope;
  if (!scope) return { kind: "unknown", reason: NO_SCOPE_REASON };
  return {
    kind: "known",
    lotBbl: scope.lot.bbl,
    lotDisplay: scope.lot.display,
    resultsId: results.results_id,
    revisionFingerprint: fingerprint([
      results.results_id,
      results.study_id,
      results.option_id,
      results.revision,
      results.computed_at,
    ]),
  };
}

/**
 * True only when both identities are known and name the same lot, the same results id and the same
 * revision fingerprint. Two documents for different lots are a mismatch; so are two revisions of one
 * lot (so a stale export is caught). An unknown identity never matches anything, including another
 * unknown — an unidentified document is never silently treated as the current one.
 */
export function identitiesMatch(a: ResultIdentity, b: ResultIdentity): boolean {
  if (a.kind !== "known" || b.kind !== "known") return false;
  return (
    a.lotBbl === b.lotBbl &&
    a.resultsId === b.resultsId &&
    a.revisionFingerprint === b.revisionFingerprint
  );
}
