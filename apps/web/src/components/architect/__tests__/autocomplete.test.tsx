import { cleanup, act, fireEvent, render, screen } from "@testing-library/react";
import { createRef } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AddressAutocomplete, FULL_ADDRESS_SEARCH_LABEL } from "../AddressAutocomplete";
import type { AddressSearchErrorReason, AddressSearchOutcome } from "@/lib/address-search";
const search = vi.hoisted(() => vi.fn());
const fullSearch = vi.hoisted(() => vi.fn());
vi.mock("@/lib/address-search", () => ({ ADDRESS_SEARCH_DEBOUNCE_MS: 300, fetchAddressSuggestions: search, fetchAddressSearch: fullSearch }));
afterEach(() => { vi.useRealTimers(); vi.clearAllMocks(); });
const suggestion = (street: string): AddressSearchOutcome => ({ kind: "suggestions", suggestions: [{ label: street, borough: "Queens", query: { houseNumber: "120-55", street, borough: "Queens", zip: null } }] });
describe("address suggestion interaction", () => {
  it("debounces typing and resolves only an explicit keyboard pick", async () => {
    vi.useFakeTimers(); search.mockResolvedValue(suggestion("QUEENS BOULEVARD"));
    const onPick = vi.fn(), onEdit = vi.fn();
    render(<AddressAutocomplete onPick={onPick} onEdit={onEdit} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Queens" } });
    await act(async () => { vi.advanceTimersByTime(299); });
    expect(screen.queryByRole("option")).not.toBeInTheDocument();
    expect(onPick).not.toHaveBeenCalled();
    await act(async () => { vi.advanceTimersByTime(1); });
    expect(screen.getByRole("option")).toHaveTextContent("QUEENS BOULEVARD");
    fireEvent.keyDown(screen.getByRole("combobox"), { key: "ArrowDown" });
    fireEvent.keyDown(screen.getByRole("combobox"), { key: "Enter" });
    expect(onPick).toHaveBeenCalledWith({ houseNumber: "120-55", street: "QUEENS BOULEVARD", borough: "Queens", zip: null });
    expect(screen.getByRole("combobox")).toHaveAttribute("aria-expanded", "false");
  });
  it("ignores a stale suggestion response after the user edits the address", async () => {
    vi.useFakeTimers();
    let completeOld: (value: AddressSearchOutcome) => void = () => undefined;
    search.mockImplementationOnce(() => new Promise(resolve => { completeOld = resolve; })).mockResolvedValueOnce(suggestion("NEW STREET"));
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "old street" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "new street" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    await act(async () => { completeOld(suggestion("OLD STREET")); });
    expect(screen.getByRole("option")).toHaveTextContent("NEW STREET");
    expect(screen.queryByText("OLD STREET")).not.toBeInTheDocument();
    fireEvent.keyDown(screen.getByRole("combobox"), { key: "Escape" });
    expect(screen.queryByRole("option")).not.toBeInTheDocument();
  });
});

describe("distinct failure recovery and the explicit full-address action (M5-T032)", () => {
  it("reads each failure reason with its own copy and never clears the typed text (handoff §6)", async () => {
    vi.useFakeTimers();
    const cases: Array<[AddressSearchErrorReason, RegExp]> = [
      ["rate_limited", /rate-limited/i],
      ["timeout", /taking too long/i],
      ["source_unavailable", /temporarily unavailable/i],
      // DB-006: a 4xx the service will not accept reads as its own honest line,
      // never the transient "temporarily unavailable" copy.
      ["rejected", /didn.t accept that search/i],
      ["unavailable", /check your connection/i],
      ["malformed", /read safely/i],
    ];
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} inputRef={createRef()} />);
    for (const [reason, pattern] of cases) {
      search.mockResolvedValue({ kind: "error", reason });
      fireEvent.change(screen.getByRole("combobox"), { target: { value: `120 Broadway ${reason}` } });
      await act(async () => { vi.advanceTimersByTime(300); });
      expect(screen.getByRole("status")).toHaveTextContent(pattern);
      // The typed text survives every failure — nothing is retyped.
      expect(screen.getByRole("combobox")).toHaveValue(`120 Broadway ${reason}`);
    }
  });

  it("AS-2 (DB-007): the timeout outcome STILL offers the explicit full-address search button", async () => {
    // The recovery affordance the timeout copy points at must actually be
    // present — the test fails if the button disappears on a timeout.
    vi.useFakeTimers();
    search.mockResolvedValue({ kind: "error", reason: "timeout" });
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Broadway" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    const button = screen.getByTestId("full-address-search");
    expect(button).toBeInTheDocument();
    // It is usable, not stuck disabled (nothing is searching at rest).
    expect(button).not.toBeDisabled();
    expect(screen.getByRole("status")).toHaveTextContent(/taking too long/i);
  });

  it("AS-4 (DB-009): the failure copy names the SAME string the button carries — one shared label, no silent drift", async () => {
    // A malformed reply still renders the full-address button; its copy must
    // name that button by exactly the label the button shows. Both read from
    // FULL_ADDRESS_SEARCH_LABEL, so a rename cannot break only one side.
    vi.useFakeTimers();
    search.mockResolvedValue({ kind: "error", reason: "malformed" });
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Broadway" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    expect(screen.getByTestId("full-address-search")).toHaveTextContent(FULL_ADDRESS_SEARCH_LABEL);
    expect(screen.getByRole("status")).toHaveTextContent(FULL_ADDRESS_SEARCH_LABEL);
  });

  it("distinguishes an incomplete address from a genuine no-match (neither is presented as a service failure)", async () => {
    vi.useFakeTimers();
    search.mockResolvedValue({ kind: "suggestions", suggestions: [] });
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "12" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    expect(screen.getByRole("status")).toHaveTextContent(/at least 3 characters/i);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Nowhere Street" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    expect(screen.getByRole("status")).toHaveTextContent(/no matching address found/i);
  });

  it("routes a source failure to the prefilled manual/Geoclient fallback with the typed text intact", async () => {
    vi.useFakeTimers();
    search.mockResolvedValue({ kind: "error", reason: "source_unavailable" });
    const onFallback = vi.fn();
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} onFallback={onFallback} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Broadway" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    fireEvent.click(screen.getByTestId("use-manual-entry"));
    expect(onFallback).toHaveBeenCalledWith("120 Broadway");
  });

  it("runs the explicit full-address /search and never auto-accepts the first candidate as the lot", async () => {
    vi.useFakeTimers();
    search.mockResolvedValue({ kind: "suggestions", suggestions: [] });
    fullSearch.mockResolvedValue(suggestion("BROADWAY"));
    const onPick = vi.fn();
    render(<AddressAutocomplete onPick={onPick} onEdit={vi.fn()} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Broadway, New York" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    await act(async () => { fireEvent.click(screen.getByTestId("full-address-search")); });
    expect(fullSearch).toHaveBeenCalledWith("120 Broadway, New York", expect.objectContaining({ signal: expect.any(AbortSignal) }));
    // A candidate is shown, but nothing is accepted as the lot without an explicit pick.
    expect(onPick).not.toHaveBeenCalled();
    expect(screen.getByRole("option")).toHaveTextContent("BROADWAY");
    fireEvent.keyDown(screen.getByRole("combobox"), { key: "ArrowDown" });
    fireEvent.keyDown(screen.getByRole("combobox"), { key: "Enter" });
    expect(onPick).toHaveBeenCalledTimes(1);
  });

  it("Enter with no highlighted suggestion triggers the explicit /search, never a silent first-match accept", async () => {
    vi.useFakeTimers();
    search.mockResolvedValue({ kind: "suggestions", suggestions: [] });
    fullSearch.mockResolvedValue(suggestion("BROADWAY"));
    const onPick = vi.fn();
    render(<AddressAutocomplete onPick={onPick} onEdit={vi.fn()} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Broadway, New York" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    await act(async () => { fireEvent.keyDown(screen.getByRole("combobox"), { key: "Enter" }); });
    expect(fullSearch).toHaveBeenCalledWith("120 Broadway, New York", expect.objectContaining({ signal: expect.any(AbortSignal) }));
    expect(onPick).not.toHaveBeenCalled();
  });
});

