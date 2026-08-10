"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ConfirmDocumentPanel } from "./ConfirmDocumentPanel";
import { DocumentOverlay } from "./DocumentOverlay";
import { DownstreamImpact } from "./DownstreamImpact";
import { FactList } from "./FactList";
import { FocusedItem } from "./FocusedItem";
import { ReadFailureState } from "./ReadFailureState";
import { StateHistory } from "./StateHistory";
import { StatusBadge } from "./StatusBadge";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import { useSurveyReviewClient } from "@/lib/surveyReview/context";
import { documentStateDisplay } from "@/lib/surveyReview/labels";
import { canOfferConfirm, openItemCount, orderFactsByUrgency } from "@/lib/surveyReview/model";
import type {
  ActionOutcome,
  CorrectFactRequest,
  ReadDocumentOutcome,
  ReviewDocument,
  ReviewFact,
  ReviewPage,
} from "@/lib/surveyReview/types";

/**
 * Survey review screen (task M2-T016; workflow §3.1, §10). Orchestrates the
 * load / stale / conflict / empty / error states and the per-fact decision loop
 * against the injected `SurveyReviewClient`. It holds NO legal logic: it renders
 * the read-model, forwards decisions to the client, and mirrors the settled
 * read-model the backend returns (deterministic recalculation is the backend's).
 */

const FALLBACK_PAGE: ReviewPage = {
  page_number: 1,
  image_ref: null,
  width: null,
  height: null,
  coordinate_space: null,
};

export function SurveyReviewScreen({ documentId }: { documentId: string }) {
  const client = useSurveyReviewClient();
  const [loading, setLoading] = useState(true);
  const [readOutcome, setReadOutcome] = useState<ReadDocumentOutcome | null>(null);
  const [document, setDocument] = useState<ReviewDocument | null>(null);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [attempt, setAttempt] = useState(0);
  const [announcement, setAnnouncement] = useState("");
  const [recalculating, setRecalculating] = useState(false);
  const requestSeq = useRef(0);
  const outcomeRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const seq = ++requestSeq.current;
    setLoading(true);
    setAnnouncement("");
    void client.readDocument(documentId, { signal: controller.signal }).then((result) => {
      if (requestSeq.current !== seq || result.kind === "aborted") return;
      setLoading(false);
      setReadOutcome(result);
      if (result.kind === "document") {
        setDocument(result.document);
        const ordered = orderFactsByUrgency(result.document.facts);
        setSelectedEvidenceId(ordered[0]?.fact.evidence_id ?? null);
        setPageNumber(result.document.pages[0]?.page_number ?? 1);
        setAnnouncement(
          `Loaded survey document for BBL ${result.document.target_bbl}. Document state: ${documentStateDisplay(result.document.state).label}.`,
        );
      } else {
        setAnnouncement("The survey document could not be loaded.");
      }
    });
    return () => controller.abort();
  }, [client, documentId, attempt]);

  // Move focus to the outcome heading once an outcome arrives (keyboard/SR).
  useEffect(() => {
    if (!loading && readOutcome) {
      outcomeRef.current?.querySelector<HTMLElement>("[data-outcome-heading]")?.focus();
    }
  }, [loading, readOutcome]);

  const applyOutcome = useCallback((outcome: ActionOutcome): ActionOutcome => {
    if (outcome.kind === "updated") {
      setDocument(outcome.document);
      setAnnouncement("Decision recorded. Dependent conclusions were recalculated.");
    } else if (
      outcome.kind === "error" &&
      outcome.reject_code === "stale_history" &&
      outcome.currentDocument
    ) {
      setDocument(outcome.currentDocument);
      setAnnouncement("This item was updated elsewhere; the current state has been reloaded.");
    }
    return outcome;
  }, []);

  const runAction = useCallback(
    async (fn: () => Promise<ActionOutcome>): Promise<ActionOutcome> => {
      setRecalculating(true);
      const outcome = await fn();
      setRecalculating(false);
      return applyOutcome(outcome);
    },
    [applyOutcome],
  );

  const retry = useCallback(() => setAttempt((n) => n + 1), []);

  const selectEvidence = useCallback(
    (evidenceId: string) => {
      setSelectedEvidenceId(evidenceId);
      const fact = document?.facts.find((f) => f.fact.evidence_id === evidenceId);
      if (fact) setPageNumber(fact.fact.page_number);
    },
    [document],
  );

  const selectedFact = useMemo(
    () => document?.facts.find((f) => f.fact.evidence_id === selectedEvidenceId) ?? null,
    [document, selectedEvidenceId],
  );

  return (
    <div data-testid="survey-review-screen">
      <OutcomeAnnouncer message={loading ? "" : announcement} />
      {loading ? (
        <section className="card" data-testid="review-loading" aria-busy="true">
          <h1 className="section-title">Loading survey document…</h1>
          <p className="section-note">
            Retrieving the document, its extracted facts, and any dependent
            buildability conclusions.
          </p>
        </section>
      ) : null}

      <div ref={outcomeRef}>
        {!loading && readOutcome && readOutcome.kind !== "document" ? (
          <ReadFailureState outcome={readOutcome} onRetry={retry} />
        ) : null}

        {!loading && document ? (
          <ReviewBody
            document={document}
            selectedFact={selectedFact}
            selectedEvidenceId={selectedEvidenceId}
            pageNumber={pageNumber}
            recalculating={recalculating}
            onSelectEvidence={selectEvidence}
            onSetPage={setPageNumber}
            onAccept={(evidenceId) =>
              runAction(() => client.acceptFact({ documentId, evidenceId }))
            }
            onCorrect={(req: CorrectFactRequest) =>
              runAction(() => client.correctFact({ ...req, documentId }))
            }
            onRejectFact={(evidenceId, reason) =>
              runAction(() => client.rejectFact({ documentId, evidenceId, reason }))
            }
            onConfirmDocument={() => runAction(() => client.confirmDocument({ documentId }))}
            onRejectDocument={(reason) =>
              runAction(() => client.rejectDocument({ documentId, reason }))
            }
          />
        ) : null}
      </div>
    </div>
  );
}

