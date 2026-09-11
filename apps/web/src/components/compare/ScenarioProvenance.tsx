import { Fragment } from "react";
import { boundedText } from "@/lib/bounded";
import { provenanceLeaves } from "@/lib/scenario-display";
import type { Scenario, ScenarioCitation } from "@/lib/scenario-contract";

/**
 * Evaluated-input identity and legal-source provenance for the Compare screen
 * (task M5-T004 rework), converged on the ACCEPTED sibling
 * components/rule-evaluation/RuleEvaluationResult.tsx:76-158: the same collapsed
 * `<details className="provenance-details">` with a `dl` inside a
 * `provenance-body`, the same "not stated" wording for a null identity, and the
 * same citation block shape.
 *
 * WHAT THIS CLOSES
 *
 *   - `evaluated_input` was dropped in FULL — all four required leaves. The
 *     object exists precisely so a consumer can confirm which inputs produced
 *     the scenario without embedding a profile, and `input_fingerprint` is the
 *     only way to pin it to a specific input snapshot (DCV-4, G1-7).
 *   - `cap_provenance.citations` never rendered ANYWHERE in the repo, so the
 *     one material number on the screen — the cap — was surfaced with no
 *     citation at all. The contract's own rule: "a material value may never be
 *     surfaced without it, PRD section 19" (DCV CRITICAL-1, G1-5).
 *   - `contract_version` never rendered (DCV-12).
 *
 * COMPLETENESS OVER CURATION: the sibling renders a chosen subset of each
 * citation's resolved provenance (source, host, retrieved_at). That subset is
 * what dropped `request_url`, `content_digest_sha256`, `raw_html_verified` and
 * `extraction_status` here, so the four NAMED citation fields render explicitly
 * and the open `provenance` object is walked leaf by leaf. Values render as
 * TEXT, never as links: no server string is ever placed in an href.
 */

function CitationBlock({
  citation,
  index,
}: {
  citation: ScenarioCitation;
  index: number;
}) {
  const { leaves, truncated } = provenanceLeaves(citation.provenance);
  return (
    <dl data-testid={`scenario-citation-${index}`}>
      <dt>Snapshot</dt>
      <dd>
        <code>{citation.snapshot_id}</code>
      </dd>
      <dt>Section</dt>
      <dd>{citation.section}</dd>
      <dt>Quote</dt>
      <dd>{citation.quote}</dd>
      <dt>Last amended</dt>
      <dd>
        {typeof citation.last_amended === "string" && citation.last_amended !== ""
          ? citation.last_amended
          : "not stated"}
      </dd>
      {leaves.length === 0 ? (
        <>
          <dt>Source provenance</dt>
          <dd>not stated by the document</dd>
        </>
      ) : (
        leaves.map((leaf) => (
          <Fragment key={leaf.path}>
            <dt>{leaf.path}</dt>
            <dd>{leaf.value}</dd>
          </Fragment>
        ))
      )}
      {truncated ? (
        <>
          <dt>Note</dt>
          <dd>
            This citation&apos;s provenance record is larger than this view
            shows; the omission is stated rather than left silent.
          </dd>
        </>
      ) : null}
    </dl>
  );
}

export function ScenarioProvenance({
  document,
  requestedBbl,
}: {
  document: Scenario;
  requestedBbl: string;
}) {
  const input = document.evaluated_input;
  const evaluatedBbl = input.bbl === null ? null : boundedText(input.bbl, "");
  const citations = document.cap_provenance?.citations ?? [];
  return (
    <section className="card" data-testid="scenario-provenance-section">
      <h2 className="section-title">Evidence for what is shown above</h2>
      <p className="section-note">
        Which inputs produced this scenario, which contract versions they came
        from, and the legal source behind the draft cap. Progressive disclosure:
        the detail is one keystroke away rather than absent.
      </p>
      <details className="provenance-details" data-testid="scenario-provenance">
        <summary>Evaluated input, contract version, and legal-source provenance</summary>
        <div className="provenance-body">
        <dl>
          <dt>Scenario contract version</dt>
          <dd>
            <code data-testid="scenario-contract-version">
              {document.contract_version}
            </code>
          </dd>
          <dt>BBL this document was evaluated for</dt>
          <dd data-testid="scenario-evaluated-bbl">
            {evaluatedBbl === null || evaluatedBbl === "" ? "not stated" : evaluatedBbl}
          </dd>
          <dt>BBL requested by this screen</dt>
          <dd data-testid="scenario-requested-bbl">{requestedBbl}</dd>
          <dt>Property-profile contract version</dt>
          <dd>
            <code>{input.profile_contract_version}</code>
          </dd>
          <dt>Rule-evaluation contract version</dt>
          <dd>
            <code>{input.rule_evaluation_contract_version}</code>
          </dd>
          <dt>Input fingerprint</dt>
          <dd>
            <code data-testid="scenario-input-fingerprint">
              {input.input_fingerprint ?? "not stated"}
            </code>
          </dd>
        </dl>

        <h3 className="section-subtitle">Legal-source citations for the draft cap</h3>
        {document.cap_provenance === null ? (
          <p className="section-note">
            This document attaches no cap provenance, so there is no citation to
            show. There is also no cap: the contract forbids one without it.
          </p>
        ) : citations.length === 0 ? (
          <p className="section-note" data-testid="scenario-citations-empty">
            The cap provenance records NO citations. A material value carrying no
            citation is stated here explicitly rather than shown as a clean,
            empty section.
          </p>
        ) : (
          <div data-testid="scenario-citations">
            <p className="section-note">
              Unverified draft extraction from the official source — not a
              Verified reading of it:
            </p>
            {citations.map((citation, index) => (
              <CitationBlock
                key={`${citation.snapshot_id}-${citation.section}-${index}`}
                citation={citation}
                index={index}
              />
            ))}
          </div>
        )}
        </div>
      </details>
    </section>
  );
}
