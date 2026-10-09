"use client";
import { useEffect, useRef, useState } from "react";
import { fetchPropertyProfile, type LookupOutcome } from "@/lib/api";
/** Last-issued request wins; a property change clears the old profile immediately. */
export function useProperty(bbl: string | null) {
    const [result, setResult] = useState<{
        bbl: string;
        outcome: LookupOutcome;
    } | null>(null);
    const [pending, setPending] = useState(false);
    const [attempt, setAttempt] = useState(0);
    const seq = useRef(0);
    useEffect(() => {
        const current = ++seq.current;
        if (!bbl)
            return;
        const controller = new AbortController();
        setPending(true);
        void fetchPropertyProfile(bbl, { signal: controller.signal }).then(outcome => {
            if (seq.current !== current || controller.signal.aborted || outcome.kind === "aborted")
                return;
            setResult({ bbl, outcome });
            setPending(false);
        });
        return () => controller.abort();
    }, [bbl, attempt]);
    return {
        loading: !!bbl && (pending || result?.bbl !== bbl),
        outcome: result?.bbl === bbl && !pending ? result.outcome : null,
        retry: () => setAttempt(value => value + 1),
    };
}
