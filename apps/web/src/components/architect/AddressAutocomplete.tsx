"use client";
import { useState, type RefObject } from "react";
import type { AddressQuery } from "@/lib/address-api";
import type { AddressSuggestion } from "@/lib/address-search";
import { useAddressSuggestions } from "@/lib/architect/use-address-suggestions";
export function AddressAutocomplete({ onPick, onEdit, inputRef }: {
    onPick: (query: AddressQuery) => void;
    onEdit: () => void;
    inputRef: RefObject<HTMLInputElement | null>;
}) {
    const [text, setText] = useState("");
    const [open, setOpen] = useState(false);
    const [active, setActive] = useState(-1);
    const [selected, setSelected] = useState(false);
    const { outcome, loading } = useAddressSuggestions(text, selected);
    const suggestions = outcome?.kind === "suggestions" ? outcome.suggestions : [];
    const choose = (item: AddressSuggestion) => {
        setText(`${item.query.houseNumber} ${item.query.street}, ${item.borough}`);
        setSelected(true);
        setOpen(false);
        onPick(item.query);
    };
    const message = loading ? "Searching official NYC addresses…" : outcome?.kind === "error" ? (outcome.reason === "rate_limited" ? "Address suggestions are busy. Use manual entry or BBL below." : "Address suggestions are unavailable. Use manual entry or BBL below.") : outcome?.kind === "suggestions" && open ? (suggestions.length ? `${suggestions.length} address suggestions. Use arrow keys to choose, then Enter.` : "No matching address suggestions. Try a more complete address, manual entry or BBL.") : "";
    return <div className="architect-autocomplete">
    <label className="field-label" htmlFor="architect-address">Street address</label>
    <input id="architect-address" ref={inputRef} className="text-input architect-search-input" role="combobox" aria-autocomplete="list" aria-expanded={open && suggestions.length > 0} aria-controls="architect-address-options" aria-activedescendant={open && active >= 0 ? `address-option-${active}` : undefined} aria-describedby="architect-address-hint" autoComplete="off" placeholder="Enter a New York City address" maxLength={200} value={text} onChange={event => { setText(event.target.value); setSelected(false); setActive(-1); setOpen(true); onEdit(); }} onKeyDown={event => {
            if (event.key === "Escape") {
                setOpen(false);
                setActive(-1);
            }
            if (event.key === "ArrowDown" && suggestions.length) {
                event.preventDefault();
                setOpen(true);
                setActive(index => (index + 1) % suggestions.length);
            }
            if (event.key === "ArrowUp" && suggestions.length) {
                event.preventDefault();
                setOpen(true);
                setActive(index => (index <= 0 ? suggestions.length - 1 : index - 1));
            }
            if (event.key === "Enter") {
                event.preventDefault();
                if (open && active >= 0 && suggestions[active])
                    choose(suggestions[active]);
            }
        }} onBlur={() => setOpen(false)} onFocus={() => { if (!selected && suggestions.length)
        setOpen(true); }}/>
    {open && suggestions.length ? <ul id="architect-address-options" role="listbox" aria-label="Official NYC address suggestions" className="architect-suggestions">
      {suggestions.map((item, index) => <li key={`${item.label}-${index}`} id={`address-option-${index}`} role="option" aria-selected={active === index} onMouseDown={event => event.preventDefault()} onClick={() => choose(item)}>
        <strong>
          {item.query.houseNumber} {item.query.street}
        </strong>
        <span>
          {item.borough}
          {item.query.zip ? ` · ${item.query.zip}` : ""}
        </span>
      </li>)}
    </ul> : <ul id="architect-address-options" role="listbox" aria-label="Official NYC address suggestions" hidden/>}
    <p id="architect-address-hint" className="section-note">All five boroughs · <a href="https://geosearch.planninglabs.nyc/docs/" target="_blank" rel="noopener noreferrer">NYC Planning address suggestions ↗</a>
    </p>
    <p className="architect-search-status" role="status">
      {message}
    </p>
  </div>;
}
