import { cleanup, act, fireEvent, render, screen } from "@testing-library/react";
import { createRef } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AddressAutocomplete } from "../AddressAutocomplete";
import type { AddressSearchOutcome } from "@/lib/address-search";
const search = vi.hoisted(() => vi.fn());
vi.mock("@/lib/address-search", () => ({ ADDRESS_SEARCH_DEBOUNCE_MS: 300, fetchAddressSuggestions: search }));
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

afterEach(cleanup);
