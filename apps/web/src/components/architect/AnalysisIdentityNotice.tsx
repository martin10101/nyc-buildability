import { CapturedRecord } from "./EvidenceRecord";
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
    return <section className="architect-alert" role="alert">
    <strong>
      {label} identity {document.evaluated_input.bbl ? "mismatch" : "missing"}
    </strong>
    <p>Requested BBL {requestedBbl}; returned BBL {document.evaluated_input.bbl ?? "not stated"}. Results are withheld from this property.</p>
    <CapturedRecord value={document} label={`Returned ${label.toLowerCase()} record`}/>
  </section>;
}
