/**
 * Website exact-section law-link resolver (M5-T206; D-094 R027/R246).
 *
 * The TypeScript port of the report's own law-link code
 * (services/api/app/drawings/report/law_links.py section_url/_section_index and
 * sources.py zr_section_page_number), so the website resolves every Zoning
 * Resolution citation to the SAME exact-section URL the PDF links, and a citation
 * with no captured section shows as plain text (no link, never the host homepage).
 *
 * ZR_SECTION_URLS is a committed section-page -> official-URL map derived from the
 * server's law captures and frozen byte-for-byte by the Python parity golden
 * (apps/web/src/test-support/report-parity-law-links.json; regenerate both with
 * UPDATE_GOLDEN=1 on services/api .../test_web_parity_links.py after a capture
 * change). Every URL is re-validated here through the shared source-links
 * allowlist, so a bad or host-only URL is dropped (its page resolves to null),
 * never coerced to the homepage. This module computes no zoning law; it only
 * reproduces the server's resolution. M5-T174 mounts the links in the Results flow.
 */
import { officialZoningTextUrl } from "./source-links";

// Raw committed section-page -> exact official URL map (one entry per captured
// section page; mirrors law_links._section_index at the pinned head). Frozen by
// report-parity-law-links.json; do not hand-edit — regenerate from the server.
const RAW_SECTION_URLS: Record<string, string> = {
  "11-23": "https://zoningresolution.planning.nyc.gov/article-i/chapter-1/11-23",
  "12-10": "https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10",
  "22-12": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-12",
  "22-121": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-121",
  "22-122": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-122",
  "22-13": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-13",
  "22-131": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-131",
  "22-132": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-132",
  "22-133": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-133",
  "22-134": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-134",
  "22-135": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-135",
  "23-12": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-12",
  "23-20": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-20",
  "23-21": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-21",
  "23-22": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22",
  "23-23": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-23",
  "23-231": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-231",
  "23-232": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-232",
  "23-233": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-233",
  "23-234": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-234",
  "23-24": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-24",
  "23-241": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-241",
  "23-242": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-242",
  "23-243": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-243",
  "23-311": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-311",
  "23-312": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-312",
  "23-322": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-322",
  "23-335": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-335",
  "23-34": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-34",
  "23-341": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-341",
  "23-342": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342",
  "23-343": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-343",
  "23-344": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344",
  "23-35": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-35",
  "23-351": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-351",
  "23-352": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-352",
  "23-353": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-353",
  "23-362": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362",
  "23-363": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-363",
  "23-371": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-371",
  "23-372": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-372",
  "23-381": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-381",
  "23-41": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-41",
  "23-411": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-411",
  "23-412": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-412",
  "23-413": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-413",
  "23-43": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-43",
  "23-431": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-431",
  "23-432": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432",
  "23-433": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-433",
  "23-434": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-434",
  "23-435": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-435",
  "23-436": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436",
  "23-44": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-44",
  "23-441": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-441",
  "23-442": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-442",
  "23-443": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-443",
  "23-51": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-51",
  "23-52": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52",
  "23-62": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-62",
  "23-63": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-63",
  "24-04": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-04",
  "24-11": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-11",
  "24-111": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-111",
  "24-161": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-161",
  "24-162": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-162",
  "24-163": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-163",
  "24-33": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-33",
  "24-34": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-34",
  "24-35": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-35",
  "24-36": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-36",
  "24-37": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-37",
  "24-38": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-38",
  "24-39": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-39",
  "24-391": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-391",
  "24-392": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-392",
  "24-393": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-393",
  "24-52": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-52",
  "24-522": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-522",
  "24-56": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-56",
  "25-02": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-02",
  "25-20": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-20",
  "25-211": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-211",
  "25-212": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-212",
  "25-22": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-22",
  "25-221": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-221",
  "25-222": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-222",
  "25-23": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-23",
  "25-231": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-231",
  "25-232": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-232",
  "25-24": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-24",
  "25-241": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-241",
  "25-80": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-80",
  "25-81": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-81",
  "25-811": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811",
  "27-111": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-111",
  "27-131": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-131",
  "27-133": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-133",
  "27-14": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-14",
  "27-151": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-151",
  "27-16": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-16",
  "27-161": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-161",
  "27-162": "https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-162",
  "32-121": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-2/32-121",
  "32-131": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-2/32-131",
  "32-161": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-2/32-161",
  "32-421": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-2/32-421",
  "33-10": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-10",
  "33-11": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-11",
  "33-12": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-12",
  "33-121": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-121",
  "33-122": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-122",
  "33-123": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-123",
  "33-26": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-26",
  "33-27": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-27",
  "33-28": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-28",
  "33-30": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-30",
  "33-301": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-301",
  "33-302": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-302",
  "33-303": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-303",
  "34-11": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-11",
  "34-111": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111",
  "34-112": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-112",
  "34-113": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-113",
  "34-21": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-21",
  "34-22": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-22",
  "34-221": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-221",
  "34-222": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-222",
  "34-223": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-223",
  "34-224": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-224",
  "34-23": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-23",
  "34-231": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-231",
  "34-232": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-232",
  "34-233": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-233",
  "34-24": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-24",
  "35-00": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-00",
  "35-01": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-01",
  "35-20": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-20",
  "35-21": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-21",
  "35-22": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-22",
  "35-23": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-23",
  "35-24": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-24",
  "35-30": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-30",
  "35-31": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31",
  "35-32": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-32",
  "35-33": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-33",
  "35-36": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-36",
  "35-53": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-53",
  "35-62": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-62",
  "35-63": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-63",
  "35-631": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631",
  "35-632": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-632",
  "35-633": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633",
  "35-64": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-64",
  "35-641": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-641",
  "35-642": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-642",
  "35-643": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-643",
  "35-71": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-71",
  "36-21": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-21",
  "36-23": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-23",
  "36-231": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-231",
  "36-232": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-232",
  "36-233": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-233",
  "36-24": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-24",
  "36-25": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-25",
  "36-30": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-30",
  "36-31": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-31",
  "36-62": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-62",
  "36-64": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-64",
  "36-70": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-70",
  "36-71": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-71",
  "36-711": "https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-711",
  "54-311": "https://zoningresolution.planning.nyc.gov/article-v/chapter-4/54-311",
  "54-40": "https://zoningresolution.planning.nyc.gov/article-v/chapter-4/54-40",
  "54-41": "https://zoningresolution.planning.nyc.gov/article-v/chapter-4/54-41",
  "66-11": "https://zoningresolution.planning.nyc.gov/article-vi/chapter-6/66-11",
  "73-11": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-3/73-11",
  "73-13": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-3/73-13",
  "73-18": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-3/73-18",
  "73-432": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-3/73-432",
  "73-433": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-3/73-433",
  "74-52": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-4/74-52",
  "74-902": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-4/74-902",
  "74-903": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-4/74-903",
  "75-31": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-5/75-31",
  "76-131": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-6/76-131",
  "77-00": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-00",
  "77-01": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-01",
  "77-10": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-10",
  "77-11": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-11",
  "77-12": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-12",
  "77-20": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-20",
  "77-21": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-21",
  "77-211": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-211",
  "77-22": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-22",
  "77-24": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-24",
  "77-25": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-25",
  "77-26": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-26",
  "77-27": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-27",
  "77-28": "https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-28",
};

