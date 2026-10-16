import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { ZR_SECTION_URLS, sectionUrl } from "@/lib/architect/zr-section-urls";
import { ZrSectionLinks } from "../ZrSectionLinks";

/**
 * M5-T206 — the presentational exact-section law-link component. A citation that resolves
 * (sectionUrl non-null) renders as an anchor to its exact section (new tab); one that does not
 * renders as plain text; a blank/missing citation renders nothing. The resolvable label is taken
 * from the committed map so the test stays decoupled from which sections are captured, while the
 * unresolvable label uses a page absent from the map.
 */

afterEach(cleanup);

// A page the committed map resolves, cited with a sub-paragraph so the visible label keeps it.
const RESOLVABLE_PAGE = Object.keys(ZR_SECTION_URLS)[0];
const RESOLVABLE_LABEL = `ZR ${RESOLVABLE_PAGE}(a)`;
const RESOLVABLE_HREF = ZR_SECTION_URLS[RESOLVABLE_PAGE];
// A page with no capture: resolves to null -> plain text (matches the PDF for ZR 11-25).
const UNRESOLVABLE_LABEL = "ZR 999-99";

describe("ZrSectionLinks", () => {
  it("renders a resolvable citation as an exact-section anchor (new tab), label verbatim (S6)", () => {
    expect(sectionUrl(RESOLVABLE_LABEL)).toBe(RESOLVABLE_HREF);
    render(<ZrSectionLinks citations={[RESOLVABLE_LABEL]} />);
    const link = screen.getByTestId("zr-section-link");
    expect(link.tagName).toBe("A");
    expect(link).toHaveAttribute("href", RESOLVABLE_HREF);
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
    expect(link.textContent).toBe(RESOLVABLE_LABEL);
    // never the bare host.
    expect(link).not.toHaveAttribute("href", "https://zoningresolution.planning.nyc.gov/");
  });

  it("renders an unresolvable citation as plain text, no anchor (S3)", () => {
    expect(sectionUrl(UNRESOLVABLE_LABEL)).toBeNull();
    render(<ZrSectionLinks citations={[UNRESOLVABLE_LABEL]} />);
    expect(screen.queryByTestId("zr-section-link")).toBeNull();
    const plain = screen.getByTestId("zr-section-plain");
    expect(plain.textContent).toBe(UNRESOLVABLE_LABEL);
  });

  it("keeps resolvable links and plain text in order and skips blanks (S6)", () => {
    render(
      <ZrSectionLinks citations={[RESOLVABLE_LABEL, "", UNRESOLVABLE_LABEL, "   "]} />,
    );
    // exactly one anchor and one plain-text item; the two blank entries render nothing.
    const links = screen.getAllByTestId("zr-section-link");
    const plains = screen.getAllByTestId("zr-section-plain");
    expect(links).toHaveLength(1);
    expect(plains).toHaveLength(1);
    expect(links[0]).toHaveAttribute("href", RESOLVABLE_HREF);
    expect(plains[0].textContent).toBe(UNRESOLVABLE_LABEL);
    // order preserved: the link precedes the plain text in the DOM.
    const container = screen.getByTestId("zr-section-links");
    expect(container.textContent).toBe(`${RESOLVABLE_LABEL}${UNRESOLVABLE_LABEL}`);
  });

  it("renders nothing for an empty or all-blank citation list (nothing invented)", () => {
    const { container: empty } = render(<ZrSectionLinks citations={[]} />);
    expect(empty.firstChild).toBeNull();
    cleanup();
    const { container: blanks } = render(<ZrSectionLinks citations={["", "   "]} />);
    expect(blanks.firstChild).toBeNull();
    expect(screen.queryByTestId("zr-section-links")).toBeNull();
  });
});
