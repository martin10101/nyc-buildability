import { CapturedRecord } from "./EvidenceRecord";
/**
 * Analysis identity record (M5-T045, D-073-R006; substitution branch M5-T058).
 *
 * The identity distinction the production web contract establishes is the
 * identity the analyst OPENED (`requestedBbl`, from profile.identity.bbl) versus
 * the identity the returned {label} analysis was run for
 * (`document.evaluated_input.bbl`). When those differ with NO corresponding
 * substitution stamp the identifiers are stated NEUTRALLY as entered versus
 * analyzed and results are WITHHELD fail-safe; no billing-to-base-lot (condo)
 * resolution — or any other relationship — is inferred from the identifiers
 * differing.
 *
 * M5-T058 adds ONE legitimate exception: a rule_evaluation document that carries
 * the additive `substrate_substitution` stamp (contract 1.2.0) records that the
 * entered condo BILLING lot was legitimately analyzed on its single resolved
 * base tax lot. When the stamp CORRESPONDS to the identities on screen (its
 * entered_bbl is the opened property and equals evaluated_input.bbl, and its
 * analyzed_bbl is a real, different base lot) the notice renders a legitimate
 * "analyzed on base lot" record INSTEAD of the withhold alert (DB-036(d)
 * closure). A stamp that does NOT correspond is ignored, so the fail-safe
 * withhold guard still governs — the guard is closed by ADDING a stamped branch,
 * never by relaxing the unstamped path.
 *
 * Records vs allowances: this component only ever shows a RECORD of which
 * identity was analyzed (entered, analyzed, or the entered-versus-analyzed-base
 * substitution). Calculated allowances live in DevelopmentLimits; an identifier
 * is never presented as a calculated result. A matching identity with no
 * substitution renders nothing here so the analysis proceeds without noise.
 */
export function AnalysisIdentityNotice({ label, requestedBbl, document }: {
    label: string;
    requestedBbl: string;
    document: {
        evaluated_input: {
            bbl: string | null;
        };
        substrate_substitution?: {
            entered_bbl?: string | null;
            analyzed_bbl?: string | null;
        } | null;
    } | null;
}) {
    if (!document)
        return null;
    const analyzedBbl = document.evaluated_input.bbl;
    const substitution = document.substrate_substitution ?? null;
    // A substrate_substitution stamp legitimizes analyzing a condo billing lot on
    // its resolved base lot ONLY when it corresponds to the identities on screen:
    // its entered_bbl is the opened property AND the value evaluated_input.bbl
    // reports (the backend keeps evaluated_input.bbl the entered billing BBL), and
    // its analyzed_bbl is a real, DIFFERENT base lot. A non-corresponding stamp is
    // ignored and the withhold guard below still governs.
    const stampLegitimate =
        !!substitution &&
        typeof substitution.entered_bbl === "string" &&
        substitution.entered_bbl === requestedBbl &&
        substitution.entered_bbl === analyzedBbl &&
        typeof substitution.analyzed_bbl === "string" &&
        substitution.analyzed_bbl.length > 0 &&
        substitution.analyzed_bbl !== substitution.entered_bbl;
    if (stampLegitimate) {
        const analyzedBase = substitution!.analyzed_bbl as string;
        return <section className="architect-note" data-testid={`analysis-identity-substitution-${label.toLowerCase().replace(/\s+/g, "-")}`} data-identity-state="substituted">
      <strong>{label} analyzed on the base lot</strong>
      <p>You entered BBL {requestedBbl}, a condo billing lot (the single tax lot a condo is billed under); this {label.toLowerCase()} was analyzed on the recorded base tax lot BBL {analyzedBase} — the land parcel the city records as this condo&rsquo;s base. The billing lot and the base lot are recorded as entered versus analyzed — a city record of the documented resolution, not a computed allowance.</p>
      <CapturedRecord value={document} label={`Returned ${label.toLowerCase()} record`}/>
    </section>;
    }
    if (analyzedBbl === requestedBbl)
        return null;
    return <section className="architect-alert" role="alert" data-testid={`analysis-identity-${label.toLowerCase().replace(/\s+/g, "-")}`} data-identity-state={analyzedBbl ? "differs" : "absent"}>
    <strong>
      {label} identity {analyzedBbl ? "mismatch" : "missing"}
    </strong>
    <p>Requested BBL {requestedBbl}; returned BBL {analyzedBbl ?? "not stated"}. Results are withheld from this property.</p>
    <p className="section-note">You opened BBL {requestedBbl}; this {label.toLowerCase()} was analyzed for {analyzedBbl ? `BBL ${analyzedBbl}` : "an unstated identifier"}. The identifiers are recorded as entered versus analyzed only — no relationship between them is inferred — and no calculated allowance is shown while they differ.</p>
    <CapturedRecord value={document} label={`Returned ${label.toLowerCase()} record`}/>
  </section>;
}