function ReviewBody({
  document,
  selectedFact,
  selectedEvidenceId,
  pageNumber,
  recalculating,
  onSelectEvidence,
  onSetPage,
  onAccept,
  onCorrect,
  onRejectFact,
  onConfirmDocument,
  onRejectDocument,
}: {
  document: ReviewDocument;
  selectedFact: ReviewFact | null;
  selectedEvidenceId: string | null;
  pageNumber: number;
  recalculating: boolean;
  onSelectEvidence: (evidenceId: string) => void;
  onSetPage: (page: number) => void;
  onAccept: (evidenceId: string) => Promise<ActionOutcome>;
  onCorrect: (req: CorrectFactRequest) => Promise<ActionOutcome>;
  onRejectFact: (evidenceId: string, reason: string) => Promise<ActionOutcome>;
  onConfirmDocument: () => Promise<ActionOutcome>;
  onRejectDocument: (reason: string) => Promise<ActionOutcome>;
}) {
  const stateDisplay = documentStateDisplay(document.state);
  const openItems = openItemCount(document);
  const pages = document.pages.length > 0 ? document.pages : [FALLBACK_PAGE];
  const activePage = pages.find((p) => p.page_number === pageNumber) ?? pages[0];
  const confirmReady = canOfferConfirm(document);

  return (
    <>
      {/* Slim top bar: document identity + layer-A state + dominant action. */}
      <header className="card sr-topbar" data-testid="review-topbar">
        <div className="sr-topbar-main">
          <h1 className="section-title" tabIndex={-1} data-outcome-heading data-testid="review-title">
            {document.title}
          </h1>
          <p className="section-note">
            Target BBL {document.target_bbl} · document {document.document_id}
          </p>
        </div>
        <div className="sr-topbar-status">
          <StatusBadge display={stateDisplay} testId="document-state-badge" />
          {recalculating ? (
            <span className="sr-recalc" role="status" data-testid="recalculating">
              Recalculating dependent conclusions…
            </span>
          ) : null}
        </div>
        <p className="sr-dominant-action section-note" data-testid="dominant-action">
          {openItems > 0
            ? `Next: resolve ${openItems} open item${openItems === 1 ? "" : "s"} (highest priority first).`
            : confirmReady
              ? "Next: confirm or reject the document below."
              : "All material facts are resolved."}
        </p>
      </header>

      {!document.extraction_available ? (
        <section className="card" data-testid="extraction-unavailable-note">
          <p className="section-note">
            Extraction is temporarily unavailable; the document is stored safely
            and unprocessed. It rests in its uploaded state and no extracted
            facts or overlay are shown — nothing is fabricated.
          </p>
        </section>
      ) : null}

      <div className="sr-layout">
        <div className="sr-layout-canvas">
          <DocumentOverlay
            facts={document.facts}
            pageNumber={activePage.page_number}
            imageRef={activePage.image_ref}
            pageWidth={activePage.width}
            pageHeight={activePage.height}
            extractionAvailable={document.extraction_available}
            selectedEvidenceId={selectedEvidenceId}
            onSelect={onSelectEvidence}
          />
          {pages.length > 1 ? (
            <nav className="sr-page-nav" aria-label="Document pages" data-testid="page-nav">
              {pages.map((p) => (
                <button
                  key={p.page_number}
                  type="button"
                  className={`secondary-button${p.page_number === activePage.page_number ? " sr-page-active" : ""}`}
                  onClick={() => onSetPage(p.page_number)}
                  aria-current={p.page_number === activePage.page_number ? "page" : undefined}
                >
                  Page {p.page_number}
                </button>
              ))}
            </nav>
          ) : null}
        </div>

        <div className="sr-layout-decisions">
          <FactList
            facts={document.facts}
            selectedEvidenceId={selectedEvidenceId}
            onSelect={onSelectEvidence}
          />
          {selectedFact ? (
            <FocusedItem
              key={`${selectedFact.fact.evidence_id}:${selectedFact.fact.correction_history.length}:${selectedFact.fact.professional_confirmation.state}`}
              fact={selectedFact}
              capabilities={document.principal.capabilities}
              onAccept={() => onAccept(selectedFact.fact.evidence_id)}
              onCorrect={onCorrect}
              onReject={(reason) => onRejectFact(selectedFact.fact.evidence_id, reason)}
            />
          ) : null}
        </div>
      </div>

      <DownstreamImpact
        downstream={document.downstream}
        facts={document.facts}
        onSelectEvidence={onSelectEvidence}
      />

      <ConfirmDocumentPanel
        document={document}
        onConfirm={onConfirmDocument}
        onRejectDocument={onRejectDocument}
        onSelectEvidence={onSelectEvidence}
      />

      <StateHistory history={document.state_history} />

      <p className="section-note">
        <Link href="/survey/review">Back to the review inbox</Link>
      </p>
    </>
  );
}
