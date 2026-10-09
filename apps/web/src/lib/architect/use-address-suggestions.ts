"use client";
import { useEffect, useRef, useState } from "react";
import { ADDRESS_SEARCH_DEBOUNCE_MS, fetchAddressSuggestions, type AddressSearchOutcome } from "@/lib/address-search";

/** Last typed query owns suggestions; selection, edit and unmount cancel prior work. */
export function useAddressSuggestions(query: string, selected: boolean) {
  const sequence = useRef(0);
  const [result, setResult] = useState<{ query: string; outcome: AddressSearchOutcome } | null>(null);
  const [pending, setPending] = useState<string | null>(null);
  useEffect(() => {
    const seq = ++sequence.current;
    if (selected || query.trim().length < 3) return;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      setPending(query);
      void fetchAddressSuggestions(query, { signal: controller.signal }).then(outcome => {
        if (seq !== sequence.current || controller.signal.aborted || outcome.kind === "aborted") return;
        setResult({ query, outcome });
        setPending(null);
      });
    }, ADDRESS_SEARCH_DEBOUNCE_MS);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [query, selected]);
  return { outcome: !selected && result?.query === query ? result.outcome : null, loading: !selected && pending === query };
}
