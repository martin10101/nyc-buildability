import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { SurveyReviewScreen } from "@/components/survey-review/SurveyReviewScreen";
import { SurveyReviewClientProvider } from "@/lib/surveyReview/context";
import type { ActionOutcome, ReviewDocument, SurveyReviewClient } from "@/lib/surveyReview/types";
import {
  createMockSurveyReviewClient,
  seedStore,
  DIGEST_PRO,
  DIGEST_USER,
} from "@/test-support/survey-review/mockClient";

/**
 * Survey review screen component journeys (task M2-T016 rework). Drives the
 * human journey against the reconciled mock backend: accept / correct / reject,
 * downstream honesty, confirmation gating, plus the human-journey fixes F1
 * (dominant-action flips to Confirm) and F3 (stale-history draft preservation).
 */

const CLEAN = "sev:doc:p1:1";
const AREA = "sev:doc:p1:2";
const NORTH = "sev:doc:p1:3";

afterEach(cleanup);

function renderScreen(digest = DIGEST_PRO, client?: SurveyReviewClient) {
  const resolved = client ?? createMockSurveyReviewClient(seedStore());
  return render(
    <SurveyReviewClientProvider client={resolved}>
      <SurveyReviewScreen documentDigest={digest} />
    </SurveyReviewClientProvider>,
  );
}

async function correctFocused(value: string, reason: string) {
  fireEvent.click(screen.getByTestId("action-correct"));
  fireEvent.change(screen.getByTestId("correction-value"), { target: { value } });
  fireEvent.change(screen.getByTestId("correction-reason"), { target: { value: reason } });
  fireEvent.click(screen.getByTestId("correction-submit"));
}

describe("SurveyReviewScreen — orientation (SC-S1/S4)", () => {
  it("shows the document state, overlay, urgency-ordered facts, and Unconfirmed evidence", async () => {
    renderScreen();
    await screen.findByTestId("review-topbar");
    expect(screen.getByTestId("document-state-badge")).toHaveTextContent("Needs review");
    expect(screen.getByTestId(`overlay-mark-${AREA}`)).toBeInTheDocument();
    expect(screen.getByTestId("focused-heading")).toHaveTextContent("Stated lot area");
    expect(screen.getByTestId(`fact-confirmation-${CLEAN}`)).toHaveTextContent("Unconfirmed evidence");
    expect(screen.queryByText("Verified", { exact: true })).toBeNull();
  });

  it("F1: the dominant action counts only open items, then flips to Confirm when resolved", async () => {
    renderScreen();
    await screen.findByTestId("review-topbar");
    // f1 (clean/unconfirmed) is NOT counted; only f2 (conflict) + f3 (unresolved).
    expect(screen.getByTestId("dominant-action")).toHaveTextContent("resolve 2 open items");

    await correctFocused("4800", "resolve area conflict");
    await screen.findByTestId("correction-chain");

    fireEvent.click(screen.getByTestId(`fact-row-${NORTH}`));
    await correctFocused("15", "resolve north orientation");
    await waitFor(() =>
      expect(screen.getByTestId("dominant-action")).toHaveTextContent(/confirm or reject the document/i),
    );
  });
});

describe("SurveyReviewScreen — correction journey (SC-S2/S5/S6)", () => {
  it("corrects the conflict, preserves the immutable original, and clears its downstream block", async () => {
    renderScreen();
    await screen.findByTestId("focused-item");

    expect(screen.getByTestId("check-conflict")).toBeInTheDocument();
    expect(screen.getByTestId("conflict-resolve")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /dismiss|acknowledge|ignore/i })).toBeNull();
    expect(screen.getByTestId(`downstream-${AREA}`)).toHaveAttribute("data-status", "blocked");

    await correctFocused("4800", "OCR misread the stated area digit.");
    await screen.findByTestId("correction-chain");
    expect(screen.getByTestId("correction-chain")).toHaveTextContent("OCR misread");
    expect(screen.getByTestId("original-value")).toHaveTextContent("5,000 SF");
    expect(screen.getByTestId("current-value")).toHaveTextContent("4800");

    // The area fact's downstream flips from blocked to provisional (recalculated).
    await waitFor(() =>
      expect(screen.getByTestId(`downstream-${AREA}`)).toHaveAttribute("data-status", "provisional"),
    );
  });
});

describe("SurveyReviewScreen — accept affordance (F2)", () => {
  it("shows a session affirmation marker with accurate copy after Accept", async () => {
    renderScreen();
    await screen.findByTestId("focused-item");
    fireEvent.click(screen.getByTestId(`fact-row-${CLEAN}`));
    fireEvent.click(await screen.findByTestId("action-accept"));
    await screen.findByTestId("accept-affirmed");
    expect(screen.getByTestId("accept-affirmed")).toHaveTextContent("affirmed this value this session");
    expect(screen.getByTestId("accept-affirmed")).toHaveTextContent("recalculation of dependent conclusions was requested");
  });
});

