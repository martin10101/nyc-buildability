"use client";

import { useEffect, useId, useRef, useState, type ReactNode } from "react";

/**
 * The on-demand detail of one answer (presentation contract §2 item 7 "How was this derived …
 * available on demand", §4 "… details action"; M5-T149 part A). A real button opens a region that
 * holds the answer's other value rows, its conditions, its rule sections and its measurement basis.
 *
 * Focus behaviour (acceptance UX-09): opening moves focus INTO the region; Escape closes it and
 * returns focus to the button. The region stays in the DOM when closed — the `hidden` attribute
 * toggles its visibility — so assistive technology and in-page search still reach the derivation,
 * and the limitation it carries is never dropped from the document, only folded away by default.
 *
 * It renders nothing of its own content: the caller passes the rows/conditions/sections/measurement
 * as children (the website types no number, label, condition or reason — ruling V2).
 */
export function ResultDetails({ name, children }: { name: string; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const regionId = useId();
  const regionRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Focus moves into the region after it becomes visible. Done in an effect keyed on `open`, never
  // synchronously in the click handler, because the region's visibility changes with the state
  // (CODING_RULES: focus a target that a state change reveals from a useEffect).
  useEffect(() => {
    if (open) regionRef.current?.focus();
  }, [open]);

  // Escape returns focus to the button, which is never remounted, so focusing it here is safe.
  const close = () => {
    setOpen(false);
    buttonRef.current?.focus();
  };

  return (
    <div className="ta-details" data-testid="answer-details">
      <button
        ref={buttonRef}
        type="button"
        className="ta-details-button"
        aria-expanded={open}
        aria-controls={regionId}
        // The visible label stays "Details"/"Hide details"; the accessible name carries the result's
        // own name so several disclosures on one screen do not all read "Details" to a screen reader
        // navigating by buttons (rework 4 corrections, W2).
        aria-label={`${open ? "Hide details" : "Details"} — ${name}`}
        data-testid="answer-details-button"
        onClick={() => setOpen(value => !value)}
      >
        {open ? "Hide details" : "Details"}
      </button>
      <div
        ref={regionRef}
        id={regionId}
        className="ta-details-region"
        data-testid="answer-details-region"
        role="group"
        aria-label={`Details — ${name}`}
        tabIndex={-1}
        hidden={!open}
        onKeyDown={event => {
          if (event.key === "Escape") {
            event.stopPropagation();
            close();
          }
        }}
      >
        {children}
      </div>
    </div>
  );
}
