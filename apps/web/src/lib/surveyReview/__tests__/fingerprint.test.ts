import { describe, expect, it } from "vitest";
import { historyFingerprint, sha256Hex } from "@/lib/surveyReview/fingerprint";

/**
 * The dependency-free SHA-256 must match the standard FIPS-180-4 vectors so the
 * client-derived `accepted_history_fingerprint` matches the backend
 * `history_fingerprint` (canonical JSON + sha256). If these drift, corrections
 * fail SAFELY with concurrent_review_modification (never data loss), but the
 * seam is meant to match.
 */
describe("sha256Hex — known vectors", () => {
  it("hashes the empty string", () => {
    expect(sha256Hex("")).toBe(
      "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    );
  });
  it("hashes 'abc'", () => {
    expect(sha256Hex("abc")).toBe(
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
    );
  });
  it("hashes a longer message", () => {
    expect(sha256Hex("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq")).toBe(
      "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1",
    );
  });
});

describe("historyFingerprint", () => {
  it("returns sha256:<hex> over the canonical empty history", () => {
    const fp = historyFingerprint([]);
    // canonical JSON of [] is "[]"
    expect(fp).toBe(`sha256:${sha256Hex("[]")}`);
    expect(fp).toMatch(/^sha256:[0-9a-f]{64}$/);
  });
  it("changes when the history changes", () => {
    const a = historyFingerprint([]);
    const b = historyFingerprint([{ reason: "x", corrected_units: null } as never]);
    expect(a).not.toBe(b);
  });
  it("is stable and key-order independent (canonical sort)", () => {
    const one = historyFingerprint([{ a: 1, b: 2 } as never]);
    const two = historyFingerprint([{ b: 2, a: 1 } as never]);
    expect(one).toBe(two);
  });
});
