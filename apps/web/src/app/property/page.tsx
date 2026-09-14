import type { Metadata } from "next";
import { InternalBanner } from "@/components/property/InternalBanner";
import { PropertyLookup } from "@/components/property/PropertyLookup";
import { ruleEvaluationSurfaceEnabled } from "@/lib/rule-evaluation";

export const metadata: Metadata = {
  title: "Property lookup — NYC Buildability (internal)",
};

/**
 * First browser Property screen (task M2-T001; hardened in M2-T002; M4-T005
 * adds the optional draft rule-evaluation surface).
 * INTERNAL/DEV ONLY: the property-profile API has no authentication yet
 * (B-001) and this screen must not be deployed publicly. The PRD section 29
 * disclaimer is rendered by the shared layout footer on every page.
 *
 * This is a Server Component, so it reads the non-public runtime flag
 * INTERNAL_RULE_EVAL_ENABLED once per request (never inlined into the browser
 * bundle) and passes a plain boolean into the client tree. When the flag is
 * off the rule-evaluation surface is never rendered and its fetch is never
 * issued (defense in depth; the endpoint is independently gated). With the
 * flag on, the surface is either explicit opt-in-only (plain `/property`
 * shows just the BBL form; append `?ruleeval=on`), or default-on when the
 * optional INTERNAL_RULE_EVAL_DEFAULT_ON var is set (D-057; plain `/property`
 * shows the full internal flow with no query param). A per-request, PRESENT
 * `?ruleeval` value that is not a true token (e.g. `off`) acts as a fail-safe
 * kill switch in BOTH modes — it always disables the surface, never
 * weakened by the default-on var. See `ruleEvaluationSurfaceEnabled` in
 * `@/lib/rule-evaluation` for the exact decision table.
 */
export default async function PropertyPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  const ruleEvalEnabled = ruleEvaluationSurfaceEnabled({ ruleeval: params.ruleeval });
  return (
    <div className="property-shell">
      <InternalBanner />
      <PropertyLookup ruleEvalEnabled={ruleEvalEnabled} />
    </div>
  );
}
