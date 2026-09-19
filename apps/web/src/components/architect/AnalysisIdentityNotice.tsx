import { CapturedRecord } from "./EvidenceRecord";
/**
 * Analysis identity record (M5-T045, D-073-R006).
 *
 * The ONLY identity distinction the production web contract establishes is the
 * identity the analyst OPENED (`requestedBbl`, from profile.identity.bbl) versus
 * the identity the returned {label} analysis was run for
 * (`document.evaluated_input.bbl`). There is no base-lot/substrate BBL exposed
 * on this contract, so the identifiers are stated NEUTRALLY as entered versus
 * analyzed; no billing-to-base-lot (condo) resolution — or any other
 * relationship — is inferred from the identifiers differing.
 *
 * Records vs allowances: this component only ever shows a RECORD of which
 * identity was analyzed. Calculated allowances live in DevelopmentLimits; when
 * the analyzed identity diverges from (or is absent for) the opened property the
 * allowances are WITHHELD fail-safe and this record says so — an identifier is
 * never presented as a calculated result. A matching identity renders nothing
 * here so the analysis proceeds without noise.
 */
export function AnalysisIdentityNotice({ label, requestedBbl, document }: {
    label: string;
    requestedBbl: string;
    document: {
        evaluated_input: {
            bbl: string | null;
        };
    } | null;
}) {
    if (!document || document.evaluated_input.bbl === requestedBbl)
        return null;
    const analyzedBbl = document.evaluated_input.bbl;
    return <section className="architect-alert" role="alert" data-testid={`analysis-identity-${label.toLowerCase().replace(/\s+/g, "-")}`} data-identity-state={analyzedBbl ? "differs" : "absent"}>
    <strong>
      {label} identity {analyzedBbl ? "mismatch" : "missing"}
    </strong>
    <p>Requested BBL {requestedBbl}; returned BBL {analyzedBbl ?? "not stated"}. Results are withheld from this property.</p>
    <p className="section-note">You opened BBL {requestedBbl}; this {label.toLowerCase()} was analyzed for {analyzedBbl ? `BBL ${analyzedBbl}` : "an unstated identifier"}. The identifiers are recorded as entered versus analyzed only — no relationship between them is inferred — and no calculated allowance is shown while they differ.</p>
    <CapturedRecord value={document} label={`Returned ${label.toLowerCase()} record`}/>
  </section>;
}
