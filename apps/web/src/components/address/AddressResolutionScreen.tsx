"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";
import { announcementForAddressOutcome } from "@/lib/announce";
import {
  resolveAddress,
  type AddressOutcome,
  type AddressQuery,
} from "@/lib/address-api";
import { AddressAutocomplete } from "@/components/architect/AddressAutocomplete";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import { AddressConfirmCard } from "./AddressConfirmCard";
import {
  AddressClientTimeoutCard,
  AddressErrorCard,
  AddressNetworkErrorCard,
  AddressUnexpectedResponseCard,
  AmbiguousCard,
  NotFoundCard,
  RejectedCard,
  UnrecognizedStatusCard,
} from "./AddressOutcomeCards";
import {
  AddressForm,
  EMPTY_ADDRESS_FORM,
  type AddressFormValues,
} from "./AddressForm";

/**
 * Address entry + resolution outcomes (task M5-T015; Packet-2 routing and
 * card extraction M5-T016). A deliberate near-clone of the PropertyLookup
 * state machine — same AbortController + monotonic requestSeq guard, same
 * [data-outcome-heading] focus move, same retryFocus hand-off to the
 * loading card, same single persistent OutcomeAnnouncer (its own live
 * region via testId, the M4-T005 coexistence pattern).
 *
 * Branching is on `document.status` for the 200 family (never on field
 * presence) and on the typed error state for the non-200 family — both
 * already discriminated and BOUNDED by src/lib/address-api.ts. This screen
 * never calculates, never normalizes an address, never picks a suggestion
 * (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md).
 *
 * M5-T016: `resolved` / `resolved_with_warnings` route to the Address
 * Confirm card ("is this the right lot?") with the ZoLa deep-link and the
 * /property/confirm handoff; "Not my property" returns to entry with the
 * form values retained. The presentation table lives in
 * AddressOutcomeCards.tsx / AddressConfirmCard.tsx (G3 F4 extraction);
 * this file keeps only the machine and the loading card.
 */

interface ResolutionResult {
  query: AddressQuery;
  outcome: AddressOutcome;
}

/** Loading card. LoadingStages is BBL-lookup copy, so the address flow has
 * its own minimal equivalent with the same focus contract: on a retry (or a
 * suggestion pick) the previous card's button unmounts, so this card takes
 * focus rather than letting it drop to <body>. */
function ResolvingCard({ focusOnMount }: { focusOnMount: boolean }) {
  const headingRef = useRef<HTMLHeadingElement | null>(null);
  useEffect(() => {
    if (focusOnMount) headingRef.current?.focus();
  }, [focusOnMount]);
  return (
    <section className="card" aria-busy="true" data-testid="address-resolving">
      <h2 className="section-title" tabIndex={-1} ref={headingRef}>
        Resolving address…
      </h2>
      <p className="section-note">
        Asking the city&apos;s Geoclient service for the official record.
        Nothing is guessed on this side.
      </p>
    </section>
  );
}

