"use client";

import { useEffect, useRef, useState, type CSSProperties, type KeyboardEvent, type PointerEvent, type ReactNode } from "react";

type Frame = { left: number; top: number; width: number; height: number };
type Gesture = { pointerId: number; x: number; y: number; frame: Frame; resize: boolean };

export type FloatingWorkspaceWindowProps = {
  id: string;
  title: string;
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  wide?: boolean;
};

let lastWindowLayer = 40;
const GUTTER = 8;

function viewport() {
  const visual = window.visualViewport;
  return {
    left: (visual?.offsetLeft ?? 0) + GUTTER,
    top: (visual?.offsetTop ?? 0) + GUTTER,
    width: Math.max(1, (visual?.width ?? window.innerWidth) - GUTTER * 2),
    height: Math.max(1, (visual?.height ?? window.innerHeight) - GUTTER * 2),
  };
}

function fitFrame(frame: Frame): Frame {
  const bounds = viewport();
  const width = Math.max(Math.min(400, bounds.width), Math.min(frame.width, bounds.width));
  const height = Math.max(Math.min(280, bounds.height), Math.min(frame.height, bounds.height));
  return {
    width,
    height,
    left: Math.max(bounds.left, Math.min(frame.left, bounds.left + bounds.width - width)),
    top: Math.max(bounds.top, Math.min(frame.top, bounds.top + bounds.height - height)),
  };
}

function initialFrame(wide: boolean): Frame {
  const bounds = viewport();
  const width = Math.min(wide ? 1100 : 850, bounds.width);
  const height = Math.min(690, bounds.height);
  return fitFrame({
    left: bounds.left + (bounds.width - width) / 2,
    top: bounds.top + (bounds.height - height) / 2,
    width,
    height,
  });
}

