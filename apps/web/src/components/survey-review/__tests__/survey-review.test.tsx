import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { SurveyReviewScreen } from "@/components/survey-review/SurveyReviewScreen";
import { SurveyReviewClientProvider } from "@/lib/surveyReview/context";
import type { ActionOutcome, SurveyReviewClient } from "@/lib/surveyReview/types";
import { createMockSurveyReviewClient, seedStore } from "@/test-support/survey-review/mockClient";

/**
 * Survey review screen component journeys (task M2-T016). Drives the full
 * human journey against the stateful mock backend through the injected client:
 * open a needs_review document → overlay + highlighted conflict → accept /
 * correct / reject → audit trail + downstream recalculation → confirm. Also
 * covers immutability (SC-S2), authorization (SC-S3), no-auto-verified (SC-S4),
 * downstream honesty (SC-S5), conflict-not-dismissible (SC-S6), and recovery
 * (SC-S7).
 */

afterEach(cleanup);

function renderScreen(documentId = "doc-pro", client?: SurveyReviewClient) {
  const resolved = client ?? createMockSurveyReviewClient(seedStore());
  return render(
    <SurveyReviewClientProvider client={resolved}>
      <SurveyReviewScreen documentId={documentId} />
    </SurveyReviewClientProvider>,
  );
}

describe("SurveyReviewScreen — orientation (SC-S1/S4)", () => {
  it("shows the document state, the overlay, and the urgency-ordered fact list", async () => {
    renderScreen();
    await screen.findByTestId("review-topbar");

    // Layer A: document state badge.
    expect(screen.getByTestId("document-state-badge")).toHaveTextContent("Needs review");
    // Overlay marks anchored to the extracted geometry.
    expect(screen.getByTestId("overlay-mark-sev:doc:p1:2")).toBeInTheDocument();
    // The conflict fact is focused first (urgency ordering).
    expect(screen.getByTestId("focused-heading")).toHaveTextContent("Stated lot area");
  });

  it("labels auto-extracted facts as Unconfirmed evidence and never Verified (SC-S4)", async () => {
    renderScreen();
    await screen.findByTestId("review-topbar");
    expect(screen.getByTestId("fact-confirmation-sev:doc:p1:1")).toHaveTextContent(
      "Unconfirmed evidence",
    );
    // No status/label is ever the standalone word "Verified" (honest sentences
    // that mention 'never Verified' are allowed; a Verified STATUS is not).
    expect(screen.queryByText("Verified", { exact: true })).toBeNull();
  });
});

describe("SurveyReviewScreen — correction journey (SC-S1/S2/S5/S6)", () => {
  it("corrects the conflict fact, preserves the immutable original, and clears the downstream flags", async () => {
    renderScreen();
    await screen.findByTestId("focused-item");

    // The area conflict is visible, plain-language, and NOT dismissible.
    expect(screen.getByTestId("check-area_vs_stated")).toHaveTextContent("Conflict");
    expect(screen.getByTestId("conflict-resolve-area_vs_stated")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /dismiss|acknowledge|ignore/i })).toBeNull();

    // Downstream conclusions are blocked / provisional on the conflict.
    expect(screen.getByTestId("downstream-far_max")).toHaveAttribute("data-status", "blocked");
    expect(screen.getByTestId("downstream-lot_coverage")).toHaveAttribute(
      "data-status",
      "provisional",
    );

    // Correct the fact.
    fireEvent.click(screen.getByTestId("action-correct"));
    fireEvent.change(screen.getByTestId("correction-value"), { target: { value: "4800" } });
    fireEvent.change(screen.getByTestId("correction-reason"), {
      target: { value: "OCR misread the stated area digit against the boundary calculation." },
    });
    fireEvent.click(screen.getByTestId("correction-submit"));

    // Audit: the append-only chain now carries the correction with its reason.
    await screen.findByTestId("correction-chain");
    expect(screen.getByTestId("correction-chain")).toHaveTextContent("OCR misread");
    // Immutability: the original detection is preserved, not overwritten.
    expect(screen.getByTestId("original-value")).toHaveTextContent("5,000 SF");
    expect(screen.getByTestId("current-value")).toHaveTextContent("4800");

    // Downstream cleared THROUGH recalculation (not a manual dismiss).
    await waitFor(() =>
      expect(screen.getByTestId("downstream-far_max")).toHaveAttribute("data-status", "cleared"),
    );
    expect(screen.getByTestId("downstream-lot_coverage")).toHaveAttribute("data-status", "cleared");
  });
});

