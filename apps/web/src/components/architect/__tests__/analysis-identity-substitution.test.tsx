import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { AnalysisIdentityNotice } from "../AnalysisIdentityNotice";
import type { RuleEvaluation } from "@/lib/rule-evaluation-contract";
import {
  SUBSTITUTION_ANALYZED_BBL,
  SUBSTITUTION_ENTERED_BBL,
  draftApplicableDoc,
  substitutionStampDoc,
} from "@/test-support/rule-evaluation-fixtures";

/**
 * M5-T058 — AnalysisIdentityNotice substitution branch (DB-036(d) closure).
 *
 * Both directions of the guard are bound here:
 *  - a rule_evaluation document CARRYING a substrate_substitution stamp that
 *    CORRESPONDS to the identities on screen (its entered_bbl is the opened
 *    property AND equals evaluated_input.bbl, and its analyzed_bbl is a real,
 *    DIFFERENT base lot) renders a legitimate "analyzed on the base lot" record
 *    and the fail-safe withhold alert does NOT fire;
 *  - an UNSTAMPED entered-vs-analyzed mismatch still withholds exactly as before,
 *    and a NON-CORRESPONDING stamp is ignored so the withhold guard still governs
 *    (the guard is closed by ADDING the stamped branch, never by relaxing the
 *    unstamped path).
 *
 * The component only ever shows a RECORD of which identity was analyzed; no
 * calculated allowance is presented here. Web behaviour proves in CI only.
 */

afterEach(cleanup);

const LABEL = "Rule evaluation";
const SUB_TESTID = "analysis-identity-substitution-rule-evaluation";
const ALERT_TESTID = "analysis-identity-rule-evaluation";

/** The component reads only these two fields; the fixture supplies the full doc. */
type NoticeDoc = {
  evaluated_input: { bbl: string | null };
  substrate_substitution?: RuleEvaluation["substrate_substitution"];
} | null;

function renderNotice(requestedBbl: string, document: NoticeDoc) {
  return render(
    <AnalysisIdentityNotice label={LABEL} requestedBbl={requestedBbl} document={document} />,
  );
}

describe("M5-T058 — corresponding stamp renders a legitimate substitution record", () => {
  it("shows the entered-vs-analyzed base-lot record and fires NO withhold alert", () => {
    const doc = substitutionStampDoc();
    // The stamp corresponds: entered_bbl == the opened property == evaluated_input.bbl.
    expect(doc.evaluated_input.bbl).toBe(SUBSTITUTION_ENTERED_BBL);
    expect(doc.substrate_substitution?.entered_bbl).toBe(SUBSTITUTION_ENTERED_BBL);
    expect(doc.substrate_substitution?.analyzed_bbl).toBe(SUBSTITUTION_ANALYZED_BBL);

    renderNotice(SUBSTITUTION_ENTERED_BBL, doc);

    const notice = screen.getByTestId(SUB_TESTID);
    expect(notice).toHaveAttribute("data-identity-state", "substituted");
    expect(notice).toHaveTextContent(`${LABEL} analyzed on the base lot`);
    expect(notice).toHaveTextContent(`You entered BBL ${SUBSTITUTION_ENTERED_BBL}`);
    expect(notice).toHaveTextContent(`base tax lot BBL ${SUBSTITUTION_ANALYZED_BBL}`);
    expect(notice).toHaveTextContent("recorded as entered versus analyzed");
    expect(notice).toHaveTextContent("not a computed allowance");
    // The RECORD of the returned document is captured, never a computed allowance.
    expect(screen.getByText(`Returned ${LABEL.toLowerCase()} record`)).toBeInTheDocument();

    // The safety withhold branch must NOT fire for a legitimate stamped substitution.
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.queryByTestId(ALERT_TESTID)).toBeNull();
    expect(screen.queryByText(/Results are withheld from this property/)).toBeNull();
  });
});

describe("DB-042(d)/(e) — the substitution record defines billing/base inline and uses consistent-domain wording", () => {
  it("defines 'billing lot' and 'base' on first use and reads as a city record (guard behaviour unchanged)", () => {
    const doc = substitutionStampDoc();
    renderNotice(SUBSTITUTION_ENTERED_BBL, doc);

    const notice = screen.getByTestId(SUB_TESTID);
    // DB-042(e): the analyst is told, inline on first use, that the entered BBL is
    // a condo billing lot and what the base lot is — no undefined jargon.
    expect(notice).toHaveTextContent("condo billing lot (the single tax lot a condo is billed under)");
    expect(notice).toHaveTextContent("the land parcel the city records as this condo");
    // DB-042(d): consistent-domain "city record" framing shared with the
    // condo-records section, still disclaiming a computed allowance.
    expect(notice).toHaveTextContent("a city record of the documented resolution");
    expect(notice).toHaveTextContent("not a computed allowance");
    // The record branch stays non-alarming (no withhold alert fires).
    expect(screen.queryByRole("alert")).toBeNull();
  });
});

