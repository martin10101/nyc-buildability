import type { AddressDocumentOutcome } from "@/lib/address-api";
import { validateBblInput } from "@/lib/bbl";
const PREFIX = "nyc-buildability:confirmed-address:";
export interface SelectedAddress {
    bbl: string;
    label: string;
    confirmedAt: string;
    sourceRecord: unknown;
}
/** Session-only presentation context. The validated BBL, never the label, keys API requests. */
export function rememberAddress(outcome: AddressDocumentOutcome): void {
    const view = outcome.view;
    const result = validateBblInput(view.canonical.bbl ?? "");
    if (!result.ok || !["resolved", "resolved_with_warnings"].includes(view.status))
        return;
    const label = [[view.inputEcho.houseNumber, view.canonical.streetNameNormalized].filter(Boolean).join(" "), view.canonical.boroughName].filter(Boolean).join(", ");
    if (!label || label.length > 260)
        return;
    const record: SelectedAddress = { bbl: result.canonical, label, confirmedAt: new Date().toISOString(), sourceRecord: view };
    try {
        sessionStorage.setItem(PREFIX + result.canonical, JSON.stringify(record));
    }
    catch { /* Storage denial does not block the property. */ }
}
export function recalledAddress(bbl: string): SelectedAddress | null {
    if (!validateBblInput(bbl).ok)
        return null;
    try {
        const raw = sessionStorage.getItem(PREFIX + bbl);
        if (!raw || raw.length > 100000)
            return null;
        const record = JSON.parse(raw) as Partial<SelectedAddress>;
        if (record.bbl !== bbl || typeof record.label !== "string" || !record.label || record.label.length > 260 || typeof record.confirmedAt !== "string")
            return null;
        return record as SelectedAddress;
    }
    catch {
        return null;
    }
}
