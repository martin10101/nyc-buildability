import { TAX_LOT_ONLY_ESTIMATE, taxLotScopeWarning, type VerifiedZoningLot } from "@/lib/architect/tax-lot-scope";

/**
 * The tax-lot-only warning (owner directive 2026-10-01). Always visible on every surface that
 * shows a calculated floor-area or FAR number: never behind a tap, a strip or a disclosure, and
 * printed with the brief. Plain text in a note, not a chip. With a coherent verified zoning-lot
 * fact for `bbl` it names the zoning lot's tax lots and the one lot the numbers use; otherwise
 * it reads the generic warning.
 */
export function TaxLotOnlyNotice({ bbl = "", zoningLot = null }: { bbl?: string; zoningLot?: VerifiedZoningLot | null }) {
  return <p className="tax-lot-only-notice" role="note" data-testid="tax-lot-only-warning">{taxLotScopeWarning(bbl, zoningLot)}</p>;
}

/** The label on a floor-area cap value: a plain-text line under the number, never a chip. */
export function TaxLotOnlyEstimate({ testId }: { testId: string }) {
  return <p className="tax-lot-only-qualifier" data-testid={testId}>{TAX_LOT_ONLY_ESTIMATE}</p>;
}
