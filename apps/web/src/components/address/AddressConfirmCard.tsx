"use client";

import Link from "next/link";
import type { AddressDocumentOutcome } from "@/lib/address-api";
import { validateBblInput } from "@/lib/bbl";
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
 *     labs-zola router source + live checks 2026-09-12). Host+path is a
 *     module CONSTANT; ZoLa's SPA answers 200 for any path, so this client
 *     validation is the only guard.
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

const ZOLA_BBL_URL_PREFIX = "https://zola.planning.nyc.gov/bbl/";

export function AddressConfirmCard({
  outcome,
  onNotMyProperty,
}: {
  outcome: AddressDocumentOutcome;
  onNotMyProperty: () => void;
}) {
  const view = outcome.view;
  const validation =
    view.canonical.bbl === null ? null : validateBblInput(view.canonical.bbl);
  const canonicalBbl = validation?.ok ? validation.canonical : null;

  const addressLine = [
    [view.inputEcho.houseNumber, view.canonical.streetNameNormalized]
      .filter(Boolean)
      .join(" "),
    view.canonical.boroughName,
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

      {canonicalBbl ? (
        <p>
          <a
            className="secondary-button"
            href={`${ZOLA_BBL_URL_PREFIX}${encodeURIComponent(canonicalBbl)}`}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="zola-link"
          >
            View this lot on the city&apos;s ZoLa map
          </a>
        </p>
      ) : (
        <p className="section-note" data-testid="zola-link-absent">
          The city&apos;s map link needs a valid BBL, which this result did
          not provide.
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
      {canonicalBbl ? <LotOutlineMap bbl={canonicalBbl} /> : null}

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
          href={`/property/confirm?bbl=${encodeURIComponent(canonicalBbl)}`}
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
