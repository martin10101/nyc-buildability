"use client";

import { useState } from "react";
import type { SuggestionView } from "@/lib/address-api";

/**
 * The `caller_selects` chooser (task M5-T015, design spec section 2,
 * ambiguous). The endpoint's `selection_policy: "caller_selects"` is
 * rendered LITERALLY: the source's suggestions in source slot order,
 * verbatim (escaped, bounded), as a labeled radio-group with NO default
 * selection, no visual pre-highlight, and no "recommended" chip. The
 * platform picks nothing — "Use this address" stays disabled until the
 * user actively chooses (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md).
 *
 * Render safety: suggestion text renders ONLY as JSX text nodes; the React
 * key is the array index, never the suggestion string; nothing reflected
 * reaches an href/value-as-URL/attribute context. The pick hands back the
 * suggestion's RAW street name (verbatim re-query contract) — that string
 * goes to the fetch seam, never to the DOM.
 */
export function SuggestionChooser({
  suggestions,
  onPick,
}: {
  suggestions: SuggestionView[];
  onPick: (rawStreetName: string) => void;
}) {
  // null = no selection. There is deliberately no default.
  const [selected, setSelected] = useState<number | null>(null);
  return (
    <fieldset className="field-group" data-testid="suggestion-chooser">
      <legend className="field-label">
        Possible street matches, in the city&apos;s own order
      </legend>
      <ul className="missing-list">
        {suggestions.map((suggestion, index) => (
          <li key={index}>
            <label>
              <input
                type="radio"
                name="address-suggestion"
                checked={selected === index}
                onChange={() => setSelected(index)}
                data-testid={`suggestion-option-${index}`}
              />{" "}
              {suggestion.streetName}
              {suggestion.streetCode ? (
                <>
                  {" "}
                  <span className="field-hint">
                    (street code <code>{suggestion.streetCode}</code>)
                  </span>
                </>
              ) : null}
            </label>
          </li>
        ))}
      </ul>
      <button
        type="button"
        className="primary-button"
        disabled={selected === null}
        data-testid="use-suggestion"
        onClick={() => {
          if (selected !== null) {
            onPick(suggestions[selected].rawStreetName);
          }
        }}
      >
        Use this address
      </button>
    </fieldset>
  );
}