/**
 * The resolver's section-page -> URL map: every RAW entry re-validated through the
 * same allowlist the server uses (officialZoningTextUrl). A URL that fails the
 * allowlist is dropped so sectionUrl returns null, never the host homepage.
 */
export const ZR_SECTION_URLS: Record<string, string> = Object.fromEntries(
  Object.entries(RAW_SECTION_URLS).filter(([, url]) => officialZoningTextUrl(url) !== null),
);

// Anchored at the start only (Python re.match on \d{1,3}-\d{1,4}).
const SECTION_PAGE_RE = /^\d{1,3}-\d{1,4}/;

/**
 * The section PAGE number of a cited section: strip a leading "ZR", then take the
 * leading <n>-<n> (any sub-paragraph dropped). A value with no section number
 * yields "". TypeScript port of sources.zr_section_page_number.
 */
export function zrSectionPageNumber(cited: unknown): string {
  const text = String(cited || "").trim();
  const bare = text.toUpperCase().startsWith("ZR") ? text.slice(2).trim() : text;
  const match = SECTION_PAGE_RE.exec(bare);
  return match ? match[0] : "";
}

/**
 * The exact official section URL for a cited section (sub-paragraph dropped for the
 * lookup), or null when no capture records that section. TypeScript port of
 * law_links.section_url.
 */
export function sectionUrl(cited: unknown): string | null {
  const page = zrSectionPageNumber(cited);
  if (!page) return null;
  return ZR_SECTION_URLS[page] ?? null;
}
