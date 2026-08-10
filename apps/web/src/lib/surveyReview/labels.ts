/**
 * Survey-review display vocabulary (task M2-T016).
 *
 * Every status is communicated with the full quadruple — LABEL + SYMBOL +
 * (CSS) tone + GLOSS — so meaning is never carried by color alone
 * (docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md §8; docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md).
 * The exact wire enum value is preserved; the gloss only explains it. The UI
 * never invents a status and never upgrades one — in particular "Verified" is
 * NEVER used for a survey fact (workflow §5.4).
 */

import type {
  CheckId,
  CheckStatus,
  ConfirmationState,
  DocumentState,
  DownstreamStatus,
  ExtractionMethod,
} from "./types";

export interface StatusDisplay {
  /** Human label shown to the reviewer. */
  label: string;
  /** Non-color symbol so status is never color-only. */
  symbol: string;
  /** Plain-language explanation (title/screen-reader gloss). */
  gloss: string;
  /** CSS tone class suffix (`.sr-tone-<tone>`); never the sole signal. */
  tone: "neutral" | "info" | "caution" | "conflict" | "positive" | "muted";
}

const DOCUMENT_STATE_DISPLAY: Record<DocumentState, StatusDisplay> = {
  uploaded: {
    label: "Uploaded",
    symbol: "◍",
    gloss: "Original stored immutably; not yet processed.",
    tone: "muted",
  },
  processing: {
    label: "Processing",
    symbol: "◔",
    gloss: "Extraction or verification is running. Read-only.",
    tone: "info",
  },
  auto_extracted: {
    label: "Auto-extracted",
    symbol: "◐",
    gloss:
      "Every executed check passed on the clean digital path. Facts are still unconfirmed evidence — never promoted by extraction alone.",
    tone: "info",
  },
  needs_review: {
    label: "Needs review",
    symbol: "!",
    gloss: "A qualified professional must resolve open items before this document can be confirmed.",
    tone: "caution",
  },
  rejected: {
    label: "Rejected",
    symbol: "∅",
    gloss: "Terminal. A corrected upload is a NEW document with its own digest.",
    tone: "conflict",
  },
  professionally_confirmed: {
    label: "Professionally confirmed",
    symbol: "✓",
    gloss:
      "A designated qualified professional confirmed the document after per-fact review. Each fact still carries its own confirmation state.",
    tone: "positive",
  },
};

export function documentStateDisplay(state: DocumentState): StatusDisplay {
  return DOCUMENT_STATE_DISPLAY[state];
}

const CONFIRMATION_DISPLAY: Record<ConfirmationState, StatusDisplay> = {
  unconfirmed: {
    label: "Unconfirmed evidence",
    symbol: "◐",
    gloss:
      "No qualified professional has confirmed this fact. This is the birth state of every extracted fact regardless of method or confidence — it is never 'Verified'.",
    tone: "caution",
  },
  confirmed: {
    label: "Confirmed",
    symbol: "✓",
    gloss: "A qualified professional confirmed this normalized value.",
    tone: "positive",
  },
  rejected: {
    label: "Rejected",
    symbol: "✕",
    gloss: "A qualified professional rejected this detection as unusable.",
    tone: "conflict",
  },
};

export function confirmationDisplay(state: ConfirmationState): StatusDisplay {
  return CONFIRMATION_DISPLAY[state];
}

const CHECK_STATUS_DISPLAY: Record<CheckStatus, StatusDisplay> = {
  pass: {
    label: "Passed",
    symbol: "✓",
    gloss: "The deterministic check confirmed the value.",
    tone: "positive",
  },
  fail: {
    label: "Conflict",
    symbol: "≠",
    gloss: "The check ran and found a contradiction. Resolve by correcting the fact or rejecting the detection.",
    tone: "conflict",
  },
  unresolved: {
    label: "Unresolved",
    symbol: "?",
    gloss: "The check could not independently validate the value. This is a visible fail-closed condition, never a silent pass.",
    tone: "caution",
  },
};

export function checkStatusDisplay(status: CheckStatus): StatusDisplay {
  return CHECK_STATUS_DISPLAY[status];
}

const DOWNSTREAM_DISPLAY: Record<DownstreamStatus, StatusDisplay> = {
  blocked: {
    label: "Blocked",
    symbol: "⨯",
    gloss: "This conclusion cannot be computed without the unresolved survey item. No value is fabricated.",
    tone: "conflict",
  },
  provisional: {
    label: "Provisional",
    symbol: "≈",
    gloss: "Computed on a stated assumption while a survey item is unresolved. Not a final result.",
    tone: "caution",
  },
  recalculating: {
    label: "Recalculating",
    symbol: "◔",
    gloss: "Your decision changed the evidence; dependent conclusions are being recomputed.",
    tone: "info",
  },
  cleared: {
    label: "Cleared",
    symbol: "✓",
    gloss: "The blocking survey item was resolved and the dependent conclusion recomputed.",
    tone: "positive",
  },
};

export function downstreamDisplay(status: DownstreamStatus): StatusDisplay {
  return DOWNSTREAM_DISPLAY[status];
}

/** Human labels for the closed check-id enum. */
const CHECK_LABELS: Record<CheckId, string> = {
  address_bbl_match: "Address / BBL match",
  units_consistency: "Units consistency",
  scale_consistency: "Scale consistency",
  north_orientation: "North orientation",
  boundary_closure: "Boundary closure",
  area_vs_stated: "Calculated vs stated area",
  segment_sum: "Segment sum",
  contradictory_dimensions: "Contradictory dimensions",
  geometry_validity: "Geometry validity",
  elevation_consistency: "Elevation consistency",
  tax_lot_geometry_comparison: "Tax-lot geometry comparison",
};

export function checkLabel(checkId: CheckId): string {
  return CHECK_LABELS[checkId];
}

/** Human labels + advisory marker for the closed extraction-method enum. */
const EXTRACTION_METHOD_LABELS: Record<ExtractionMethod, { label: string; advisory: boolean }> = {
  vector_object_extraction: { label: "Vector object extraction", advisory: false },
  embedded_text_extraction: { label: "Embedded text extraction", advisory: false },
  ocr_text: { label: "OCR text (advisory)", advisory: true },
  line_symbol_detection: { label: "Line / symbol detection (advisory)", advisory: true },
  ai_assisted_classification: { label: "AI-assisted classification (advisory)", advisory: true },
  deterministic_geometry_reconstruction: {
    label: "Deterministic geometry reconstruction",
    advisory: false,
  },
};

export function extractionMethodDisplay(method: ExtractionMethod): { label: string; advisory: boolean } {
  return EXTRACTION_METHOD_LABELS[method];
}