/** The explicit /search must carry the SAME cancellation + request-generation
 * discipline as the suggestion hook: editing, picking a candidate, and unmount
 * all supersede an in-flight search, a new query can search immediately, and a
 * late/superseded reply is dropped, never rendered (M5-T032, handoff §6). */
describe("explicit full-address search — cancellation and request-generation protection (M5-T032)", () => {
  function deferred<T>() {
    let resolve!: (value: T) => void;
    const promise = new Promise<T>((r) => { resolve = r; });
    return { promise, resolve };
  }

  it("editing during an in-flight full search aborts its transport and frees an immediate new search", async () => {
    vi.useFakeTimers();
    search.mockResolvedValue({ kind: "suggestions", suggestions: [] });
    const first = deferred<AddressSearchOutcome>();
    const signals: AbortSignal[] = [];
    fullSearch.mockImplementation((_query: string, options: { signal: AbortSignal }) => {
      signals.push(options.signal);
      return signals.length === 1 ? first.promise : Promise.resolve(suggestion("FIFTH"));
    });
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Broadway" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    await act(async () => { fireEvent.click(screen.getByTestId("full-address-search")); });
    expect(signals[0].aborted).toBe(false);

    // Editing supersedes the in-flight search — its transport is aborted…
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "500 Fifth Avenue" } });
    expect(signals[0].aborted).toBe(true);
    await act(async () => { vi.advanceTimersByTime(300); });
    // …and a brand-new search runs immediately (the button is not stuck disabled).
    const button = screen.getByTestId("full-address-search");
    expect(button).not.toBeDisabled();
    await act(async () => { fireEvent.click(button); });
    expect(signals).toHaveLength(2);
    expect(fullSearch.mock.calls[1][0]).toBe("500 Fifth Avenue");

    // The abandoned first reply arrives late and must never render.
    await act(async () => { first.resolve(suggestion("STALE")); });
    expect(screen.queryByText(/STALE/)).not.toBeInTheDocument();
    expect(screen.getByRole("option")).toHaveTextContent("FIFTH");
  });

  it("a delayed full-address reply for a superseded query never overwrites the current screen", async () => {
    vi.useFakeTimers();
    search.mockResolvedValue({ kind: "suggestions", suggestions: [] });
    const slow = deferred<AddressSearchOutcome>();
    fullSearch.mockReturnValueOnce(slow.promise);
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Broadway" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    await act(async () => { fireEvent.click(screen.getByTestId("full-address-search")); });

    // The user edits away before the slow /search reply arrives.
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "500 Fifth Avenue" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    await act(async () => { slow.resolve(suggestion("BROADWAY")); });
    expect(screen.queryByText(/BROADWAY/)).not.toBeInTheDocument();
    expect(screen.queryByRole("option")).toBeNull();
    expect(screen.getByRole("combobox")).toHaveValue("500 Fifth Avenue");
  });

  it("A→B→A: a late reply for the FIRST search of query A never displaces the fresh A result (query-equality alone cannot guard this)", async () => {
    vi.useFakeTimers();
    search.mockResolvedValue({ kind: "suggestions", suggestions: [] });
    const firstA = deferred<AddressSearchOutcome>();
    fullSearch
      .mockReturnValueOnce(firstA.promise)            // A (first)
      .mockResolvedValueOnce(suggestion("A-FRESH"));  // A (second, after B)
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} inputRef={createRef()} />);
    const box = screen.getByRole("combobox");
    fireEvent.change(box, { target: { value: "100 A Street" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    await act(async () => { fireEvent.click(screen.getByTestId("full-address-search")); }); // A (first) in flight
    fireEvent.change(box, { target: { value: "200 B Street" } });                            // → B
    await act(async () => { vi.advanceTimersByTime(300); });
    fireEvent.change(box, { target: { value: "100 A Street" } });                            // → back to A
    await act(async () => { vi.advanceTimersByTime(300); });
    await act(async () => { fireEvent.click(screen.getByTestId("full-address-search")); }); // A (second)
    expect(screen.getByRole("option")).toHaveTextContent("A-FRESH");

    // The first-A reply (same text as now) arrives LAST — the sequence guard,
    // not text equality, must drop it.
    await act(async () => { firstA.resolve(suggestion("A-STALE")); });
    expect(screen.getByRole("option")).toHaveTextContent("A-FRESH");
    expect(screen.queryByText(/A-STALE/)).not.toBeInTheDocument();
  });

  it("selecting a candidate aborts an in-flight full search", async () => {
    vi.useFakeTimers();
    search.mockResolvedValue(suggestion("QUEENS BOULEVARD"));
    const slow = deferred<AddressSearchOutcome>();
    let captured: AbortSignal | undefined;
    fullSearch.mockImplementation((_query: string, options: { signal: AbortSignal }) => { captured = options.signal; return slow.promise; });
    render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Queens" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    await act(async () => { fireEvent.click(screen.getByTestId("full-address-search")); });
    expect(captured!.aborted).toBe(false);
    fireEvent.keyDown(screen.getByRole("combobox"), { key: "ArrowDown" });
    fireEvent.keyDown(screen.getByRole("combobox"), { key: "Enter" });
    expect(captured!.aborted).toBe(true);
  });

  it("unmounting aborts an in-flight full search", async () => {
    vi.useFakeTimers();
    search.mockResolvedValue({ kind: "suggestions", suggestions: [] });
    const slow = deferred<AddressSearchOutcome>();
    let captured: AbortSignal | undefined;
    fullSearch.mockImplementation((_query: string, options: { signal: AbortSignal }) => { captured = options.signal; return slow.promise; });
    const { unmount } = render(<AddressAutocomplete onPick={vi.fn()} onEdit={vi.fn()} inputRef={createRef()} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "120 Broadway" } });
    await act(async () => { vi.advanceTimersByTime(300); });
    await act(async () => { fireEvent.click(screen.getByTestId("full-address-search")); });
    expect(captured!.aborted).toBe(false);
    unmount();
    expect(captured!.aborted).toBe(true);
  });
});

afterEach(cleanup);
