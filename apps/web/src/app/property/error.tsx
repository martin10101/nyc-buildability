"use client";

import Link from "next/link";
import { InternalBanner } from "@/components/property/InternalBanner";

/**
 * Route-level error boundary for /property and every segment under it —
 * /property, /property/confirm, /property/compare (task M5-T004 rework; G5
 * finding 1's reachability note).
 *
 * WHY IT EXISTS. Before this file the ONLY error boundary in the application
 * was under /dashboard; there was none under /property and none at the app
 * root, so any throw while rendering the analysis product blanked the route
 * entirely — a white page with no explanation and no way back. The concrete
 * path G5 traced: `cap_provenance` passed validation as merely "object or
 * null", a non-string field inside it reached React, React threw "Objects are
 * not valid as a React child" AFTER validation had passed, and the route went
 * blank. scenario-contract.ts now type-checks that object field by field so
 * that specific throw cannot happen — but a render boundary is the thing that
 * makes the NEXT unanticipated throw survivable, and the whole point of a
 * fail-safe is that it does not depend on having predicted the fault.
 *
 * HONESTY UNDER FAILURE. This card shows only the opaque `error.digest` —
 * never `error.message`, never a stack — so no internal detail leaks (the
 * dashboard boundary's rule, applied here). It states plainly that nothing was
 * determined and that no value on the failed screen should be relied on, rather
 * than implying the analysis merely needs a refresh.
 */
export default function PropertyError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="property-shell" role="alert">
      <InternalBanner />
      <section className="card failure-state" data-testid="property-error-boundary">
        <h1 className="failure-title">This screen could not be displayed</h1>
        <p>
          Something went wrong while rendering this property screen, and it was
          contained here instead of leaving you with a blank page. Nothing was
          determined, nothing was saved, and no value from the interrupted
          screen should be relied on — a partially rendered analysis is not an
          analysis.
        </p>
        <p className="section-note">
          Official data and the deterministic engine are unaffected by this
          failure; it is a display fault on this screen only.
        </p>
        {error.digest ? (
          <p className="failure-meta">
            Reference id for support and server logs:{" "}
            <code data-testid="property-error-digest">{error.digest}</code>
          </p>
        ) : null}
        <p>
          <button type="button" className="secondary-button" onClick={() => reset()}>
            Try this screen again
          </button>{" "}
          <Link className="next-action-link" href="/property">
            Back to property lookup
          </Link>
        </p>
      </section>
    </div>
  );
}