describe("M5-T058 — an UNSTAMPED entered-vs-analyzed mismatch still withholds", () => {
  it("withholds with the neutral entered-vs-analyzed alert (no stamp present)", () => {
    const doc = draftApplicableDoc();
    doc.evaluated_input.bbl = SUBSTITUTION_ANALYZED_BBL; // differs from the opened property
    // No substrate_substitution key at all.
    expect(doc.substrate_substitution).toBeUndefined();

    renderNotice(SUBSTITUTION_ENTERED_BBL, doc);

    const alert = screen.getByRole("alert");
    expect(alert).toHaveAttribute("data-identity-state", "differs");
    expect(alert).toHaveTextContent(`${LABEL} identity mismatch`);
    expect(alert).toHaveTextContent("Results are withheld from this property");
    expect(alert).toHaveTextContent("no relationship between them is inferred");
    expect(alert).toHaveTextContent("no calculated allowance is shown");
    expect(screen.queryByTestId(SUB_TESTID)).toBeNull();
  });

  it("withholds with the missing-identity alert when the analysis states no BBL", () => {
    const doc = draftApplicableDoc();
    doc.evaluated_input.bbl = null;

    renderNotice(SUBSTITUTION_ENTERED_BBL, doc);

    const alert = screen.getByRole("alert");
    expect(alert).toHaveAttribute("data-identity-state", "absent");
    expect(alert).toHaveTextContent(`${LABEL} identity missing`);
    expect(alert).toHaveTextContent("returned BBL not stated");
    expect(screen.queryByTestId(SUB_TESTID)).toBeNull();
  });
});

describe("M5-T058 — a NON-CORRESPONDING stamp is ignored; the withhold guard governs", () => {
  it("ignores a stamp whose entered_bbl is not the opened property (still withholds)", () => {
    const doc = substitutionStampDoc();
    // The analysis was run for a different property AND the stamp names that
    // other property as entered — it does not correspond to the opened lot.
    doc.evaluated_input.bbl = SUBSTITUTION_ANALYZED_BBL;
    doc.substrate_substitution!.entered_bbl = SUBSTITUTION_ANALYZED_BBL;

    renderNotice(SUBSTITUTION_ENTERED_BBL, doc);

    expect(screen.queryByTestId(SUB_TESTID)).toBeNull();
    const alert = screen.getByRole("alert");
    expect(alert).toHaveAttribute("data-identity-state", "differs");
    expect(alert).toHaveTextContent("Results are withheld from this property");
  });

  it("ignores a stamp whose entered_bbl disagrees with evaluated_input.bbl (still withholds)", () => {
    const doc = substitutionStampDoc();
    // entered_bbl matches the opened property, but evaluated_input.bbl reports a
    // different lot — the stamp does not correspond, so the guard governs.
    doc.evaluated_input.bbl = SUBSTITUTION_ANALYZED_BBL;
    expect(doc.substrate_substitution!.entered_bbl).toBe(SUBSTITUTION_ENTERED_BBL);

    renderNotice(SUBSTITUTION_ENTERED_BBL, doc);

    expect(screen.queryByTestId(SUB_TESTID)).toBeNull();
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Results are withheld from this property",
    );
  });

  it("renders no substitution record for a degenerate stamp whose analyzed_bbl equals entered_bbl", () => {
    const doc = substitutionStampDoc();
    // analyzed_bbl is not a real, different base lot — no legitimate substitution.
    doc.substrate_substitution!.analyzed_bbl = SUBSTITUTION_ENTERED_BBL;

    renderNotice(SUBSTITUTION_ENTERED_BBL, doc);

    // Not a legitimate stamp, and the identities match, so nothing renders (no
    // false substitution notice, no spurious alert).
    expect(screen.queryByTestId(SUB_TESTID)).toBeNull();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("renders nothing when a matching identity carries no legitimate stamp", () => {
    const doc = draftApplicableDoc();
    doc.evaluated_input.bbl = SUBSTITUTION_ENTERED_BBL;

    const { container } = renderNotice(SUBSTITUTION_ENTERED_BBL, doc);

    expect(container.querySelector<HTMLElement>("section")).toBeNull();
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.queryByTestId(SUB_TESTID)).toBeNull();
  });
});
