import type { Metadata } from "next";
import { InternalBanner } from "@/components/property/InternalBanner";
import { PropertyLookup } from "@/components/property/PropertyLookup";
import { ruleEvaluationSurfaceEnabled } from "@/lib/rule-evaluation";
import { scenarioSurfaceEnabled } from "@/lib/scenario";

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
 *
 * M5-T002 adds an independent draft scenario surface the same way: the Server
 * Component reads the non-public runtime flag INTERNAL_SCENARIO_UI once per
 * request and passes a plain boolean into the client tree. When off the scenario
 * surface is never rendered and its fetch is never issued; `?scenario=off` acts
 * only as a fail-safe kill switch. The two surfaces are gated independently.
 */
export default async function PropertyPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  const ruleEvalEnabled = ruleEvaluationSurfaceEnabled({ ruleeval: params.ruleeval });
  const scenarioEnabled = scenarioSurfaceEnabled({ scenario: params.scenario });
  return (
    <div className="property-shell">
      <InternalBanner />
      <PropertyLookup ruleEvalEnabled={ruleEvalEnabled} scenarioEnabled={scenarioEnabled} />
    </div>
  );
}
