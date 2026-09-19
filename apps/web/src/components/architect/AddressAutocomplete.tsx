"use client";
import { useEffect, useRef, useState, type RefObject } from "react";
import type { AddressQuery } from "@/lib/address-api";
import {
    fetchAddressSearch,
    type AddressSearchErrorReason,
    type AddressSearchOutcome,
    type AddressSuggestion,
} from "@/lib/address-search";
import { useAddressSuggestions } from "@/lib/architect/use-address-suggestions";

/** The label of the explicit full-address action. DB-009: exported as the
 * SINGLE source of truth for both the button below and the failure copy that
 * names it, so the copy and the affordance it points at cannot drift apart
 * silently (one shared string, asserted by the tests). */
export const FULL_ADDRESS_SEARCH_LABEL = "Search this full address";

/** DB-024(b): the single shared "no canonical BBL, so no city-map link" note.
 * AddressConfirmCard, PropertyOverview, and ZoningContextPanel render it
 * BYTE-IDENTICALLY from here so the three honest-absence notes cannot drift into
 * three near-duplicate literals (the same single-source-of-truth discipline as
 * FULL_ADDRESS_SEARCH_LABEL; asserted via this import in the tests). */
export const ABSENT_BBL_MAP_LINK_NOTE =
    "The city map link needs a valid BBL, which this lot did not provide.";

/** DB-024(d): one accessible name for every ZoLa lot-map link — the
 * AddressConfirmCard action, the PropertyOverview site-context link, and the
 * ZoningContextPanel link. Reading identically to assistive tech instead of
 * drifting between "Open ZoLa", "Open in ZoLa", and a longer sentence. The
 * validated zolaLotUrl helper is untouched; this is presentation only. */
export const ZOLA_LOT_LINK_LABEL = "Open ZoLa";

/** Distinct, non-collapsing copy per failure reason (handoff §6): the old UI
 * folded timeout, source failure, and transport error into one "unavailable"
 * line. Each reason now reads differently and points at a real next step.
 * DB-006: `rejected` (a 4xx the service will not accept) is its own honest,
 * non-retry line. DB-009: the reasons that still render the full-address button
 * name it by its exact label via FULL_ADDRESS_SEARCH_LABEL. */
const ERROR_MESSAGES: Record<AddressSearchErrorReason, string> = {
    rate_limited: `Address suggestions are rate-limited right now. Wait a moment, then use the “${FULL_ADDRESS_SEARCH_LABEL}” button below, or use manual entry or BBL.`,
    timeout: `The city’s address service is taking too long to suggest. Use the “${FULL_ADDRESS_SEARCH_LABEL}” button below, or use manual entry or BBL.`,
    source_unavailable: `The city’s address service is temporarily unavailable. Use the “${FULL_ADDRESS_SEARCH_LABEL}” button below, or use manual entry or BBL.`,
    rejected: `The city’s address service didn’t accept that search. Use the “${FULL_ADDRESS_SEARCH_LABEL}” button below, or use manual entry or BBL.`,
    unavailable: `Couldn’t reach the city’s address service. Check your connection, then use the “${FULL_ADDRESS_SEARCH_LABEL}” button below, or use manual entry or BBL.`,
    malformed: `The city’s address service returned a response we can’t read safely. Use the “${FULL_ADDRESS_SEARCH_LABEL}” button below, or use manual entry or BBL.`,
};

/** DB-024(a): copy for when the EXPLICIT full-address search ITSELF fails. The
 * ERROR_MESSAGES above point back at the “${FULL_ADDRESS_SEARCH_LABEL}” button —
 * which is CIRCULAR here, because the user just watched that exact search fail.
 * These never name the just-failed search; they point at genuinely different
 * next steps (the prefilled manual-entry recovery below, or the BBL lookup). */
const FULL_SEARCH_ERROR_MESSAGES: Record<AddressSearchErrorReason, string> = {
    rate_limited: `The full-address search is rate-limited right now. Use manual entry with this address below, or the BBL lookup.`,
    timeout: `The full-address search is taking too long. Use manual entry with this address below, or the BBL lookup.`,
    source_unavailable: `The city’s address service is temporarily unavailable. Use manual entry with this address below, or the BBL lookup.`,
    rejected: `The city’s address service didn’t accept that search. Use manual entry with this address below, or the BBL lookup.`,
    unavailable: `Couldn’t reach the city’s address service. Check your connection, then use manual entry with this address below, or the BBL lookup.`,
    malformed: `The full-address search returned a response we can’t read safely. Use manual entry with this address below, or the BBL lookup.`,
};

