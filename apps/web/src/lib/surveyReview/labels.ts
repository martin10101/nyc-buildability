/**
 * Survey-review display vocabulary (task M2-T016 rework).
 *
 * Every status is communicated with the full quadruple — LABEL + SYMBOL +
 * (CSS) tone + GLOSS — so meaning is never carried by color alone
 * (docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md §8; docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md).
 * The exact wire enum value is preserved; the gloss only explains it. "Verified"
 * is NEVER used for a survey fact (workflow §5.4).
 */

import type {
  ConfirmationState,
  DocumentState,
  DownstreamImpactKind,
  ExtractionMethod,
} from "./types";

export interface StatusDisplay {
  label: string;
  symbol: string;
  gloss: string;
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

/** Presentation status derived from a fact's deterministic-check counts. */
export type CheckSummaryKind = "conflict" | "unresolved" | "passed";

const CHECK_SUMMARY_DISPLAY: Record<CheckSummaryKind, StatusDisplay> = {
  conflict: {
    label: "Conflict",
    symbol: "≠",
    gloss: "A deterministic check found a contradiction. Resolve by correcting the fact or rejecting the detection.",
    tone: "conflict",
  },
  unresolved: {
    label: "Unresolved",
    symbol: "?",
    gloss: "A deterministic check could not independently validate the value — a visible fail-closed condition, never a silent pass.",
    tone: "caution",
  },
  passed: {
    label: "Checks passed",
    symbol: "✓",
    gloss: "Every executed deterministic check confirmed the value.",
    tone: "positive",
  },
};

export function checkSummaryDisplay(kind: CheckSummaryKind): StatusDisplay {
  return CHECK_SUMMARY_DISPLAY[kind];
}

const DOWNSTREAM_DISPLAY: Record<DownstreamImpactKind, StatusDisplay> = {
  blocked: {
    label: "Blocked",
    symbol: "⨯",
    gloss: "A dependent buildability conclusion cannot rest on this fact until it is resolved. No value is fabricated.",
    tone: "conflict",
  },
  provisional: {
    label: "Provisional",
    symbol: "≈",
    gloss: "A dependent conclusion is provisional on this unconfirmed evidence — not a final result.",
    tone: "caution",
  },
};

export function downstreamKindDisplay(kind: DownstreamImpactKind): StatusDisplay {
  return DOWNSTREAM_DISPLAY[kind];
}

/** Coverage-status gloss for a downstream impact (existing 1.4.0 vocabulary). */
export function coverageStatusGloss(status: string): string {
  if (status === "data_conflict") return "Official/derived sources disagree; nothing was resolved.";
  return "A qualified professional must review this before reliance.";
}

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

export function extractionMethodDisplay(
  method: ExtractionMethod | null,
): { label: string; advisory: boolean } {
  if (!method) return { label: "Unknown extraction method", advisory: true };
  return EXTRACTION_METHOD_LABELS[method];
}

/**
 * AWAITING-BACKEND label for the open `fact_type` string. A small known map for
 * the common survey fact types, else a humanised fallback (never fabricated —
 * it is a display transform of the wire value, clearly derived).
 */
const FACT_TYPE_LABELS: Record<string, string> = {
  boundary_segment_distance: "Boundary segment distance",
  boundary_bearing: "Boundary bearing",
  stated_lot_area: "Stated lot area",
  scale_statement: "Scale statement",
  north_arrow_orientation: "North arrow orientation",
  elevation_value: "Elevation value",
  address_text: "Address text",
};

export function factTypeLabel(factType: string): string {
  if (FACT_TYPE_LABELS[factType]) return FACT_TYPE_LABELS[factType];
  return factType
    .split(/[_\s]+/)
    .filter(Boolean)
    .map((word, i) => (i === 0 ? word.charAt(0).toUpperCase() + word.slice(1) : word))
    .join(" ");
}
