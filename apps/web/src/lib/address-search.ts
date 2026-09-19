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
 * failure (>= 500) is `source_unavailable` (retried, bounded); a client-side
 * refusal (any other 4xx/non-2xx, e.g. 404/422) is `rejected` (NEVER retried —
 * retrying cannot change a request the service will not accept); a transport/
 * offline failure is `unavailable`; a rate limit (429), malformed body, and
 * deadline are their own reasons. The UI must never fold these into one
 * "unavailable" message. DB-006: `rejected` is the honest 4xx outcome that is
 * distinct from — and never labelled — `source_unavailable`. */
export type AddressSearchErrorReason =
    | "unavailable"
    | "source_unavailable"
    | "rejected"
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
            // DB-006: only a transient server-side failure (>= 500) is a
            // retryable `source_unavailable`; every other non-2xx (a 4xx the
            // service will not accept — 404/422/400 — or any other non-ok
            // status) is a distinct, non-retried `rejected`. Retrying a 4xx
            // cannot change the answer, so it must not spend the retry bound
            // nor borrow the transient-failure label.
            if (response.status >= 500)
                return { kind: "error", reason: "source_unavailable" };
            if (!response.ok)
                return { kind: "error", reason: "rejected" };
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

/* ------------------------------------------------------------------ *
 * DB-026 — the GeoSearch address→lot IDENTITY gate.
 *
 * Suggestions (above) may stay permissive. This section governs the DISTINCT
 * act of promoting a single GeoSearch feature to THE resolved lot for
 * analysis/confirm. The captured corpus
 * (docs/research/db026-address-to-lot-fixture-capture.md §1/§4, assertions
 * 1–3) proves GeoSearch /search NEVER returns an empty features array for a
 * bad address — a nonexistent street ("zzqqxx" → "1279 53 STREET") and an
 * out-of-range house number ("99999" → "207") both return HTTP 200 with a
 * plausible but WRONG real lot, at the SAME confidence:0.8 / match_type:
 * "fallback" as the true hit. So neither field discriminates success. The
 * only honest success test is field EQUALITY: the returned housenumber and
 * NORMALIZED street must equal the parsed input. Lot identity binds to
 * addendum.pad.bbl — never the address string or bin, because the true
 * frontage, the GARAGE sibling, and the reverse address-of-record are three
 * distinct features that share one bbl (§1/§3). A gate failure is an honest
 * typed no-match, never a silently wrong lot.
 * ------------------------------------------------------------------ */

/** G5 A1 (M5-T047 rider): the generous upper bound on the parsed input the
 * equality gate will consider. A parsed housenumber or street longer than this
 * is refused with a typed no-match rather than run through normalization/compare
 * — the gate never processes an unboundedly large reflected string. Real NYC
 * addresses are far shorter, so no legitimate input is refused. */
export const GEOSEARCH_RESOLVE_INPUT_MAX_LEN = 512;

/** The parsed address components the gate compares a returned feature against.
 * GeoSearch echoes its own parse as `geocoding.query.parsed_text`; that is the
 * reference parse (corpus §1–§5) when a caller does not supply one. */
export interface GeoSearchParsedInput {
    houseNumber: string;
    street: string;
}

/** A GeoSearch feature promoted to THE resolved lot through the equality gate. */
export interface ResolvedGeoSearchLot {
    /** addendum.pad.bbl — the lot IDENTITY (canonical 10-digit). */
    bbl: string;
    /** addendum.pad.bin — RECORDED, never the identity (siblings differ by bin). */
    bin: string | null;
    /** addendum.pad.version — the body-only PAD freshness stamp (e.g. "26c").
     * GeoSearch exposes no Last-Modified/version HTTP header (corpus §8). */
    padVersion: string | null;
    /** The matched city address exactly as GeoSearch returned it. */
    matchedName: string;
    matchedHouseNumber: string;
    matchedStreet: string;
    /** RECORDED if present (/search), null on /autocomplete (corpus §5) —
     * NEVER consulted as a success test. */
    matchType: string | null;
    confidence: number | null;
}

export type GeoSearchLotResolution =
    | { kind: "resolved"; lot: ResolvedGeoSearchLot; input: GeoSearchParsedInput }
    | { kind: "no_match"; input: GeoSearchParsedInput | null };

/** Fold numeric ordinals immediately following a number: "37TH" → "37",
 * "1ST" → "1". Only a digit run directly suffixed by ST/ND/RD/TH is folded,
 * so "ST NICHOLAS AVENUE" and "37 ST" (spaced) are untouched. */
const ORDINAL_SUFFIX = /\b(\d+)(?:ST|ND|RD|TH)\b/g;

/** Corpus-anchored street normalization for the equality gate: upper-case,
 * whitespace-collapsed, and numeric ordinals folded so the parsed input
 * "37th street" and the returned "37 STREET" compare equal (corpus §1/§2).
 * Deliberately NARROW: it never expands abbreviations or guesses — anything it
 * cannot confidently fold simply fails the gate to an honest no-match rather
 * than risking a wrong lot (packet risk 2, D-051 fail-closed-with-care). */
