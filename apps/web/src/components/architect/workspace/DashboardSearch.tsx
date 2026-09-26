"use client";
import { useRef, useState, type FormEvent, type MouseEvent } from "react";
import { AddressResolutionScreen } from "@/components/address/AddressResolutionScreen";
import { validateBblInput } from "@/lib/bbl";

export function DashboardSearch({ onSelect }: { onSelect: (bbl: string) => void }) {
  const [bbl, setBbl] = useState("");
  const [error, setError] = useState<string | null>(null);
  const disclosure = useRef<HTMLDetailsElement>(null);
  const input = useRef<HTMLInputElement>(null);
  function submit(event: FormEvent) {
    event.preventDefault();
    const valid = validateBblInput(bbl);
    if (!valid.ok) { setError(valid.message); return; }
    setError(null);
    if (disclosure.current) disclosure.current.open = false;
    onSelect(valid.canonical);
  }
  function recovery(event: MouseEvent) {
    const anchor = (event.target as Element).closest("a");
    if (anchor?.getAttribute("href") !== "#bbl-input") return;
    event.preventDefault();
    if (disclosure.current) disclosure.current.open = true;
    input.current?.focus();
  }
  return <section className="dashboard-search" aria-label="Property search" onClickCapture={recovery}>
    <AddressResolutionScreen architect compact onConfirmLot={onSelect}/>
    <details className="dashboard-bbl-search" ref={disclosure}>
      <summary>Search by BBL</summary>
      <form onSubmit={submit} noValidate>
        <label htmlFor="dashboard-bbl">Borough–block–lot</label>
        <div><input id="dashboard-bbl" ref={input} className="text-input" value={bbl} onChange={event => { setBbl(event.target.value); setError(null); }} inputMode="numeric" placeholder="10-digit BBL" aria-invalid={!!error} aria-describedby="dashboard-bbl-error"/>
        <button className="primary-button" type="submit">Open property</button></div>
        <p id="dashboard-bbl-error" role="status">{error}</p>
      </form>
    </details>
  </section>;
}