describe("SurveyReviewScreen — reject + confirm journey (SC-S1)", () => {
  it("rejects a detection with a reason and confirms the document after the conflict clears", async () => {
    renderScreen();
    await screen.findByTestId("focused-item");

    // Resolve the conflict first (needed for the H5 confirmation gate).
    fireEvent.click(screen.getByTestId("action-correct"));
    fireEvent.change(screen.getByTestId("correction-value"), { target: { value: "4800" } });
    fireEvent.change(screen.getByTestId("correction-reason"), {
      target: { value: "resolve area conflict" },
    });
    fireEvent.click(screen.getByTestId("correction-submit"));
    await screen.findByTestId("correction-chain");

    // Reject the non-material advisory AI fact.
    fireEvent.click(screen.getByTestId("fact-row-sev:doc:p1:3"));
    fireEvent.click(await screen.findByTestId("action-reject"));
    fireEvent.change(screen.getByTestId("reject-fact-reason"), {
      target: { value: "AI north-arrow guess is not usable." },
    });
    fireEvent.click(screen.getByTestId("reject-fact-submit"));
    await waitFor(() =>
      expect(screen.getByTestId("fact-confirmation-sev:doc:p1:3")).toHaveTextContent("Rejected"),
    );

    // Confirm the document (now that every material fact promotes).
    const confirm = await screen.findByTestId("action-confirm-document");
    await waitFor(() => expect(confirm).not.toBeDisabled());
    fireEvent.click(confirm);

    await waitFor(() =>
      expect(screen.getByTestId("document-state-badge")).toHaveTextContent(
        "Professionally confirmed",
      ),
    );
    expect(screen.getByTestId("confirmed-note")).toBeInTheDocument();
  });
});

describe("SurveyReviewScreen — authorization (SC-S3)", () => {
  it("disables fact actions and the document decision for a read-only consumer", async () => {
    renderScreen("doc-consumer");
    await screen.findByTestId("focused-item");
    expect(screen.getByTestId("action-accept")).toBeDisabled();
    expect(screen.getByTestId("action-correct")).toBeDisabled();
    expect(screen.getByTestId("action-reject")).toBeDisabled();
    expect(screen.getByTestId("action-disabled-reason")).toBeInTheDocument();
    // No confirm control is offered; the reason is stated, not silently hidden.
    expect(screen.queryByTestId("action-confirm-document")).toBeNull();
    expect(screen.getByTestId("confirm-capability-note")).toBeInTheDocument();
  });

  it("lets a preparer correct facts but not confirm the document", async () => {
    renderScreen("doc-user");
    await screen.findByTestId("focused-item");
    expect(screen.getByTestId("action-correct")).not.toBeDisabled();
    expect(screen.queryByTestId("action-confirm-document")).toBeNull();
    expect(screen.getByTestId("confirm-capability-note")).toBeInTheDocument();
  });

  it("offers the confirm control to a professional but blocks it until the H5 gate is met", async () => {
    renderScreen("doc-pro");
    await screen.findByTestId("document-decision");
    const confirm = screen.getByTestId("action-confirm-document");
    expect(confirm).toBeDisabled();
    // Names the exact blocking fact — never silently hidden.
    expect(screen.getByTestId("confirm-blocked-explanation")).toHaveTextContent("Stated lot area");
  });
});

describe("SurveyReviewScreen — recovery (SC-S7)", () => {
  it("shows a recoverable failure state with retry when the initial read fails", async () => {
    const client: SurveyReviewClient = {
      ...createMockSurveyReviewClient(seedStore()),
      readDocument: async () => ({
        kind: "network_error",
        message: "The review service could not be reached.",
      }),
    };
    renderScreen("doc-pro", client);
    await screen.findByTestId("read-failure-network_error");
    expect(screen.getByTestId("read-retry")).toBeInTheDocument();
  });

  it("preserves the reviewer's unsaved correction input when the action fails", async () => {
    const base = createMockSurveyReviewClient(seedStore());
    const client: SurveyReviewClient = {
      ...base,
      correctFact: async (): Promise<ActionOutcome> => ({
        kind: "network_error",
        message: "The review service could not be reached. This action is safe to retry.",
      }),
    };
    renderScreen("doc-pro", client);
    await screen.findByTestId("focused-item");

    fireEvent.click(screen.getByTestId("action-correct"));
    fireEvent.change(screen.getByTestId("correction-value"), { target: { value: "4800" } });
    fireEvent.change(screen.getByTestId("correction-reason"), {
      target: { value: "OCR misread" },
    });
    fireEvent.click(screen.getByTestId("correction-submit"));

    // The failure is stated and the input is re-presented (not lost).
    await screen.findByTestId("correction-error");
    const form = screen.getByTestId("correction-form");
    expect(within(form).getByTestId("correction-value")).toHaveValue("4800");
    expect(within(form).getByTestId("correction-reason")).toHaveValue("OCR misread");
  });
});
