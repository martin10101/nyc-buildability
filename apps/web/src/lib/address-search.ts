import type { AddressQuery } from "@/lib/address-api";
import { BOROUGH_NAMES } from "@/lib/contract";
/** Official NYC DCP GeoSearch v2; verified docs and CORS in M5-T029 G1. Suggestions never supply the authoritative BBL. */
export const GEOSEARCH_AUTOCOMPLETE = "https://geosearch.planninglabs.nyc/v2/autocomplete";
export const ADDRESS_SEARCH_TIMEOUT_MS = 6000;
export const ADDRESS_SEARCH_DEBOUNCE_MS = 300;
const MAX_BYTES = 128000;
export interface AddressSuggestion {
    label: string;
    borough: string;
    query: AddressQuery;
}
export type AddressSearchOutcome = {
    kind: "suggestions";
    suggestions: AddressSuggestion[];
} | {
    kind: "error";
    reason: "unavailable" | "rate_limited" | "malformed" | "timeout";
} | {
    kind: "aborted";
};
function boundedString(value: unknown, max: number): value is string {
    return typeof value === "string" && value.trim().length > 0 && value.length <= max && !/[\u0000-\u001f\u007f]/.test(value);
}
export function parseAddressSuggestions(body: unknown): AddressSuggestion[] | null {
    if (!body || typeof body !== "object")
        return null;
    const data = body as Record<string, unknown>;
    if (data.type !== "FeatureCollection" || !Array.isArray(data.features) || data.features.length > 50)
        return null;
    const suggestions: AddressSuggestion[] = [];
    for (const feature of data.features) {
        if (!feature || typeof feature !== "object" || feature.type !== "Feature" || !feature.properties || typeof feature.properties !== "object")
            return null;
        const p = feature.properties as Record<string, unknown>;
        if (p.source !== "nycpad" || !boundedString(p.housenumber, 64) || !boundedString(p.street, 180) || !boundedString(p.label, 260) || !BOROUGH_NAMES.includes(p.borough as typeof BOROUGH_NAMES[number]))
            continue;
        if (p.postalcode != null && (typeof p.postalcode !== "string" || !/^\d{5}$/.test(p.postalcode)))
            continue;
        suggestions.push({ label: p.label, borough: p.borough as string, query: { houseNumber: p.housenumber, street: p.street, borough: p.borough as string, zip: typeof p.postalcode === "string" ? p.postalcode : null } });
        if (suggestions.length === 8)
            break;
    }
    return suggestions;
}
async function boundedBody(response: Response): Promise<unknown> {
    if (!response.body)
        throw new Error("missing-body");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let text = "";
    let bytes = 0;
    try {
        for (;;) {
            const next = await reader.read();
            if (next.done)
                break;
            bytes += next.value.byteLength;
            if (bytes > MAX_BYTES)
                throw new Error("too-large");
            text += decoder.decode(next.value, { stream: true });
        }
        return JSON.parse(text + decoder.decode());
    }
    finally {
        await reader.cancel().catch(() => undefined);
    }
}
export async function fetchAddressSuggestions(text: string, options: {
    signal?: AbortSignal;
    fetchImpl?: typeof fetch;
    timeoutMs?: number;
} = {}): Promise<AddressSearchOutcome> {
    if (text.trim().length < 3 || text.length > 200)
        return { kind: "suggestions", suggestions: [] };
    if (options.signal?.aborted)
        return { kind: "aborted" };
    const controller = new AbortController();
    let timedOut = false;
    let stop: () => void = () => undefined;
    const cancelled = new Promise<AddressSearchOutcome>(resolve => { stop = () => { controller.abort(); resolve(timedOut ? { kind: "error", reason: "timeout" } : { kind: "aborted" }); }; });
    options.signal?.addEventListener("abort", stop, { once: true });
    const timer = setTimeout(() => { timedOut = true; stop(); }, options.timeoutMs ?? ADDRESS_SEARCH_TIMEOUT_MS);
    const request = (async (): Promise<AddressSearchOutcome> => {
        try {
            const response = await (options.fetchImpl ?? fetch)(`${GEOSEARCH_AUTOCOMPLETE}?text=${encodeURIComponent(text.trim())}`, { signal: controller.signal, credentials: "omit", referrerPolicy: "no-referrer", headers: { Accept: "application/json" } });
            if (response.status === 429)
                return { kind: "error", reason: "rate_limited" };
            if (!response.ok)
                return { kind: "error", reason: "unavailable" };
            if (!response.headers.get("content-type")?.includes("json"))
                return { kind: "error", reason: "malformed" };
            let body: unknown;
            try {
                body = await boundedBody(response);
            }
            catch {
                return { kind: "error", reason: "malformed" };
            }
            const suggestions = parseAddressSuggestions(body);
            return suggestions ? { kind: "suggestions", suggestions } : { kind: "error", reason: "malformed" };
        }
        catch {
            return controller.signal.aborted ? (timedOut ? { kind: "error", reason: "timeout" } : { kind: "aborted" }) : { kind: "error", reason: "unavailable" };
        }
    })();
    try {
        return await Promise.race([request, cancelled]);
    }
    finally {
        clearTimeout(timer);
        options.signal?.removeEventListener("abort", stop);
    }
}
