"use client";

import Link from "next/link";
import { rememberAddress } from "@/lib/architect/selected-address";
import type { AddressDocumentOutcome } from "@/lib/address-api";
import { validateBblInput } from "@/lib/bbl";
import { zolaLotUrl } from "@/lib/provenance-link";
import {
  ABSENT_BBL_MAP_LINK_NOTE,
  ZOLA_LOT_LINK_LABEL,
} from "@/components/architect/AddressAutocomplete";
import { Meta } from "./AddressOutcomeCards";
import { LotOutlineMap } from "./LotOutlineMap";

/**
 * The Address Confirm card (task M5-T016, design spec sections 1/2-resolved/
 * 3/4, Packet 2): deliberately THIN — canonical address large, BBL, ZoLa
 * deep-link, lot-outline honesty placeholder, collapsed provenance
 * disclosure, one dominant action. The rich compact property card already
 * exists at ConfirmScreen (step 2) and is reached BY BBL after this gate.
 *
 * THE TWO URL CONTEXTS (the only ones in the address flow) are built
 * EXCLUSIVELY from a canonical BBL that passed the CLIENT re-validation
 * (`validateBblInput`, belt-and-suspenders over the server's normalize_bbl):
 *
 *   - ZoLa: the CONFIRMED `/bbl/<10-digit-bbl>` convenience route
 *     (docs/design/zola-deeplink-url-confirmation.md — verified from the
 *     labs-zola router source + live checks 2026-09-12). DB-005: built ONLY
 *     through the shared validated `zolaLotUrl` helper (constant host+path
 *     prefix + strict canonical-BBL check), which returns null — and renders
 *     NO link — for anything that is not a canonical BBL. ZoLa's SPA answers
 *     200 for any path, so this validation is the only guard.
 *   - The handoff: /property/confirm?bbl=<canonical> (the existing step-2
 *     route contract; ConfirmEntry reads the param on hydration).
 *
 * If the BBL fails re-validation, NO link renders — an honest absence,
 * never a link built from anything the source echoed. Reflected text can
 * therefore never reach an href (packet scenarios S2/S3/S6).
 *
 * Not-verified posture (spec section 4): nothing here is "Verified";
 * source_facts confidence (1.0 = deterministic retrieval) is deliberately
 * absent from the view model and never becomes a badge.
 */

