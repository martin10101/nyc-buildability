import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { officialZoningTextUrl } from "@/lib/architect/source-links";
import { ZR_SECTION_URLS, sectionUrl, zrSectionPageNumber } from "@/lib/architect/zr-section-urls";

/**
 * M5-T206 — the website's exact-section law-link resolver, pinned to the report's own code
 * through a Python-written golden (services/api/.../test_web_parity_links.py writes it from
 * law_links._section_index/section_url + sources.zr_section_page_number). ZR_SECTION_URLS must
 * deep-equal the golden's section_index, and zrSectionPageNumber/sectionUrl must reproduce every
 * pinned case; hand-editing one golden number reddens this suite and the Python test together.
 */

interface Golden {
  section_index: Record<string, string>;
  page_number_cases: { cited: unknown; page: string }[];
  section_url_cases: { cited: unknown; url: string | null }[];
}

const HOST = "https://zoningresolution.planning.nyc.gov";

/** Read the SAME golden the Python parity test writes (apps/web cwd during vitest). */
function readGolden(): Golden {
  const path = resolve(process.cwd(), "src/test-support/report-parity-law-links.json");
  return JSON.parse(readFileSync(path, "utf8")) as Golden;
}

const golden = readGolden();

describe("zrSectionPageNumber (port of sources.zr_section_page_number)", () => {
  // Pure citation parsing (independent of the capture set): pinned cases from S1.
  it.each([
    ["ZR 23-52(b)", "23-52"],
    ["12-10", "12-10"],
    ["ZR 23-344(c)(3)", "23-344"],
    ["ZR 23-362", "23-362"],
    ["zr 23-362", "23-362"],
    ["  ZR 23-362  ", "23-362"],
  ])("%s -> %s (ZR stripped, sub-paragraph dropped, start-anchored)", (cited, page) => {
    expect(zrSectionPageNumber(cited)).toBe(page);
  });

  // A value with no leading <n>-<n> yields "" (S1): null, a number, blank and prose.
  it.each([
    [null, ""],
    [123, ""],
    ["", ""],
    ["Appendix A", ""],
    ["New York City Zoning Resolution (official text)", ""],
  ] as [unknown, string][])("%s -> empty", (cited, page) => {
    expect(zrSectionPageNumber(cited)).toBe(page);
  });

  // Start-anchoring (RISK 2): a section number BURIED after other text must NOT be picked up.
  // This guards the `^` in SECTION_PAGE_RE / Python re.match: dropping the anchor would make
  // these parse the embedded "23-52" and redden here and the server-written golden together.
  it.each([
    ["see 23-52", ""],
    ["Appendix 23-52", ""],
    ["note 12-10 applies", ""],
  ] as [unknown, string][])("buried number %s is not matched (start-anchored)", (cited, page) => {
    expect(zrSectionPageNumber(cited)).toBe(page);
  });

  it("reproduces every golden page-number case (parity with the server)", () => {
    for (const { cited, page } of golden.page_number_cases) {
      expect(zrSectionPageNumber(cited)).toBe(page);
    }
  });
});

describe("ZR_SECTION_URLS (committed section-page -> URL map)", () => {
  it("deep-equals the golden section_index (web/PDF parity; S4)", () => {
    expect(ZR_SECTION_URLS).toEqual(golden.section_index);
  });

  it("holds an exact section URL for every page, never the bare host (S5)", () => {
    const pages = Object.keys(ZR_SECTION_URLS);
    expect(pages.length).toBeGreaterThan(0);
    for (const page of pages) {
      const url = ZR_SECTION_URLS[page];
      // every value passes the shared allowlist unchanged (canonical form)...
      expect(officialZoningTextUrl(url)).toBe(url);
      // ...and is the EXACT section (last path segment == its page), not a host/chapter link.
      expect(url.startsWith(`${HOST}/`)).toBe(true);
      expect(url.split("#")[0].replace(/\/$/, "").split("/").pop()).toBe(page);
    }
  });

  it("drops a host-only URL at the validator (S5)", () => {
    // the bare host fails officialZoningTextUrl, so such a page would never enter the map.
    expect(officialZoningTextUrl(`${HOST}/`)).toBeNull();
  });
});

describe("sectionUrl (port of law_links.section_url)", () => {
  it("reproduces every golden section_url case, incl. the no-capture null (S2, S3)", () => {
    for (const { cited, url } of golden.section_url_cases) {
      expect(sectionUrl(cited)).toBe(url);
    }
  });

  it("resolves a cited sub-paragraph to its exact section page (S2)", () => {
    const direct = sectionUrl("23-52");
    expect(sectionUrl("ZR 23-52(b)")).toBe(direct);
    if (direct !== null) {
      expect(direct.replace(/\/$/, "").split("/").pop()).toBe("23-52");
    }
  });

  it("returns null for a citation whose page has no capture (S3)", () => {
    // a page absent from the map resolves to null (plain text), never the homepage.
    const absent = "999-99";
    expect(ZR_SECTION_URLS[absent]).toBeUndefined();
    expect(sectionUrl(`ZR ${absent}`)).toBeNull();
    // and a value with no section number resolves to null, not an invented link.
    expect(sectionUrl("Appendix A")).toBeNull();
  });
});