export function AddressAutocomplete({ onPick, onEdit, onFallback, inputRef }: {
    /** The picked suggestion's structured query PLUS the raw one-box text the
     * analyst typed before picking. DB-026: the caller carries the typed text to
     * the confirm surface so a city-shaped picked suggestion never masquerades as
     * the verbatim entered input (the picked query re-resolves through Geoclient,
     * which echoes the picked components, not the raw text). */
    onPick: (query: AddressQuery, typedText: string) => void;
    onEdit: () => void;
    /** Hand the preserved typed text to the manual/Geoclient fallback so it is
     * prefilled, never retyped (handoff §6). Optional so callers can opt out. */
    onFallback?: (text: string) => void;
    inputRef: RefObject<HTMLInputElement | null>;
}) {
    const [text, setText] = useState("");
    const [open, setOpen] = useState(false);
    const [active, setActive] = useState(-1);
    const [selected, setSelected] = useState(false);
    const [searching, setSearching] = useState(false);
    /** Result of an EXPLICIT full-address /search, valid only while its query
     * still equals the current text (a stale full search never displays). */
    const [searchResult, setSearchResult] = useState<{ query: string; outcome: AddressSearchOutcome } | null>(null);
    const { outcome: typedOutcome, loading } = useAddressSuggestions(text, selected);
    /** Monotonic id + abort controller for the EXPLICIT /search, mirroring the
     * suggestion hook's guard: a superseded response can never apply (the seq
     * check) and its transport is actively cancelled (the controller). Editing,
     * picking a candidate, and unmount all supersede an in-flight full search. */
    const fullSearchSeq = useRef(0);
    const fullSearchAbort = useRef<AbortController | null>(null);

    // Cancel any in-flight explicit full-address search on unmount.
    useEffect(() => () => fullSearchAbort.current?.abort(), []);

    /** Supersede an in-flight full search: abort its transport, retire its
     * sequence so a late reply is dropped, and clear `searching` so a NEW
     * query can search immediately (never blocked behind an abandoned request). */
    const cancelFullSearch = () => {
        fullSearchAbort.current?.abort();
        fullSearchAbort.current = null;
        fullSearchSeq.current += 1;
        setSearching(false);
    };

    const fullSearchActive = searchResult !== null && searchResult.query === text;
    const outcome: AddressSearchOutcome | null = fullSearchActive ? searchResult!.outcome : typedOutcome;
    const suggestions = outcome?.kind === "suggestions" ? outcome.suggestions : [];
    const trimmedLength = text.trim().length;
    const incomplete = trimmedLength > 0 && trimmedLength < 3;

    const choose = (item: AddressSuggestion) => {
        // Selecting a candidate supersedes any full search still in flight.
        cancelFullSearch();
        // `text` is the raw one-box string as typed, captured BEFORE setText
        // rewrites the field to the picked label — that raw text is what the
        // confirm surface shows verbatim (DB-026 identity honesty).
        onPick(item.query, text);
        setText(`${item.query.houseNumber} ${item.query.street}, ${item.borough}`);
        setSelected(true);
        setOpen(false);
    };

    /** The explicit /search action for a complete pasted address (never
     * auto-accepts a candidate — the picked one still routes to confirmation).
     * Request-generation + abort protected: only the newest search applies, and
     * a superseded reply (edit / selection / unmount) is dropped, not rendered. */
    const runFullSearch = () => {
        const query = text;
        if (query.trim().length < 3 || searching) return;
        fullSearchAbort.current?.abort();
        const controller = new AbortController();
        fullSearchAbort.current = controller;
        const seq = ++fullSearchSeq.current;
        setSearching(true);
        setOpen(true);
        setActive(-1);
        void fetchAddressSearch(query, { signal: controller.signal }).then(result => {
            // Only the newest, un-aborted search may touch the screen.
            if (seq !== fullSearchSeq.current || result.kind === "aborted") return;
            setSearching(false);
            setSearchResult({ query, outcome: result });
            if (result.kind === "suggestions" && result.suggestions.length) setOpen(true);
        });
    };

    // The autocomplete could not offer a usable pick: surface the explicit
    // full-address action and the prefilled manual/Geoclient fallback.
    const stalled =
        outcome?.kind === "error" ||
        (outcome?.kind === "suggestions" && suggestions.length === 0 && trimmedLength >= 3);
    const offerRecovery = stalled && !selected && !searching;

    const statusMessage = searching
        ? "Searching the city’s full address service…"
        : loading
            ? "Searching official NYC addresses…"
            : incomplete
                ? "Keep typing the full address (at least 3 characters)."
                : outcome?.kind === "error"
                    ? (fullSearchActive ? FULL_SEARCH_ERROR_MESSAGES : ERROR_MESSAGES)[outcome.reason]
                    : outcome?.kind === "suggestions"
                        ? suggestions.length && open
                            ? `${suggestions.length} address suggestions. Use arrow keys to choose, then Enter.`
                            : suggestions.length === 0 && trimmedLength >= 3
                                ? "No matching address found in the city’s records. Search the full address, or use manual entry or BBL below."
                                : ""
                        : "";

    return <div className="architect-autocomplete">
    <label className="field-label" htmlFor="architect-address">Street address</label>
    <input id="architect-address" ref={inputRef} className="text-input architect-search-input" role="combobox" aria-autocomplete="list" aria-expanded={open && suggestions.length > 0} aria-controls="architect-address-options" aria-activedescendant={open && active >= 0 ? `address-option-${active}` : undefined} aria-describedby="architect-address-hint" autoComplete="off" placeholder="Enter a New York City address" maxLength={200} value={text} onChange={event => { setText(event.target.value); setSelected(false); setActive(-1); setOpen(true); setSearchResult(null); cancelFullSearch(); onEdit(); }} onKeyDown={event => {
            if (event.key === "Escape") {
                setOpen(false);
                setActive(-1);
            }
            if (event.key === "ArrowDown" && suggestions.length) {
                event.preventDefault();
                setOpen(true);
                setActive(index => (index + 1) % suggestions.length);
            }
            if (event.key === "ArrowUp" && suggestions.length) {
                event.preventDefault();
                setOpen(true);
                setActive(index => (index <= 0 ? suggestions.length - 1 : index - 1));
            }
            if (event.key === "Enter") {
                event.preventDefault();
                if (open && active >= 0 && suggestions[active])
                    choose(suggestions[active]);
                else if (trimmedLength >= 3)
                    // No highlighted suggestion: run the explicit /search — never
                    // silently accept the first approximate match as the lot.
                    runFullSearch();
            }
        }} onBlur={() => setOpen(false)} onFocus={() => { if (!selected && suggestions.length)
        setOpen(true); }}/>
    {open && suggestions.length ? <ul id="architect-address-options" role="listbox" aria-label="Official NYC address suggestions" className="architect-suggestions">
      {suggestions.map((item, index) => <li key={`${item.label}-${index}`} id={`address-option-${index}`} role="option" aria-selected={active === index} onMouseDown={event => event.preventDefault()} onClick={() => choose(item)}>
        <strong>
          {item.query.houseNumber} {item.query.street}
        </strong>
        <span>
          {item.borough}
          {item.query.zip ? ` · ${item.query.zip}` : ""}
        </span>
      </li>)}
    </ul> : <ul id="architect-address-options" role="listbox" aria-label="Official NYC address suggestions" hidden/>}
    <p id="architect-address-hint" className="section-note">All five boroughs · <a href="https://geosearch.planninglabs.nyc/docs/" target="_blank" rel="noopener noreferrer">NYC Planning address suggestions <span aria-hidden="true">↗</span></a>
    </p>
    {trimmedLength >= 3 && !selected ? <div className="architect-search-actions">
      <button type="button" className="secondary-button" data-testid="full-address-search" onClick={runFullSearch} disabled={searching}>
        {FULL_ADDRESS_SEARCH_LABEL}
      </button>
      {offerRecovery && onFallback ? <button type="button" className="secondary-button" data-testid="use-manual-entry" onClick={() => onFallback(text)}>
        Use manual entry with this address
      </button> : null}
    </div> : null}
    <p className="architect-search-status" role="status">
      {statusMessage}
    </p>
  </div>;
}
