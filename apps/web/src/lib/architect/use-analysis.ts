"use client";
import { useEffect, useRef, useState } from "react";
import { fetchScenario, type ScenarioOutcome } from "@/lib/scenario-api";
import { fetchRuleEvaluation, type RuleEvaluationOutcome } from "@/lib/rule-evaluation";
/** Separate bounded operations; retrying one failed document never invalidates the other. */
export function useAnalysis(bbl: string) {
    const [scenario, setScenario] = useState<{
        bbl: string;
        value: ScenarioOutcome;
    } | null>(null);
    const [evaluation, setEvaluation] = useState<{
        bbl: string;
        value: RuleEvaluationOutcome;
    } | null>(null);
    const [scenarioAttempt, setScenarioAttempt] = useState(0);
    const [evaluationAttempt, setEvaluationAttempt] = useState(0);
    const scenarioSeq = useRef(0), evaluationSeq = useRef(0);
    useEffect(() => {
        const current = ++scenarioSeq.current;
        const controller = new AbortController();
        setScenario(null);
        void fetchScenario(bbl, { signal: controller.signal }).then(value => {
            if (scenarioSeq.current === current && !controller.signal.aborted && value.kind !== "aborted")
                setScenario({ bbl, value });
        });
        return () => controller.abort();
    }, [bbl, scenarioAttempt]);
    useEffect(() => {
        const current = ++evaluationSeq.current;
        const controller = new AbortController();
        setEvaluation(null);
        void fetchRuleEvaluation(bbl, { signal: controller.signal }).then(value => {
            if (evaluationSeq.current === current && !controller.signal.aborted && value.kind !== "aborted")
                setEvaluation({ bbl, value });
        });
        return () => controller.abort();
    }, [bbl, evaluationAttempt]);
    return {
        scenario: scenario?.bbl === bbl ? scenario.value : null,
        evaluation: evaluation?.bbl === bbl ? evaluation.value : null,
        retryScenario: () => setScenarioAttempt(value => value + 1),
        retryEvaluation: () => setEvaluationAttempt(value => value + 1),
    };
}
