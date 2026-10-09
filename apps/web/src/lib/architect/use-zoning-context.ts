"use client";
import { useEffect, useRef, useState } from "react";
import { fetchZoningContext, type ContextBounds, type ZoningContextOutcome } from "./zoning-context";

export function useZoningContext(bounds: ContextBounds, enabled: boolean) {
  const sequence = useRef(0);
  const [result, setResult] = useState<{ bounds: ContextBounds; outcome: ZoningContextOutcome } | null>(null);
  useEffect(() => {
    const current = ++sequence.current;
    if (!enabled) return;
    const controller = new AbortController();
    setResult(null);
    void fetchZoningContext(bounds, controller.signal).then(outcome => {
      if (sequence.current === current && !controller.signal.aborted && outcome.kind !== "aborted") setResult({ bounds, outcome });
    });
    return () => controller.abort();
  }, [bounds, enabled]);
  return enabled && result?.bounds === bounds ? result.outcome : null;
}
