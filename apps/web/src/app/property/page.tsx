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
 * INTERNAL_RULE_EVAL_UI once per request (never inlined into the browser
 * bundle) and passes a plain boolean into the client tree. When the flag is
 * off the rule-evaluation surface is never rendered and its fetch is never
 * issued (defense in depth; the endpoint is independently gated). A per-request
 * `?ruleeval=off` acts only as a fail-safe kill switch.
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
