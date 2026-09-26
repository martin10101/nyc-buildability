import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { isMapContainerVisible, observeMapContainer } from "../map-container";

let panel: HTMLDivElement;
let container: HTMLDivElement;
let resized: ResizeObserverCallback;
const disconnected = vi.fn();

beforeEach(() => {
  vi.useFakeTimers();
  panel = document.createElement("div");
  container = document.createElement("div");
  panel.append(container);
  document.body.append(panel);
  disconnected.mockReset();
  vi.stubGlobal("ResizeObserver", class {
    constructor(callback: ResizeObserverCallback) { resized = callback; }
    observe() {}
    disconnect() { disconnected(); }
  });
});
afterEach(() => { panel.remove(); vi.unstubAllGlobals(); vi.useRealTimers(); });

describe("floating map container lifecycle", () => {
  it("pauses a partially used render deadline while hidden and resumes only the remaining visible time", async () => {
    const onResize = vi.fn(), onTimeout = vi.fn();
    const watch = observeMapContainer(container, { onResize, onTimeout });
    await vi.advanceTimersByTimeAsync(4_000);
    panel.hidden = true;
    await Promise.resolve();
    await vi.advanceTimersByTimeAsync(30_000);
    expect(onTimeout).not.toHaveBeenCalled();
    panel.hidden = false;
    await Promise.resolve();
    expect(onResize).toHaveBeenCalledOnce();
    await vi.advanceTimersByTimeAsync(5_999);
    expect(onTimeout).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(1);
    expect(onTimeout).toHaveBeenCalledOnce();
    watch.dispose();
  });

  it("does not spend the initial deadline behind a hidden ancestor, including CSS hiding", async () => {
    panel.style.display = "none";
    const onResize = vi.fn(), onTimeout = vi.fn();
    const watch = observeMapContainer(container, { onResize, onTimeout });
    expect(isMapContainerVisible(container)).toBe(false);
    await vi.advanceTimersByTimeAsync(20_000);
    expect(onTimeout).not.toHaveBeenCalled();
    panel.style.display = "block";
    await Promise.resolve();
    expect(isMapContainerVisible(container)).toBe(true);
    expect(onResize).toHaveBeenCalledOnce();
    await vi.advanceTimersByTimeAsync(10_000);
    expect(onTimeout).toHaveBeenCalledOnce();
    watch.dispose();
  });

  it("keeps resizing after real parcel readiness without rearming the deadline", async () => {
    const onResize = vi.fn(), onTimeout = vi.fn();
    const watch = observeMapContainer(container, { onResize, onTimeout });
    watch.markReady();
    resized([], {} as ResizeObserver);
    expect(onResize).toHaveBeenCalledOnce();
    panel.hidden = true;
    await Promise.resolve();
    resized([], {} as ResizeObserver);
    expect(onResize).toHaveBeenCalledOnce();
    panel.hidden = false;
    await Promise.resolve();
    expect(onResize).toHaveBeenCalledTimes(2);
    await vi.advanceTimersByTimeAsync(30_000);
    expect(onTimeout).not.toHaveBeenCalled();
    watch.dispose();
  });

  it("disposes observers and the deadline, ignoring later resize notifications", async () => {
    const onResize = vi.fn(), onTimeout = vi.fn();
    const watch = observeMapContainer(container, { onResize, onTimeout });
    watch.dispose();
    expect(disconnected).toHaveBeenCalledOnce();
    resized([], {} as ResizeObserver);
    panel.hidden = true;
    await vi.advanceTimersByTimeAsync(20_000);
    expect(onResize).not.toHaveBeenCalled();
    expect(onTimeout).not.toHaveBeenCalled();
  });

  it("still detects reveal when ResizeObserver is unavailable", async () => {
    vi.stubGlobal("ResizeObserver", undefined);
    panel.hidden = true;
    const onResize = vi.fn();
    const watch = observeMapContainer(container, { onResize, onTimeout: vi.fn() });
    panel.hidden = false;
    await Promise.resolve();
    expect(onResize).toHaveBeenCalledOnce();
    watch.dispose();
  });
});
