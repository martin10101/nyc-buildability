import { useEffect, useState } from "react";
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { FloatingWorkspaceWindow } from "../FloatingWorkspaceWindow";

function Harness({ onMount = () => undefined }: { onMount?: () => void }) {
  const [open, setOpen] = useState(false);
  return <div className="architect-shell">
    <button type="button" onClick={() => setOpen(true)}>Open map</button>
    <button type="button">Dashboard action</button>
    <FloatingWorkspaceWindow id="test-map" title="Map" open={open} onClose={() => setOpen(false)}>
      <Editor onMount={onMount} />
    </FloatingWorkspaceWindow>
  </div>;
}

function Editor({ onMount }: { onMount: () => void }) {
  const [name, setName] = useState("");
  useEffect(onMount, [onMount]);
  return <label>Proposal name<input value={name} onChange={event => setName(event.target.value)} /></label>;
}

function openMap() {
  const opener = screen.getByRole("button", { name: "Open map" });
  opener.focus();
  fireEvent.click(opener);
  return opener;
}

function rectangle(element: HTMLElement) {
  return {
    left: Number.parseFloat(element.style.left), top: Number.parseFloat(element.style.top),
    width: Number.parseFloat(element.style.width), height: Number.parseFloat(element.style.height),
  };
}

class TestPointerEvent extends MouseEvent {
  readonly pointerId: number;
  constructor(type: string, init: PointerEventInit = {}) {
    super(type, init);
    this.pointerId = init.pointerId ?? 1;
  }
}

beforeEach(() => {
  vi.stubGlobal("innerWidth", 1440);
  vi.stubGlobal("innerHeight", 1000);
});
afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });

