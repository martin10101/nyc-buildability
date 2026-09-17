import type { AddressQuery } from "@/lib/address-api";
import { BOROUGH_NAMES } from "@/lib/contract";
/** Official NYC DCP GeoSearch v2; verified docs and CORS in M5-T029 G1. Suggestions never supply the authoritative BBL. */
export const GEOSEARCH_AUTOCOMPLETE = "https://geosearch.planninglabs.nyc/v2/autocomplete";
/** GeoSearch /search: the explicit action for a complete pasted address. It is
 * the SAME upstream service as autocomplete (docs/), so this is a distinct user
 * action, never an independent-failover source. */
export const GEOSEARCH_SEARCH = "https://geosearch.planninglabs.nyc/v2/search";
export const ADDRESS_SEARCH_TIMEOUT_MS = 6000;
export const ADDRESS_SEARCH_DEBOUNCE_MS = 300;
/** Bounded recovery: at most this many total attempts against a transient
 * source failure (5xx). The per-attempt deadline is never raised — only a fast
 * source-failure is retried; a timeout is terminal (never stacks deadlines). */
export const ADDRESS_SEARCH_MAX_ATTEMPTS = 3;
const ADDRESS_SEARCH_RETRY_BACKOFF_MS = 400;
const MAX_BYTES = 128000;
export interface AddressSuggestion {
    label: string;
    borough: string;
    query: AddressQuery;
}
/** Distinct, non-collapsing failure reasons (handoff §6): a transient source
 * failure (5xx) is `source_unavailable` (retried, bounded); a transport/offline
 * failure is `unavailable`; a rate limit, malformed body, and deadline are their
 * own reasons. The UI must never fold these into one "unavailable" message. */
export type AddressSearchErrorReason =
    | "unavailable"
    | "source_unavailable"
    | "rate_limited"
    | "malformed"
    | "timeout";
export type AddressSearchOutcome = {
    kind: "suggestions";
    suggestions: AddressSuggestion[];
} | {
    kind: "error";
    reason: AddressSearchErrorReason;
} | {
    kind: "aborted";
};
export interface AddressSearchOptions {
    signal?: AbortSignal;
    fetchImpl?: typeof fetch;
    timeoutMs?: number;
    /** Total attempts against a transient 5xx (default ADDRESS_SEARCH_MAX_ATTEMPTS). */
    maxAttempts?: number;
    /** Delay between bounded retries (default ADDRESS_SEARCH_RETRY_BACKOFF_MS). */
    backoffMs?: number;
}
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
/** Delay `ms`, resolving early to "aborted" if the external signal fires. */
function backoff(ms: number, signal?: AbortSignal): Promise<"done" | "aborted"> {
    return new Promise(resolve => {
        if (signal?.aborted) return resolve("aborted");
        const cleanup = () => { clearTimeout(timer); signal?.removeEventListener("abort", onAbort); };
        const onAbort = () => { cleanup(); resolve("aborted"); };
        const timer = setTimeout(() => { cleanup(); resolve("done"); }, ms);
        signal?.addEventListener("abort", onAbort, { once: true });
    });
}

/** One time-bounded attempt against a GeoSearch endpoint. The per-attempt
 * deadline is fixed; a transient 5xx is `source_unavailable`, a transport/
 * offline failure is `unavailable`, and neither is folded into the other. */
async function fetchGeoSearchOnce(endpoint: string, text: string, options: AddressSearchOptions): Promise<AddressSearchOutcome> {
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
            const response = await (options.fetchImpl ?? fetch)(`${endpoint}?text=${encodeURIComponent(text.trim())}`, { signal: controller.signal, credentials: "omit", referrerPolicy: "no-referrer", headers: { Accept: "application/json" } });
            if (response.status === 429)
                return { kind: "error", reason: "rate_limited" };
            if (!response.ok)
                return { kind: "error", reason: "source_unavailable" };
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

/** Bounded recovery: retry ONLY a transient source failure (5xx), at most
 * `maxAttempts` total, with a short backoff. A timeout, rate-limit, malformed
 * body, transport error, or a successful reply returns immediately — so the
 * deadline is never stacked and there is no unbounded retry. */
async function fetchGeoSearchWithRetry(endpoint: string, text: string, options: AddressSearchOptions): Promise<AddressSearchOutcome> {
    if (text.trim().length < 3 || text.length > 200)
        return { kind: "suggestions", suggestions: [] };
    const maxAttempts = Math.max(1, options.maxAttempts ?? ADDRESS_SEARCH_MAX_ATTEMPTS);
    const backoffMs = options.backoffMs ?? ADDRESS_SEARCH_RETRY_BACKOFF_MS;
    let outcome = await fetchGeoSearchOnce(endpoint, text, options);
    for (let attempt = 1; attempt < maxAttempts && outcome.kind === "error" && outcome.reason === "source_unavailable"; attempt++) {
        if (await backoff(backoffMs, options.signal) === "aborted")
            return { kind: "aborted" };
        outcome = await fetchGeoSearchOnce(endpoint, text, options);
    }
    return outcome;
}

/** Autocomplete-while-typing (debounced by the caller). Bounded 5xx recovery. */
export async function fetchAddressSuggestions(text: string, options: AddressSearchOptions = {}): Promise<AddressSearchOutcome> {
    return fetchGeoSearchWithRetry(GEOSEARCH_AUTOCOMPLETE, text, options);
}

/** The explicit full-address action for a complete pasted address the user did
 * not pick from autocomplete. Same upstream service, same bounded recovery, same
 * strict PAD parsing — its candidates still require an explicit user pick. */
export async function fetchAddressSearch(text: string, options: AddressSearchOptions = {}): Promise<AddressSearchOutcome> {
    return fetchGeoSearchWithRetry(GEOSEARCH_SEARCH, text, options);
}