/** A modeless, in-tree workspace surface. Closing never discards a mounted editor. */
export function FloatingWorkspaceWindow({ id, title, open, onClose, children, wide = false }: FloatingWorkspaceWindowProps) {
  const [hasOpened, setHasOpened] = useState(open);
  const [frame, setFrame] = useState<Frame | null>(null);
  const [maximized, setMaximized] = useState(false);
  const [layer, setLayer] = useState(40);
  const windowRef = useRef<HTMLElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const openerRef = useRef<HTMLElement | null>(null);
  const gesture = useRef<Gesture | null>(null);
  const wasOpen = useRef(false);
  const restoreFrame = useRef<Frame | null>(null);

  useEffect(() => {
    if (open) {
      setHasOpened(true);
      const active = document.activeElement;
      if (active instanceof HTMLElement && !windowRef.current?.contains(active)) openerRef.current = active;
      setFrame(value => fitFrame(value ?? initialFrame(wide)));
      setLayer(++lastWindowLayer);
      closeRef.current?.focus({ preventScroll: true });
    } else if (wasOpen.current) {
      gesture.current = null;
      // An external dashboard action can close a window without losing its focus.
      if ((windowRef.current?.contains(document.activeElement) || document.activeElement === document.body)
        && openerRef.current?.isConnected) {
        openerRef.current.focus({ preventScroll: true });
      }
    }
    wasOpen.current = open;
  }, [open, wide]);

  useEffect(() => {
    if (!open) return;
    const resize = () => setFrame(value => maximized ? viewport() : fitFrame(value ?? initialFrame(wide)));
    resize();
    window.addEventListener("resize", resize);
    window.visualViewport?.addEventListener("resize", resize);
    window.visualViewport?.addEventListener("scroll", resize);
    return () => {
      window.removeEventListener("resize", resize);
      window.visualViewport?.removeEventListener("resize", resize);
      window.visualViewport?.removeEventListener("scroll", resize);
    };
  }, [open, maximized, wide]);

  function raise() { setLayer(++lastWindowLayer); }

  function adjust(dx: number, dy: number, resize: boolean) {
    if (maximized) return;
    setFrame(value => {
      const current = value ?? initialFrame(wide);
      return fitFrame(resize
        ? { ...current, width: current.width + dx, height: current.height + dy }
        : { ...current, left: current.left + dx, top: current.top + dy });
    });
  }

  function moveWithKeys(event: KeyboardEvent<HTMLButtonElement>, resize = false) {
    const step = event.shiftKey ? 50 : 10;
    const directions: Record<string, [number, number]> = {
      ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step],
    };
    const direction = directions[event.key];
    if (!direction || maximized) return;
    event.preventDefault();
    event.stopPropagation();
    adjust(direction[0], direction[1], resize);
  }

  function beginGesture(event: PointerEvent<HTMLButtonElement>, resize = false) {
    if (maximized || event.button !== 0) return;
    event.preventDefault();
    event.currentTarget.focus({ preventScroll: true });
    gesture.current = { pointerId: event.pointerId, x: event.clientX, y: event.clientY,
      frame: frame ?? initialFrame(wide), resize };
    event.currentTarget.setPointerCapture?.(event.pointerId);
  }

  function continueGesture(event: PointerEvent<HTMLButtonElement>) {
    const start = gesture.current;
    if (!start || start.pointerId !== event.pointerId) return;
    const dx = event.clientX - start.x;
    const dy = event.clientY - start.y;
    setFrame(fitFrame(start.resize
      ? { ...start.frame, width: start.frame.width + dx, height: start.frame.height + dy }
      : { ...start.frame, left: start.frame.left + dx, top: start.frame.top + dy }));
  }

  function endGesture(event: PointerEvent<HTMLButtonElement>) {
    if (gesture.current?.pointerId !== event.pointerId) return;
    gesture.current = null;
    if (event.currentTarget.hasPointerCapture?.(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
  }

  function toggleMaximize() {
    gesture.current = null;
    if (maximized) {
      setFrame(fitFrame(restoreFrame.current ?? initialFrame(wide)));
    } else {
      restoreFrame.current = frame ?? initialFrame(wide);
      setFrame(viewport());
    }
    setMaximized(value => !value);
  }

  function closeWithEscape(event: KeyboardEvent<HTMLElement>) {
    if (event.key !== "Escape" || event.defaultPrevented) return;
    const target = event.target;
    // A child dialog owns its own Escape, including portalled React descendants.
    if (!(target instanceof Element) || target.closest('[role="dialog"], [role="alertdialog"], dialog') !== windowRef.current) return;
    event.stopPropagation();
    event.preventDefault();
    onClose();
  }

  if (!hasOpened && !open) return null;
  const style: CSSProperties = { ...(frame ?? {}), zIndex: layer };
  return (
    <section id={id} ref={windowRef} className={`workspace-window${maximized ? " workspace-window--maximized" : ""}`}
      role="dialog" aria-modal={false} aria-labelledby={`${id}-title`} hidden={!open}
      style={style} onKeyDown={closeWithEscape} onPointerDownCapture={raise} onFocusCapture={raise}>
      <header className="workspace-window__header">
        <h2 className="workspace-window__heading">
          <button className="workspace-window__move" type="button" aria-label={`Move ${title} window`}
            aria-describedby={`${id}-move-help`} onKeyDown={event => moveWithKeys(event)}
            onPointerDown={event => beginGesture(event)} onPointerMove={continueGesture}
            onPointerUp={endGesture} onPointerCancel={endGesture} onLostPointerCapture={() => { gesture.current = null; }}>
            <span aria-hidden="true" className="workspace-window__grip">⠿</span><span id={`${id}-title`}>{title}</span>
          </button>
        </h2>
        <div className="workspace-window__controls" role="group" aria-label={`${title} window controls`}>
          <button type="button" aria-label={`Decrease ${title} window size`} title="Smaller window" disabled={maximized}
            onClick={() => adjust(-100, -70, true)}>−</button>
          <button type="button" aria-label={`Increase ${title} window size`} title="Larger window" disabled={maximized}
            onClick={() => adjust(100, 70, true)}>+</button>
          <button type="button" aria-label={`${maximized ? "Restore" : "Maximize"} ${title} window`}
            title={maximized ? "Restore window" : "Maximize window"} onClick={toggleMaximize}>
            <span aria-hidden="true">{maximized ? "❐" : "□"}</span>
          </button>
          <button ref={closeRef} type="button" className="workspace-window__close" aria-label={`Close ${title} window`}
            title="Close window — keeps your work" onClick={onClose}>×</button>
        </div>
      </header>
      <p id={`${id}-move-help`} className="workspace-window__sr-only">Drag the title to move this window, or use the arrow keys. Hold Shift for larger steps.</p>
      <div className="workspace-window__content">{children}</div>
      <button className="workspace-window__resize" type="button" aria-label={`Resize ${title} window`}
        aria-describedby={`${id}-resize-help`} disabled={maximized} onKeyDown={event => moveWithKeys(event, true)}
        onPointerDown={event => beginGesture(event, true)} onPointerMove={continueGesture}
        onPointerUp={endGesture} onPointerCancel={endGesture} onLostPointerCapture={() => { gesture.current = null; }}>
        <span aria-hidden="true">◢</span>
      </button>
      <p id={`${id}-resize-help`} className="workspace-window__sr-only">Drag this corner or use the arrow keys to resize. Hold Shift for larger steps.</p>
    </section>
  );
}