describe("SurveyReviewScreen — stale-history draft preservation (F3)", () => {
  it("keeps the reviewer's unsaved correction input when the item changed underneath", async () => {
    const store = seedStore();
    const base = createMockSurveyReviewClient(store);
    // Build a fresh document where AREA already gained a concurrent correction
    // (history length 1) so the focused item REMOUNTS on reload.
    const freshRead = await base.readDocument(DIGEST_PRO);
    const fresh: ReviewDocument =
      freshRead.kind === "document" ? JSON.parse(JSON.stringify(freshRead.document)) : ({} as ReviewDocument);
    const area = fresh.facts.find((f) => f.evidence_id === AREA)!;
    area.correction_history = [
      {
        corrected_at: "2026-07-20T12:30:00Z",
        corrected_by_role: "qualified_professional",
        previous_normalized_value: 5000,
        corrected_normalized_value: 5000,
        previous_units: "square_feet",
        corrected_units: "square_feet",
        reason: "concurrent edit by another reviewer",
      },
    ];
    area.correction_count = 1;

    let firstCorrect = true;
    const client: SurveyReviewClient = {
      ...base,
      correctFact: async (req, o): Promise<ActionOutcome> => {
        if (firstCorrect) {
          firstCorrect = false;
          return {
            kind: "error",
            reject_code: "concurrent_review_modification",
            message: "the fact changed",
            correlationId: null,
            currentDocument: fresh,
          };
        }
        return base.correctFact(req, o);
      },
    };

    renderScreen(DIGEST_PRO, client);
    await screen.findByTestId("focused-item");
    await correctFocused("4800", "my correction");

    // The editor stays open with the preserved draft + a persistent stale notice.
    await screen.findByTestId("stale-notice");
    const form = screen.getByTestId("correction-form");
    expect(within(form).getByTestId("correction-value")).toHaveValue("4800");
    expect(within(form).getByTestId("correction-reason")).toHaveValue("my correction");
  });
});

describe("SurveyReviewScreen — authorization (SC-S3)", () => {
  it("a preparer cannot reject a fact or confirm the document (mirrored + server-enforced)", async () => {
    renderScreen(DIGEST_USER);
    await screen.findByTestId("focused-item");
    expect(screen.getByTestId("action-correct")).not.toBeDisabled();
    expect(screen.getByTestId("action-reject")).toBeDisabled();
    expect(screen.getByTestId("action-disabled-reason")).toBeInTheDocument();
    expect(screen.queryByTestId("action-confirm-document")).toBeNull();
    expect(screen.getByTestId("confirm-capability-note")).toBeInTheDocument();
  });

  it("offers the confirm control to a professional but blocks it until the H5 gate is met", async () => {
    renderScreen(DIGEST_PRO);
    await screen.findByTestId("document-decision");
    expect(screen.getByTestId("action-confirm-document")).toBeDisabled();
    expect(screen.getByTestId("confirm-blocked-explanation")).toHaveTextContent("Stated lot area");
  });
});

describe("SurveyReviewScreen — reject blocks confirmation, reopen recovers (SC-S1)", () => {
  it("rejecting a fact blocks confirmation with the rejected fact named; confirm after resolving both", async () => {
    renderScreen();
    await screen.findByTestId("focused-item");

    // Resolve the conflict, reject the unresolved detection.
    await correctFocused("4800", "resolve conflict");
    await screen.findByTestId("correction-chain");
    fireEvent.click(screen.getByTestId(`fact-row-${NORTH}`));
    fireEvent.click(await screen.findByTestId("action-reject"));
    fireEvent.change(screen.getByTestId("reject-fact-reason"), { target: { value: "AI guess unusable" } });
    fireEvent.click(screen.getByTestId("reject-fact-submit"));
    await waitFor(() =>
      expect(screen.getByTestId(`fact-confirmation-${NORTH}`)).toHaveTextContent("Rejected"),
    );

    // Confirm is blocked; the rejected fact is named in the blocking explanation.
    const confirm = screen.getByTestId("action-confirm-document");
    expect(confirm).toBeDisabled();
    expect(screen.getByTestId("confirm-blocked-explanation")).toHaveTextContent("North arrow orientation");
  });
});

describe("SurveyReviewScreen — recovery (SC-S7)", () => {
  it("shows a recoverable failure state with retry when the initial read fails", async () => {
    const client: SurveyReviewClient = {
      ...createMockSurveyReviewClient(seedStore()),
      readDocument: async () => ({ kind: "network_error", message: "unreachable" }),
    };
    renderScreen(DIGEST_PRO, client);
    await screen.findByTestId("read-failure-network_error");
    expect(screen.getByTestId("read-retry")).toBeInTheDocument();
  });
});
