import { describe, expect, it } from "vitest";
import { officialZoningTextUrl } from "@/lib/architect/source-links";

/**
 * M5-T187 (S6, D-094 R027) — the web zoning-link validator accepts exactly the URL forms the server's
 * validator accepts, so every statutory citation resolves to an exact section rather than a bare host
 * link. The server mirror is services/api/app/drawings/report/law_links.py (official_zoning_text_url);
 * both apply the SAME host/path/anchor rules:
 *
 *   • https only, host zoningresolution.planning.nyc.gov, no query, no credentials, no port;
 *   • path /article-<roman>/chapter-<n>[/<section>] — roman is [ivxlcdm]+, chapter is 1-2 digits,
 *     an optional section is \d{2}-\d{2,4};
 *   • an optional anchor only in the form #\d{2}-\d{2,4};
 *   • no control character, space or backslash anywhere, and length <= 500.
 *
 * This is a self-contained positive/negative case table — it does NOT parse law_links.py at runtime
 * (cross-language parsing is brittle and this part touches no services/api file). If the two
 * validators ever diverge, the fix to source-links.ts is routed to the orchestrator (it is read-only
 * here).
 */

const HOST = "https://zoningresolution.planning.nyc.gov";

/** Forms the server validator accepts; the web validator must return them in canonical form. */
const ACCEPTED: ReadonlyArray<{ readonly input: string; readonly canonical: string }> = [
  // article + chapter, no section
  { input: `${HOST}/article-ii/chapter-3`, canonical: `${HOST}/article-ii/chapter-3` },
  // article + chapter + section
  { input: `${HOST}/article-ii/chapter-3/23-52`, canonical: `${HOST}/article-ii/chapter-3/23-52` },
  // with a valid section anchor
  {
    input: `${HOST}/article-ii/chapter-3/23-52#23-52`,
    canonical: `${HOST}/article-ii/chapter-3/23-52#23-52`,
  },
  // a different article / chapter / four-digit section
  { input: `${HOST}/article-xi/chapter-12/12-10`, canonical: `${HOST}/article-xi/chapter-12/12-10` },
  { input: `${HOST}/article-i/chapter-1/11-255`, canonical: `${HOST}/article-i/chapter-1/11-255` },
];

/** Forms the server validator rejects (-> null); the web validator must reject each identically. */
const REJECTED: ReadonlyArray<{ readonly label: string; readonly input: unknown }> = [
  { label: "the bare host (homepage)", input: `${HOST}/` },
  { label: "the host with no trailing slash", input: HOST },
  { label: "a wrong host", input: "https://example.com/article-ii/chapter-3" },
  { label: "http (wrong scheme)", input: "http://zoningresolution.planning.nyc.gov/article-ii/chapter-3" },
  { label: "a query string", input: `${HOST}/article-ii/chapter-3?x=1` },
  { label: "an explicit port", input: "https://zoningresolution.planning.nyc.gov:8443/article-ii/chapter-3" },
  {
    label: "embedded credentials",
    input: "https://user:pass@zoningresolution.planning.nyc.gov/article-ii/chapter-3",
  },
  { label: "a non-roman article number", input: `${HOST}/article-2/chapter-3` },
  { label: "an uppercase roman article", input: `${HOST}/article-II/chapter-3` },
  { label: "a three-digit chapter", input: `${HOST}/article-ii/chapter-123` },
  { label: "a malformed section segment", input: `${HOST}/article-ii/chapter-3/badsection` },
  { label: "an extra trailing path segment", input: `${HOST}/article-ii/chapter-3/23-52/extra` },
  { label: "a malformed anchor", input: `${HOST}/article-ii/chapter-3#foo` },
  { label: "a space in the path", input: `${HOST}/article-ii/chapter-3 ` },
  { label: "a backslash in the path", input: `${HOST}/article-ii\\chapter-3` },
  { label: "an over-length value", input: `${HOST}/article-ii/chapter-3/23-52#${"9".repeat(600)}` },
  { label: "a non-string (null)", input: null },
  { label: "a non-string (number)", input: 123 },
  { label: "a non-string (undefined)", input: undefined },
];

describe("S6 — officialZoningTextUrl accepts exactly the valid ZR section forms", () => {
  for (const { input, canonical } of ACCEPTED) {
    it(`accepts ${input} and returns its canonical form`, () => {
      expect(officialZoningTextUrl(input)).toBe(canonical);
    });
  }
});

describe("S6 — officialZoningTextUrl rejects every other form", () => {
  for (const { label, input } of REJECTED) {
    it(`rejects ${label}`, () => {
      expect(officialZoningTextUrl(input)).toBeNull();
    });
  }
});