export function AddressConfirmCard({
  outcome,
  onNotMyProperty,
  architect = false,
  typedInput,
}: {
  outcome: AddressDocumentOutcome;
  onNotMyProperty: () => void;
  architect?: boolean;
  /** DB-026: the RAW one-box text the analyst typed before picking an
   * autocomplete suggestion (architect arc). When present it is shown VERBATIM
   * as the entered input, so a picked (city-shaped) suggestion never masquerades
   * as what was typed. Absent on the manual/BBL paths, where the server
   * input_echo IS the verbatim entry. */
  typedInput?: string;
}) {
  const view = outcome.view;
  const validation =
    view.canonical.bbl === null ? null : validateBblInput(view.canonical.bbl);
  const canonicalBbl = validation?.ok ? validation.canonical : null;
  // DB-005: the ZoLa deep-link is built ONLY through the shared validated
  // helper. canonicalBbl already passed validateBblInput, so this is null
  // exactly when there is no canonical BBL — the same gate as before, with
  // no raw template string on this surface.
  const zolaUrl = zolaLotUrl(canonicalBbl);

  const addressLine = [
    [view.inputEcho.houseNumber, view.canonical.streetNameNormalized]
      .filter(Boolean)
      .join(" "),
    view.canonical.boroughName,
  ]
    .filter(Boolean)
    .join(", ");

  // DB-026 identity honesty (D-073-R006 records class): the address the user
  // typed VERBATIM, kept distinct from the city's matched line above so a
  // corner/range/vanity frontage is never silently presented as the input.
  // This is a RECORD — it implies no computed value. The lot's PLUTO
  // address-of-record (which can differ again from the matched frontage) is
  // NOT carried by this Geoclient channel; that gap is a reported discovery,
  // not a built-around field (no server endpoint / contract change here).
  //
  // On the architect autocomplete arc the server input_echo carries the PICKED
  // suggestion's components (already city-shaped), NOT the raw one-box text the
  // analyst typed — so the typed text is threaded in explicitly (`typedInput`)
  // and shown VERBATIM when present. Trimming decides ONLY whether the typed
  // text is blank; the ORIGINAL string is what renders (its surrounding
  // whitespace preserved), so nothing the analyst typed is silently rewritten.
  // The manual/BBL paths pass no typedInput and fall back to input_echo, which
  // IS the verbatim entry there.
  const enteredInput =
    typedInput && typedInput.trim().length > 0
      ? typedInput
      : [
          [view.inputEcho.houseNumber, view.inputEcho.street]
            .filter(Boolean)
            .join(" "),
          view.inputEcho.borough,
          view.inputEcho.zip,
        ]
          .filter(Boolean)
          .join(", ");

  return (
    <section className="card" data-testid="address-confirm-card">
      <h2 className="section-title" tabIndex={-1} data-outcome-heading>
        Is this the right lot?
      </h2>
      {addressLine ? (
        <p
          className="section-title"
          style={{ fontSize: "1.5rem", margin: 0 }}
          data-testid="confirm-address"
        >
          {addressLine}
          {view.canonical.zipCode ? ` ${view.canonical.zipCode}` : ""}
        </p>
      ) : (
        <p className="section-note">
          The city resolved this address but returned no printable
          normalized street — the lot identifier below is the result.
        </p>
      )}

      {enteredInput ? (
        <p className="section-note" data-testid="entered-input">
          You searched for <strong>{enteredInput}</strong>. The address above is
          what the city matched to this lot; the tax lot (BBL) below is the
          identity we carry forward.
        </p>
      ) : null}

      {view.status === "resolved_with_warnings" ? (
        <div
          className="completeness-banner"
          role="status"
          data-testid="address-warnings"
        >
          <p>
            The city resolved this address but attached warnings. They are
            shown exactly as received; they do not block continuing.
          </p>
          {view.grcMessage ? (
            <p data-testid="warning-grc-message">{view.grcMessage}</p>
          ) : null}
          {view.grc2Message ? (
            <p data-testid="warning-grc2-message">{view.grc2Message}</p>
          ) : null}
          <p className="failure-meta">
            Geosupport return codes: <code>{view.grc ?? "none"}</code> /{" "}
            <code>{view.grc2 ?? "none"}</code>
          </p>
        </div>
      ) : null}

      {canonicalBbl ? (
        <p>
          Tax lot (BBL):{" "}
          <code data-testid="resolved-bbl">{canonicalBbl}</code>
          {view.canonical.bin ? (
            <>
              {" "}
              · building (BIN) <code>{view.canonical.bin}</code>
            </>
          ) : null}
        </p>
      ) : (
        <p className="section-note" data-testid="resolved-bbl-absent">
          The city&apos;s answer did not include a lot identifier that passed
          canonical validation, so no BBL is shown and this result cannot
          link onward.
        </p>
      )}

      {zolaUrl ? (
        <p>
          <a
            className="secondary-button"
            href={zolaUrl}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="zola-link"
          >
            {ZOLA_LOT_LINK_LABEL}
          </a>
        </p>
      ) : (
        <p className="section-note" data-testid="zola-link-absent">
          {ABSENT_BBL_MAP_LINK_NOTE}
        </p>
      )}

      {/* M5-T023: the lot-outline surface replaces the Packet-2 placeholder.
          It fetches the display-only EPSG:4326 outline for the re-validated
          canonical BBL and renders honest typed outcomes (outline drawn with
          MapLibre GL JS, honest-empty for condo/no-feature, review posture for
          multiple features, typed fallback on any failure). It mounts ONLY when
          a canonical BBL is present — the same gate as the ZoLa link — so no
          fetch fires for a result that cannot link onward. The whole surface
          already inherits the server-read INTERNAL_RULE_EVAL_ENABLED flag via
          PropertyLookup, so there is no second flag read here. */}
      {canonicalBbl ? <LotOutlineMap bbl={canonicalBbl} context={architect} /> : null}

      <details className="provenance-details" data-testid="address-provenance">
        <summary>Where this came from</summary>
        <div className="provenance-body">
          <p className="failure-meta">
            Official source: {view.provenance.sourceId ?? "not stated"}
            {view.provenance.endpointHost ? (
              <> · endpoint {view.provenance.endpointHost}</>
            ) : null}
            {view.provenance.retrievedAt ? (
              <> · retrieved {view.provenance.retrievedAt}</>
            ) : null}
          </p>
          <p className="failure-meta">
            Geosupport return codes: <code>{view.grc ?? "none"}</code> /{" "}
            <code>{view.grc2 ?? "none"}</code>
          </p>
          {view.provenance.connectorCorrelationId ? (
            <p className="failure-meta">
              Connector reference id (distinct from the HTTP reference id
              below):{" "}
              <code data-testid="connector-correlation-id">
                {view.provenance.connectorCorrelationId}
              </code>
            </p>
          ) : null}
          {view.provenance.responseDigest ? (
            <p className="failure-meta">
              Response digest: <code>{view.provenance.responseDigest}</code>
            </p>
          ) : null}
          {view.provenance.requestParams.length > 0 ? (
            <>
              <p className="failure-meta">Request parameters, as sent:</p>
              <ul className="missing-list" data-testid="request-params">
                {view.provenance.requestParams.map((pair, index) => (
                  <li key={index}>
                    {pair.key}: {pair.value}
                  </li>
                ))}
              </ul>
            </>
          ) : null}
          {view.sourceFacts.length > 0 ? (
            <>
              <p className="failure-meta">
                Source facts (original value → normalized value):
              </p>
              <ul className="missing-list" data-testid="source-facts">
                {view.sourceFacts.map((fact, index) => (
                  <li key={index}>
                    {fact.fieldName}: {fact.originalValue ?? "(absent)"} →{" "}
                    {fact.normalizedValue ?? "(absent)"}
                  </li>
                ))}
              </ul>
            </>
          ) : null}
          {view.sourceFactsNotEmittedReason ? (
            <p className="failure-meta" data-testid="facts-withheld">
              {view.sourceFactsNotEmittedReason}
            </p>
          ) : null}
          <p className="section-note" data-testid="not-verified-posture">
            This is an official address match from the city&apos;s Geoclient
            service, transported exactly as received. It has not been through
            the platform&apos;s rule review.
          </p>
        </div>
      </details>

      {canonicalBbl ? (
        <Link
          className="primary-button next-action-link"
          href={`/property/confirm?bbl=${encodeURIComponent(canonicalBbl)}${architect ? "&ruleeval=on" : ""}`}
          onClick={() => rememberAddress(outcome)}
          data-testid="confirm-continue"
        >
          Continue with this lot
        </Link>
      ) : (
        <p className="section-note" data-testid="confirm-continue-absent">
          Without a valid lot identifier this result cannot continue — use
          the BBL lookup on this page instead.
        </p>
      )}{" "}
      <button
        type="button"
        className="secondary-button"
        onClick={onNotMyProperty}
        data-testid="not-my-property"
      >
        Not my property
      </button>
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}
