"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ConfirmDocumentPanel } from "./ConfirmDocumentPanel";
import { initialDraft, type CorrectionDraft } from "./CorrectionForm";
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
import { dominantAction, orderFactsByUrgency } from "@/lib/surveyReview/model";
import type {
  ActionOutcome,
  CorrectFactRequest,
  FactView,
  ReadDocumentOutcome,
  ReviewDocument,
  ReviewPage,
} from "@/lib/surveyReview/types";

/**
 * Survey review screen (task M2-T016 rework; workflow §3.1, §10). Orchestrates
 * the load / stale / conflict / empty / error states and the per-fact decision
 * loop against the injected `SurveyReviewClient`. Holds NO legal logic: it
 * renders the read-model, forwards decisions, and mirrors the settled read-model
 * the backend returns after each mutation (the client re-reads).
 */

const FALLBACK_PAGE: ReviewPage = {
  page_number: 1,
  image_ref: null,
  width: null,
  height: null,
  coordinate_space: null,
};

export function SurveyReviewScreen({ documentDigest }: { documentDigest: string }) {
  const client = useSurveyReviewClient();
  const [loading, setLoading] = useState(true);
  const [readOutcome, setReadOutcome] = useState<ReadDocumentOutcome | null>(null);
  const [document, setDocument] = useState<ReviewDocument | null>(null);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [attempt, setAttempt] = useState(0);
  const [announcement, setAnnouncement] = useState("");
  const [recalculating, setRecalculating] = useState(false);
  const [affirmed, setAffirmed] = useState<Record<string, string>>({});
  // F3: the correction editor draft is lifted here so it survives a stale reload.
  const [correcting, setCorrecting] = useState(false);
  const [correctionDraft, setCorrectionDraft] = useState<CorrectionDraft>({ value: "", units: "", reason: "" });
  const [staleNotice, setStaleNotice] = useState<string | null>(null);
  const requestSeq = useRef(0);
  const outcomeRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const seq = ++requestSeq.current;
    setLoading(true);
    setAnnouncement("");
    void client.readDocument(documentDigest, { signal: controller.signal }).then((result) => {
      if (requestSeq.current !== seq || result.kind === "aborted") return;
      setLoading(false);
      setReadOutcome(result);
      if (result.kind === "document") {
        setDocument(result.document);
        const ordered = orderFactsByUrgency(result.document.facts);
        setSelectedEvidenceId(ordered[0]?.evidence_id ?? null);
        setPageNumber(result.document.pages[0]?.page_number ?? 1);
        setAnnouncement(
          `Loaded survey document for BBL ${result.document.target_bbl}. Document state: ${documentStateDisplay(result.document.state).label}.`,
        );
      } else {
        setAnnouncement("The survey document could not be loaded.");
      }
    });
    return () => controller.abort();
  }, [client, documentDigest, attempt]);

  useEffect(() => {
    if (!loading && readOutcome) {
      outcomeRef.current?.querySelector<HTMLElement>("[data-outcome-heading]")?.focus();
    }
  }, [loading, readOutcome]);

  const applyUpdated = useCallback((outcome: ActionOutcome): ActionOutcome => {
    if (outcome.kind === "updated") {
      setDocument(outcome.document);
      setAnnouncement("Decision recorded. A recalculation of dependent conclusions was requested.");
    }
    return outcome;
  }, []);

  const runAction = useCallback(
    async (fn: () => Promise<ActionOutcome>): Promise<ActionOutcome> => {
      setRecalculating(true);
      const outcome = await fn();
      setRecalculating(false);
      return applyUpdated(outcome);
    },
    [applyUpdated],
  );

  const retry = useCallback(() => setAttempt((n) => n + 1), []);

  const selectEvidence = useCallback(
    (evidenceId: string) => {
      setSelectedEvidenceId(evidenceId);
      setCorrecting(false);
      setStaleNotice(null);
      const fact = document?.facts.find((f) => f.evidence_id === evidenceId);
      if (fact?.page_number) setPageNumber(fact.page_number);
    },
    [document],
  );

  const selectedFact = useMemo(
    () => document?.facts.find((f) => f.evidence_id === selectedEvidenceId) ?? null,
    [document, selectedEvidenceId],
  );

  const handleAccept = useCallback(
    async (evidenceId: string) => {
      const outcome = await runAction(() => client.acceptFact({ documentDigest, evidenceId }));
      if (outcome.kind === "updated") {
        setAffirmed((prev) => ({ ...prev, [evidenceId]: new Date().toLocaleTimeString() }));
      }
      return outcome;
    },
    [client, documentDigest, runAction],
  );

  const handleCorrect = useCallback(
    async (req: CorrectFactRequest) => {
      const outcome = await runAction(() => client.correctFact({ ...req, documentDigest }));
      if (outcome.kind === "updated") {
        setCorrecting(false);
        setStaleNotice(null);
      } else if (
        outcome.kind === "error" &&
        outcome.reject_code === "concurrent_review_modification" &&
        outcome.currentDocument
      ) {
        // F3: reload fresh state, KEEP the editor open and the draft intact.
        setDocument(outcome.currentDocument);
        setStaleNotice(
          "This item changed while you were editing. The current state is shown; your draft below is preserved — re-apply it.",
        );
      }
      return outcome;
    },
    [client, documentDigest, runAction],
  );

  const startCorrect = useCallback(() => {
    if (selectedFact) {
      setCorrectionDraft(initialDraft(selectedFact));
      setStaleNotice(null);
      setCorrecting(true);
    }
  }, [selectedFact]);

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
            affirmed={affirmed}
            correcting={correcting}
            correctionDraft={correctionDraft}
            staleNotice={staleNotice}
            onSelectEvidence={selectEvidence}
            onSetPage={setPageNumber}
            onStartCorrect={startCorrect}
            onCancelCorrect={() => {
              setCorrecting(false);
              setStaleNotice(null);
            }}
            onDraftChange={setCorrectionDraft}
            onAccept={handleAccept}
            onCorrect={handleCorrect}
            onRejectFact={(evidenceId, reason) =>
              runAction(() => client.rejectFact({ documentDigest, evidenceId, reason }))
            }
            onConfirmDocument={() => runAction(() => client.confirmDocument({ documentDigest }))}
            onRejectDocument={(reason) => runAction(() => client.rejectDocument({ documentDigest, reason }))}
            onReopenDocument={(reason) => runAction(() => client.reopenDocument({ documentDigest, reason }))}
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
  affirmed,
  correcting,
  correctionDraft,
  staleNotice,
  onSelectEvidence,
  onSetPage,
  onStartCorrect,
  onCancelCorrect,
  onDraftChange,
  onAccept,
  onCorrect,
  onRejectFact,
  onConfirmDocument,
  onRejectDocument,
  onReopenDocument,
}: {
  document: ReviewDocument;
  selectedFact: FactView | null;
  selectedEvidenceId: string | null;
  pageNumber: number;
  recalculating: boolean;
  affirmed: Record<string, string>;
  correcting: boolean;
  correctionDraft: CorrectionDraft;
  staleNotice: string | null;
  onSelectEvidence: (evidenceId: string) => void;
  onSetPage: (page: number) => void;
  onStartCorrect: () => void;
  onCancelCorrect: () => void;
  onDraftChange: (draft: CorrectionDraft) => void;
  onAccept: (evidenceId: string) => Promise<ActionOutcome>;
  onCorrect: (req: CorrectFactRequest) => Promise<ActionOutcome>;
  onRejectFact: (evidenceId: string, reason: string) => Promise<ActionOutcome>;
  onConfirmDocument: () => Promise<ActionOutcome>;
  onRejectDocument: (reason: string) => Promise<ActionOutcome>;
  onReopenDocument: (reason: string) => Promise<ActionOutcome>;
}) {
  const stateDisplay = documentStateDisplay(document.state);
  const pages = document.pages.length > 0 ? document.pages : [FALLBACK_PAGE];
  const activePage = pages.find((p) => p.page_number === pageNumber) ?? pages[0];

  return (
    <>
      <header className="card sr-topbar" data-testid="review-topbar">
        <div className="sr-topbar-main">
          <h1 className="section-title" tabIndex={-1} data-outcome-heading data-testid="review-title">
            {document.title}
          </h1>
          <p className="section-note">
            Target BBL {document.target_bbl} · digest {document.document_digest.slice(0, 19)}…
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
          {dominantAction(document)}
        </p>
      </header>

      {!document.extraction_available ? (
        <section className="card" data-testid="extraction-unavailable-note">
          <p className="section-note">
            Extraction is temporarily unavailable; the document is stored safely
            and unprocessed. It rests in its uploaded state and no extracted facts
            or overlay are shown — nothing is fabricated.
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
          <FactList facts={document.facts} selectedEvidenceId={selectedEvidenceId} onSelect={onSelectEvidence} />
          {selectedFact ? (
            <FocusedItem
              key={`${selectedFact.evidence_id}:${selectedFact.correction_history.length}:${selectedFact.confirmation_state}`}
              fact={selectedFact}
              capabilities={document.principal.capabilities}
              documentDigest={document.document_digest}
              originalAvailable={document.original_available}
              affirmedAt={affirmed[selectedFact.evidence_id] ?? null}
              correcting={correcting}
              correctionDraft={correctionDraft}
              staleNotice={staleNotice}
              onStartCorrect={onStartCorrect}
              onCancelCorrect={onCancelCorrect}
              onDraftChange={onDraftChange}
              onAccept={() => onAccept(selectedFact.evidence_id)}
              onCorrect={onCorrect}
              onReject={(reason) => onRejectFact(selectedFact.evidence_id, reason)}
            />
          ) : null}
        </div>
      </div>

      <DownstreamImpact facts={document.facts} onSelectEvidence={onSelectEvidence} />

      <ConfirmDocumentPanel
        document={document}
        onConfirm={onConfirmDocument}
        onRejectDocument={onRejectDocument}
        onReopenDocument={onReopenDocument}
        onSelectEvidence={onSelectEvidence}
      />

      <StateHistory history={document.state_history} />

      <p className="section-note">
        <Link href="/survey/review">Back to the review inbox</Link>
      </p>
    </>
  );
}