export function AddressResolutionScreen({ architect = false }: { architect?: boolean } = {}) {
  const [values, setValues] = useState<AddressFormValues>(EMPTY_ADDRESS_FORM);
  /** Query currently being resolved, or null when nothing is in flight. */
  const [loadingQuery, setLoadingQuery] = useState<AddressQuery | null>(null);
  /** Last completed resolution — survives a later inert submit (D5). */
  const [result, setResult] = useState<ResolutionResult | null>(null);
  /** True only between a Retry/pick activation and its outcome (D1 focus). */
  const [retryFocus, setRetryFocus] = useState(false);
  /** Controls the architect "Enter address manually" disclosure so an
   * autocomplete fallback can OPEN the existing Geoclient resolver; kept in
   * sync with native summary toggles via onToggle. */
  const [manualOpen, setManualOpen] = useState(false);
  /** Bumped on each fallback so the focus effect fires even when the manual
   * resolver was already open. */
  const [manualFocusNonce, setManualFocusNonce] = useState(0);
  // Monotonic id + abort controller: a stale response can never overwrite
  // a newer resolution, and superseded requests are actively cancelled.
  const requestSeq = useRef(0);
  const abortRef = useRef<AbortController | null>(null);
  /** Wraps the rendered outcome; arrival focus queries inside it (D1). */
  const outcomeRef = useRef<HTMLDivElement | null>(null);
  const streetInputRef = useRef<HTMLInputElement | null>(null);
  const autocompleteRef = useRef<HTMLInputElement | null>(null);

  // Cancel any in-flight request on unmount.
  useEffect(() => () => abortRef.current?.abort(), []);

  // After a fallback (nonce bump) the manual resolver is open and rendered;
  // move focus to its street input so the analyst continues without hunting.
  useEffect(() => {
    if (manualFocusNonce > 0) streetInputRef.current?.focus();
  }, [manualFocusNonce]);

  /** [ORCH-CORRECTED per web CI on 3250fbc9] Bumped when returning to entry
   * (Not my property / Edit address). The entry input is remounting during
   * that same update, so a synchronous .focus() in the handler hits a null
   * ref and focus falls to <body>; the effect runs after the entry UI is
   * back in the DOM (same class of fix as manualFocusNonce above). */
  const [entryFocusNonce, setEntryFocusNonce] = useState(0);
  useEffect(() => {
    if (entryFocusNonce > 0)
      (architect ? autocompleteRef : streetInputRef).current?.focus();
  }, [entryFocusNonce, architect]);

  // D1: after an outcome arrives, move focus to the outcome heading.
  // `result` changes ONLY on arrival (an inert submit never calls
  // setResult), so this can never steal focus mid-form-edit.
  useEffect(() => {
    if (result) {
      outcomeRef.current
        ?.querySelector<HTMLElement>("[data-outcome-heading]")
        ?.focus();
    }
  }, [result]);

  const runResolve = useCallback(async (query: AddressQuery) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    const seq = ++requestSeq.current;
    setLoadingQuery(query);
    const outcome = await resolveAddress(query, { signal: controller.signal });
    if (requestSeq.current !== seq || outcome.kind === "aborted") {
      // Superseded: the newer resolution owns the screen.
      return;
    }
    setLoadingQuery(null);
    setRetryFocus(false);
    setResult({ query, outcome });
  }, []);

  const onSubmit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      if (values.houseNumber.trim() === "" && values.street.trim() === "") {
        // The submit button is inert in this state; this guard only makes
        // the same UX nicety deterministic under programmatic submits. It
        // is NOT validation — any non-blank input goes to the connector.
        return;
      }
      void runResolve({
        houseNumber: values.houseNumber,
        street: values.street,
        borough: values.borough === "" ? null : values.borough,
        zip: values.zip === "" ? null : values.zip,
      });
    },
    [values, runResolve],
  );

  const onPickSuggestion = useCallback(
    (rawStreetName: string) => {
      const base = result?.query;
      if (!base) return;
      // The connector's re-query contract: the chosen suggestion's
      // street_name VERBATIM as the new street; same house number, same
      // borough/zip. The form mirrors the pick so what was submitted is
      // visible (and editable) in the street field.
      // G3 F2: the "Use this address" button unmounts with the ambiguous
      // card, so the loading card takes focus — same rule as retry.
      setRetryFocus(true);
      setValues((current) => ({ ...current, street: rawStreetName }));
      void runResolve({ ...base, street: rawStreetName });
    },
    [result, runResolve],
  );

  const retry = useCallback(() => {
    if (result) {
      // D1: the Retry button is about to unmount with the failure card;
      // the loading card takes focus so it never drops to <body>.
      setRetryFocus(true);
      void runResolve(result.query);
    }
  }, [result, runResolve]);

  const editAddress = useCallback(() => {
    setEntryFocusNonce((nonce) => nonce + 1);
  }, []);

  /** M5-T016 "Not my property": back to entry. The result clears (the
   * card unmounts, the announcer goes silent), the FORM VALUES are
   * deliberately RETAINED for editing, and focus returns to the street
   * input. No fetch fires. */
  const notMyProperty = useCallback(() => {
    setResult(null);
    setEntryFocusNonce((nonce) => nonce + 1);
  }, []);

  /** Autocomplete fallback (handoff §6): drop into the EXISTING Geoclient
   * manual resolver with the typed text preserved and VISIBLE, opened and
   * focused. The typed text is a full one-box string, so it seeds the street
   * field alone — never silently combined with a stale house number, borough,
   * or ZIP left over from an earlier pick or edit (those are cleared). */
  const openManualFallback = useCallback((raw: string) => {
    setValues({ ...EMPTY_ADDRESS_FORM, street: raw });
    setManualOpen(true);
    setManualFocusNonce((nonce) => nonce + 1);
  }, []);

  // D1: the single outcome announcement — cleared while resolving so a
  // repeated identical outcome (e.g. retry fails the same way) announces.
  const announcement =
    loadingQuery !== null
      ? ""
      : result
        ? announcementForAddressOutcome(result.outcome)
        : "";

  const renderOutcome = (outcome: AddressOutcome): ReactNode => {
    switch (outcome.kind) {
      case "document":
        switch (outcome.view.status) {
          case "resolved":
          case "resolved_with_warnings":
            return (
              <AddressConfirmCard
                outcome={outcome}
                onNotMyProperty={notMyProperty}
                architect={architect}
              />
            );
          case "ambiguous":
            return <AmbiguousCard outcome={outcome} onPick={onPickSuggestion} />;
          case "not_found":
            return <NotFoundCard outcome={outcome} onEditAddress={editAddress} />;
          case "rejected":
            return <RejectedCard outcome={outcome} onEditAddress={editAddress} />;
          default:
            return <UnrecognizedStatusCard outcome={outcome} onRetry={retry} />;
        }
      case "error":
        return (
          <AddressErrorCard
            outcome={outcome}
            onRetry={retry}
            onEditAddress={editAddress}
          />
        );
      case "network_error":
        return (
          <AddressNetworkErrorCard message={outcome.message} onRetry={retry} />
        );
      case "client_timeout":
        return (
          <AddressClientTimeoutCard
            timeoutMs={outcome.timeoutMs}
            onRetry={retry}
          />
        );
      case "unexpected_response":
        return (
          <AddressUnexpectedResponseCard
            httpStatus={outcome.httpStatus}
            receivedState={outcome.receivedState}
            correlationId={outcome.correlationId}
            onRetry={retry}
          />
        );
      case "aborted":
        // A superseded request has no user-visible meaning.
        return null;
    }
  };

  return (
    <div data-testid="address-resolution-screen">
      <OutcomeAnnouncer message={announcement} testId="address-outcome-announcer" />
      <section className="card">
        {/* h1: the address surface is the page's primary lookup whenever it
            is mounted (G3 F1 — the document outline must not open on an h2;
            PropertyLookup demotes its own heading when the flag is on). */}
        <h1 className="section-title" style={{ fontSize: "1.4rem" }}>
          {architect ? "Find a property" : "Address lookup"}
        </h1>
        <p className="section-note">{architect ? "Search an address, then confirm the official lot match." : "Enter a street address for the city’s official Geoclient lot match."}</p>
        {architect ? <AddressAutocomplete inputRef={autocompleteRef} onPick={query => {
          setValues({ houseNumber: query.houseNumber, street: query.street, borough: query.borough ?? "", zip: query.zip ?? "" });
          void runResolve(query);
        }} onEdit={() => { ++requestSeq.current; abortRef.current?.abort(); setLoadingQuery(null); setResult(null); }} onFallback={openManualFallback} /> : null}
        {architect ? <details className="provenance-details" open={manualOpen} onToggle={event => setManualOpen((event.currentTarget as HTMLDetailsElement).open)}><summary>Enter address manually</summary><AddressForm values={values} onChange={setValues} onSubmit={onSubmit} streetInputRef={streetInputRef} /></details> : <AddressForm values={values} onChange={setValues} onSubmit={onSubmit} streetInputRef={streetInputRef} />}
      </section>

      {loadingQuery !== null ? <ResolvingCard focusOnMount={retryFocus} /> : null}

      <div ref={outcomeRef}>
        {loadingQuery === null && result ? renderOutcome(result.outcome) : null}
      </div>
    </div>
  );
}
