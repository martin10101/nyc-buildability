"use client";

import { useEffect, useMemo, useState } from "react";
import { fetchPropertyProfile, type LookupOutcome } from "@/lib/api";
import { fetchLotGeometry, type LotOutlineOutcome } from "@/lib/lot-geometry-api";

/** City-record reads only: a study choice never requests a rule evaluation. */
export interface ParcelStudyRecord {
  bbl: string;
  profileOutcome: LookupOutcome | null;
  outlineOutcome: LotOutlineOutcome | null;
  loading: boolean;
}

interface RecordSnapshot {
  request: { scope: string; attempt: number };
  records: ParcelStudyRecord[];
}

function matchProfile(bbl: string, outcome: LookupOutcome): LookupOutcome {
  return outcome.kind === "profile" && outcome.profile.identity.bbl !== bbl
    ? {
        kind: "validation_failure",
        correlationId: outcome.correlationId,
        problems: ["Property identity mismatch: the returned profile belongs to another BBL."],
      }
    : outcome;
}

function matchOutline(bbl: string, outcome: LotOutlineOutcome): LotOutlineOutcome {
  return outcome.kind === "document" && outcome.view.bbl !== bbl
    ? {
        kind: "error",
        state: "result_mismatch",
        httpStatus: 200,
        correlationId: outcome.correlationId,
        message: "Parcel identity mismatch: the returned outline does not identify the requested BBL.",
      }
    : outcome;
}

/**
 * Scope and attempt identify every visible snapshot. Old results are hidden
 * during render, before effect cleanup, including an A → B → A scope change.
 * Three parcel workers bound concurrency to six independent read requests.
 * A failed profile does not discard its outline or another parcel's records.
 */
export function useParcelStudyRecords(baseBbls: readonly string[]) {
  const scope = JSON.stringify([...new Set(baseBbls)].sort());
  const [attempt, setAttempt] = useState(0);
  const [snapshot, setSnapshot] = useState<RecordSnapshot | null>(null);
  // Object identity gives A → B → A a new generation, even before effects run.
  const request = useMemo(() => ({ scope, attempt }), [scope, attempt]);
  const emptyRecords = useMemo<ParcelStudyRecord[]>(() => {
    const bbls: string[] = JSON.parse(scope);
    return bbls.map(bbl => ({ bbl, profileOutcome: null, outlineOutcome: null, loading: true }));
  }, [scope]);

  useEffect(() => {
    const controller = new AbortController();
    let next = 0;
    const update = (bbl: string, patch: Partial<ParcelStudyRecord>) => {
      if (controller.signal.aborted) return;
      setSnapshot(previous => {
        if (controller.signal.aborted) return previous;
        const records = previous?.request === request ? previous.records : emptyRecords;
        return {
          request,
          records: records.map(record => {
            if (record.bbl !== bbl) return record;
            const merged = { ...record, ...patch };
            return { ...merged, loading: merged.profileOutcome === null || merged.outlineOutcome === null };
          }),
        };
      });
    };
    async function worker() {
      while (!controller.signal.aborted && next < emptyRecords.length) {
        const { bbl } = emptyRecords[next++];
        const options = { signal: controller.signal };
        await Promise.all([
          fetchPropertyProfile(bbl, options).then(
            outcome => update(bbl, { profileOutcome: matchProfile(bbl, outcome) }),
            () => update(bbl, { profileOutcome: { kind: "network_error", message: "Property records could not be loaded. Retry this study." } }),
          ),
          fetchLotGeometry(bbl, options).then(
            outcome => update(bbl, { outlineOutcome: matchOutline(bbl, outcome) }),
            () => update(bbl, { outlineOutcome: { kind: "network_error", message: "The parcel outline could not be loaded. Retry this study." } }),
          ),
        ]);
      }
    }
    for (let index = 0; index < Math.min(3, emptyRecords.length); index += 1) void worker();
    return () => controller.abort();
  }, [request, emptyRecords]);

  const records = snapshot?.request === request ? snapshot.records : emptyRecords;
  return {
    records,
    loading: records.some(record => record.loading),
    retry: () => setAttempt(value => value + 1),
  };
}