describe("FloatingWorkspaceWindow", () => {
  it("mounts only when first opened and retains the editor when closed", () => {
    const onMount = vi.fn();
    render(<Harness onMount={onMount} />);
    expect(screen.queryByLabelText("Proposal name")).toBeNull();
    expect(onMount).not.toHaveBeenCalled();
    openMap();
    fireEvent.change(screen.getByLabelText("Proposal name"), { target: { value: "Courtyard proposal" } });
    fireEvent.click(screen.getByRole("button", { name: "Close Map window" }));
    expect(screen.getByLabelText("Proposal name")).not.toBeVisible();
    openMap();
    expect(screen.getByLabelText("Proposal name")).toHaveValue("Courtyard proposal");
    expect(onMount).toHaveBeenCalledTimes(1);
  });

  it("stays inside the architect shell, focuses its close control, and returns focus on Escape", () => {
    render(<Harness />);
    const opener = openMap();
    const dialog = screen.getByRole("dialog", { name: "Map" });
    expect(dialog.closest(".architect-shell")).not.toBeNull();
    expect(dialog).toHaveAttribute("aria-modal", "false");
    expect(screen.getByRole("button", { name: "Close Map window" })).toHaveFocus();
    fireEvent.keyDown(screen.getByLabelText("Proposal name"), { key: "Escape" });
    expect(dialog).not.toBeVisible();
    expect(opener).toHaveFocus();
  });

  it("does not trap focus or close when Escape is pressed on the dashboard", () => {
    render(<Harness />);
    openMap();
    const outside = screen.getByRole("button", { name: "Dashboard action" });
    outside.focus();
    fireEvent.keyDown(outside, { key: "Escape" });
    expect(outside).toHaveFocus();
    expect(screen.getByRole("dialog", { name: "Map" })).toBeVisible();
  });

  it("leaves handled Escape and nested dialogs to their own controls", () => {
    const close = vi.fn();
    render(<div className="architect-shell">
      <FloatingWorkspaceWindow id="outer" title="Evidence" open onClose={close}>
        <input aria-label="Handled input" onKeyDown={event => event.preventDefault()} />
        <section role="dialog" aria-label="Source details"><button type="button">Nested action</button></section>
        <button type="button">Outer action</button>
      </FloatingWorkspaceWindow>
    </div>);
    fireEvent.keyDown(screen.getByLabelText("Handled input"), { key: "Escape" });
    fireEvent.keyDown(screen.getByRole("button", { name: "Nested action" }), { key: "Escape" });
    expect(close).not.toHaveBeenCalled();
    fireEvent.keyDown(screen.getByRole("button", { name: "Outer action" }), { key: "Escape" });
    expect(close).toHaveBeenCalledTimes(1);
  });

  it("moves only from the title control and constrains keyboard movement to the viewport", () => {
    render(<Harness />);
    openMap();
    const dialog = screen.getByRole("dialog", { name: "Map" });
    const start = rectangle(dialog);
    fireEvent.keyDown(screen.getByLabelText("Proposal name"), { key: "ArrowRight" });
    expect(rectangle(dialog)).toEqual(start);
    const move = screen.getByRole("button", { name: "Move Map window" });
    fireEvent.keyDown(move, { key: "ArrowRight" });
    fireEvent.keyDown(move, { key: "ArrowDown", shiftKey: true });
    expect(rectangle(dialog)).toEqual({ ...start, left: start.left + 10, top: start.top + 50 });
    for (let count = 0; count < 40; count++) {
      fireEvent.keyDown(move, { key: "ArrowLeft", shiftKey: true });
      fireEvent.keyDown(move, { key: "ArrowUp", shiftKey: true });
    }
    expect(rectangle(dialog).left).toBe(8);
    expect(rectangle(dialog).top).toBe(8);
  });

  it("supports pointer title dragging and stops moving after pointer release", () => {
    // JSDOM lacks PointerEvent in some supported test environments.
    vi.stubGlobal("PointerEvent", TestPointerEvent);
    render(<Harness />);
    openMap();
    const dialog = screen.getByRole("dialog", { name: "Map" });
    const start = rectangle(dialog);
    const move = screen.getByRole("button", { name: "Move Map window" });
    move.setPointerCapture = vi.fn();
    move.hasPointerCapture = vi.fn(() => true);
    move.releasePointerCapture = vi.fn();
    fireEvent.pointerDown(move, { button: 0, clientX: 100, clientY: 100 });
    expect(move.setPointerCapture).toHaveBeenCalledWith(1);
    fireEvent.pointerMove(move, { pointerId: 2, clientX: 140, clientY: 130 });
    expect(rectangle(dialog)).toEqual(start);
    fireEvent.pointerMove(move, { clientX: 140, clientY: 130 });
    expect(rectangle(dialog)).toEqual({ ...start, left: start.left + 40, top: start.top + 30 });
    fireEvent.pointerUp(move, { clientX: 140, clientY: 130 });
    expect(move.releasePointerCapture).toHaveBeenCalledWith(1);
    fireEvent.pointerMove(move, { clientX: 170, clientY: 180 });
    expect(rectangle(dialog)).toEqual({ ...start, left: start.left + 40, top: start.top + 30 });

    const resize = screen.getByRole("button", { name: "Resize Map window" });
    fireEvent.pointerDown(resize, { button: 0, clientX: 100, clientY: 100 });
    fireEvent.pointerMove(resize, { clientX: 130, clientY: 120 });
    expect(rectangle(dialog)).toEqual({ left: start.left + 40, top: start.top + 30,
      width: start.width + 30, height: start.height + 20 });
    fireEvent.pointerCancel(resize);
    fireEvent.pointerMove(resize, { clientX: 180, clientY: 200 });
    expect(rectangle(dialog).width).toBe(start.width + 30);
  });

  it("resizes using buttons and keyboard, maximizes, and restores the prior size", () => {
    render(<Harness />);
    openMap();
    const dialog = screen.getByRole("dialog", { name: "Map" });
    const start = rectangle(dialog);
    fireEvent.click(screen.getByRole("button", { name: "Decrease Map window size" }));
    expect(rectangle(dialog).width).toBe(start.width - 100);
    fireEvent.click(screen.getByRole("button", { name: "Increase Map window size" }));
    expect(rectangle(dialog)).toEqual(start);
    fireEvent.keyDown(screen.getByRole("button", { name: "Resize Map window" }), { key: "ArrowRight" });
    const resized = rectangle(dialog);
    expect(resized.width).toBe(start.width + 10);
    fireEvent.click(screen.getByRole("button", { name: "Maximize Map window" }));
    expect(rectangle(dialog)).toEqual({ left: 8, top: 8, width: 1424, height: 984 });
    expect(screen.getByRole("button", { name: "Increase Map window size" })).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: "Restore Map window" }));
    expect(rectangle(dialog)).toEqual(resized);
  });

  it("keeps its title and controls inside a narrow viewport after browser resize", () => {
    render(<Harness />);
    openMap();
    vi.stubGlobal("innerWidth", 375);
    vi.stubGlobal("innerHeight", 600);
    act(() => { window.dispatchEvent(new Event("resize")); });
    const bounds = rectangle(screen.getByRole("dialog", { name: "Map" }));
    expect(bounds).toEqual({ left: 8, top: 8, width: 359, height: 584 });
    fireEvent.click(screen.getByRole("button", { name: "Increase Map window size" }));
    expect(rectangle(screen.getByRole("dialog", { name: "Map" }))).toEqual(bounds);
  });

  it("fits the visible mobile viewport when zoom or the on-screen keyboard changes it", () => {
    const visibleViewport = Object.assign(new EventTarget(), { offsetLeft: 20, offsetTop: 100, width: 375, height: 400 });
    vi.stubGlobal("visualViewport", visibleViewport);
    render(<Harness />);
    openMap();
    const dialog = screen.getByRole("dialog", { name: "Map" });
    expect(rectangle(dialog)).toEqual({ left: 28, top: 108, width: 359, height: 384 });
    visibleViewport.height = 300;
    act(() => { visibleViewport.dispatchEvent(new Event("resize")); });
    expect(rectangle(dialog)).toEqual({ left: 28, top: 108, width: 359, height: 284 });
  });

  it("closes only the window that receives Escape", () => {
    const closeMap = vi.fn();
    const closeEvidence = vi.fn();
    render(<div className="architect-shell">
      <FloatingWorkspaceWindow id="map-one" title="Map" open onClose={closeMap}><button>Map action</button></FloatingWorkspaceWindow>
      <FloatingWorkspaceWindow id="evidence-two" title="Evidence" open onClose={closeEvidence}><button>Evidence action</button></FloatingWorkspaceWindow>
    </div>);
    fireEvent.keyDown(within(screen.getByRole("dialog", { name: "Map" })).getByRole("button", { name: "Map action" }), { key: "Escape" });
    expect(closeMap).toHaveBeenCalledTimes(1);
    expect(closeEvidence).not.toHaveBeenCalled();
  });
});