export function normalizeStreetForMatch(street: string): string {
    return street.trim().toUpperCase().replace(/\s+/g, " ").replace(ORDINAL_SUFFIX, "$1");
}

/** GeoSearch echoes its own parse of the query. Used as the reference parse
 * when the caller supplies none; tolerant of the reduced /autocomplete shape
 * (which still carries housenumber + street). */
function readParsedInput(data: Record<string, unknown>): GeoSearchParsedInput | null {
    const geocoding = data.geocoding;
    if (!geocoding || typeof geocoding !== "object") return null;
    const query = (geocoding as Record<string, unknown>).query;
    if (!query || typeof query !== "object") return null;
    const parsed = (query as Record<string, unknown>).parsed_text;
    if (!parsed || typeof parsed !== "object") return null;
    const p = parsed as Record<string, unknown>;
    if (typeof p.housenumber !== "string" || typeof p.street !== "string") return null;
    return { houseNumber: p.housenumber, street: p.street };
}

/** Read the `properties.addendum.pad` identity block, tolerating its absence. */
function readPad(props: Record<string, unknown>): { bbl: string; bin: string | null; version: string | null } | null {
    const addendum = props.addendum;
    if (!addendum || typeof addendum !== "object") return null;
    const pad = (addendum as Record<string, unknown>).pad;
    if (!pad || typeof pad !== "object") return null;
    const rec = pad as Record<string, unknown>;
    if (typeof rec.bbl !== "string") return null;
    return {
        bbl: rec.bbl.trim(),
        bin: typeof rec.bin === "string" ? rec.bin : null,
        version: typeof rec.version === "string" ? rec.version : null,
    };
}

/**
 * Promote a GeoSearch response body to THE resolved lot under the equality
 * gate, or return an honest typed no-match. `input` defaults to the body's own
 * `geocoding.query.parsed_text`. The first feature whose returned housenumber
 * equals the parsed input AND whose normalized street equals the parsed street
 * AND that carries a canonical 10-digit `addendum.pad.bbl` wins; match_type and
 * confidence are recorded on the result but are NEVER part of the test.
 */
export function resolveLotFromGeoSearch(body: unknown, input?: GeoSearchParsedInput): GeoSearchLotResolution {
    if (!body || typeof body !== "object") return { kind: "no_match", input: input ?? null };
    const data = body as Record<string, unknown>;
    const parsedInput = input ?? readParsedInput(data);
    if (data.type !== "FeatureCollection" || !Array.isArray(data.features) || parsedInput === null)
        return { kind: "no_match", input: parsedInput };
    // G5 A1 (M5-T047 rider): a generous length bound at the gate entry. A parsed
    // housenumber/street longer than this is refused with a typed no-match before
    // any normalization or comparison — the gate never processes an unboundedly
    // large reflected string. Bounded generously so no real address is refused.
    if (
        parsedInput.houseNumber.length > GEOSEARCH_RESOLVE_INPUT_MAX_LEN ||
        parsedInput.street.length > GEOSEARCH_RESOLVE_INPUT_MAX_LEN
    )
        return { kind: "no_match", input: parsedInput };
    const wantHouse = parsedInput.houseNumber.trim();
    const wantStreet = normalizeStreetForMatch(parsedInput.street);
    if (wantHouse === "" || wantStreet === "") return { kind: "no_match", input: parsedInput };
    for (const feature of data.features) {
        if (!feature || typeof feature !== "object") continue;
        const rawProps = (feature as Record<string, unknown>).properties;
        if (!rawProps || typeof rawProps !== "object") continue;
        const props = rawProps as Record<string, unknown>;
        const house = props.housenumber;
        const street = props.street;
        if (typeof house !== "string" || typeof street !== "string") continue;
        // THE EQUALITY GATE. housenumber is exact; street is normalized. A
        // fallback feature on a wrong street ("53 STREET" ≠ "37 STREET") or a
        // substituted house number ("207" ≠ "99999") fails here — match_type
        // and confidence are deliberately NOT read.
        if (house.trim() !== wantHouse) continue;
        if (normalizeStreetForMatch(street) !== wantStreet) continue;
        const pad = readPad(props);
        // Identity binds to a canonical pad.bbl; a matched frontage without one
        // cannot be promoted (honest no-match, never a partial lot).
        if (pad === null || !/^\d{10}$/.test(pad.bbl)) continue;
        return {
            kind: "resolved",
            input: parsedInput,
            lot: {
                bbl: pad.bbl,
                bin: pad.bin,
                padVersion: pad.version,
                matchedName: typeof props.name === "string" ? props.name : typeof props.label === "string" ? props.label : street,
                matchedHouseNumber: house,
                matchedStreet: street,
                matchType: typeof props.match_type === "string" ? props.match_type : null,
                confidence: typeof props.confidence === "number" ? props.confidence : null,
            },
        };
    }
    return { kind: "no_match", input: parsedInput };
}
