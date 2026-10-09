import type { Scenario } from "@/lib/scenario-contract";

/**
 * The engine's own `reasons`, rendered on EVERY branch (task M5-T004 rework).
 *
 * Before the rework this list existed only inside NoScenarioBlock, so a
 * PRELIMINARY document — the only kind that shows a number — dropped it
 * entirely, and the client substituted hard-coded prose that happened to say
 * something similar today and could never track the server (G1-2, G3-2, G4-4,
 * DCV-10). The preliminary fixture's single reason is load-bearing: it states
 * that the cap came from the ZR 23-21 trace VERBATIM and is NOT a buildable
 * envelope. Any reason the backend adds later — a substituted input, a narrowed
 * applicability — now reaches the screen without a UI change.
 *
 * An EMPTY `reasons` array is stated explicitly. "No reasons were recorded" and
 * "we did not show you the reasons" look identical when the answer is silence,
 * and only one of them is honest.
 */
export function ScenarioReasons({ document }: { document: Scenario }) {
  return (
    <section className="card" data-testid="scenario-reasons-section">
      <h2 className="section-title">What the engine recorded about this result</h2>
      <p className="section-note">
        These sentences come from the deterministic engine itself and are shown
        verbatim — they are not this screen&apos;s summary of them.
      </p>
      {document.reasons.length === 0 ? (
        <p className="section-note" data-testid="scenario-reasons-empty">
          The scenario document records no reasons for this result. That is the
          document&apos;s own state, stated here rather than left blank.
        </p>
      ) : (
        <ul className="missing-list" data-testid="scenario-reasons">
          {document.reasons.map((reason, index) => (
            <li key={`reason-${index}`}>{reason}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
