/** A hidden floating panel keeps its map mounted. Hidden time must not consume
 * the rendering deadline, and revealing/resizing the panel must resize WebGL.
 * This observes presentation only; it never decides that parcel data rendered. */
export function isMapContainerVisible(container: HTMLElement): boolean {
  if (!container.isConnected) return false;
  for (let element: HTMLElement | null = container; element; element = element.parentElement) {
    const style = getComputedStyle(element);
    if (element.hidden || style.display === "none" || style.visibility === "hidden" || style.visibility === "collapse") return false;
  }
  return true;
}

export function observeMapContainer(container: HTMLElement, options: {
  onResize: () => void;
  onTimeout: () => void;
  timeoutMs?: number;
}) {
  let remaining = options.timeoutMs ?? 10_000;
  let started = 0;
  let timer: ReturnType<typeof setTimeout> | null = null;
  let visible = isMapContainerVisible(container);
  let ready = false;
  let disposed = false;
  const pause = () => {
    if (timer === null) return;
    clearTimeout(timer);
    timer = null;
    remaining = Math.max(0, remaining - (Date.now() - started));
  };
  const resume = () => {
    if (ready || disposed || timer !== null) return;
    started = Date.now();
    timer = setTimeout(() => {
      if (disposed || ready) return;
      if (!isMapContainerVisible(container)) { pause(); visible = false; return; }
      timer = null;
      ready = true;
      options.onTimeout();
    }, remaining);
  };
  const sync = (resized: boolean) => {
    if (disposed) return;
    const next = isMapContainerVisible(container);
    const revealed = next && !visible;
    visible = next;
    if (!visible) { pause(); return; }
    resume();
    if (revealed || resized) options.onResize();
  };
  const mutationObserver = new MutationObserver(() => sync(false));
  // Observe ancestors, not map descendants: MapLibre's own style updates must
  // not trigger a resize feedback loop.
  for (let element: HTMLElement | null = container; element; element = element.parentElement) {
    mutationObserver.observe(element, { attributes: true, attributeFilter: ["hidden", "style", "class"] });
  }
  const resizeObserver = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(() => sync(true));
  resizeObserver?.observe(container);
  if (visible) resume();
  return {
    markReady() { ready = true; pause(); },
    dispose() {
      if (disposed) return;
      disposed = true;
      pause();
      mutationObserver.disconnect();
      resizeObserver?.disconnect();
    },
  };
}
