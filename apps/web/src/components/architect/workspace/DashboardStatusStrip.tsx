"use client";

import { Fragment, useId, useState } from "react";
import { STRIP_LIMIT, type DashboardNotice, type DashboardStatus } from "./dashboard-status";
import type { DashboardTool } from "./types";

/**
 * The one status strip at the top of the dashboard results (queue D-03; plan §5a items 1, 2
 * and 6). One line of at most three short items; tapping it opens the details behind it: what
 * the items mean and the standing notices, which are never repeated beside a number. Up to three
 * notices that need attention show under the line; more are grouped as one "Notes (N)" item.
 * The line's name stays the same when it opens or closes; `aria-expanded` carries that state.
 */
export function DashboardStatusStrip({ status, notices, onOpen }: {
  status: DashboardStatus;
  notices: readonly DashboardNotice[];
  onOpen: (tool: DashboardTool) => void;
}) {
  const [open, setOpen] = useState(false);
  const panel = useId();
  const items = status.items.slice(0, STRIP_LIMIT);
  const grouped = notices.length > STRIP_LIMIT;
  const noticeButton = (notice: DashboardNotice) => <li key={notice.text}>
    <button type="button" onClick={() => onOpen(notice.tool)}>{notice.text} <span aria-hidden="true">↗</span></button>
  </li>;
  return <section className="bd-status-strip" aria-label="Results status">
    <button type="button" className="bd-strip-line" data-testid="dashboard-status-strip" aria-label={`${items.join(", ")}. Details`}
      aria-expanded={open} aria-controls={panel} onClick={() => setOpen(value => !value)}>
      <span className="bd-strip-items">{items.map((item, index) => <Fragment key={item}>
        {index ? <span aria-hidden="true"> · </span> : null}<span className="bd-strip-item" data-testid="dashboard-status-item">{item}</span>
      </Fragment>)}</span>
      <span className="bd-strip-toggle">Details</span>
    </button>
    {notices.length ? <ul className="bd-strip-notices" aria-label="Needs attention">
      {grouped ? <li><button type="button" aria-controls={panel} aria-expanded={open} onClick={() => setOpen(value => !value)}>Notes ({notices.length})</button></li> : notices.map(noticeButton)}
    </ul> : null}
    <div id={panel} className="bd-strip-details" data-testid="dashboard-status-details" hidden={!open}>
      {grouped ? <><h2>Needs attention</h2><ul className="bd-strip-notice-list">{notices.map(noticeButton)}</ul></> : null}
      <h2>About these results</h2>
      <ul>{status.notes.map(note => <li key={note}>{note}</li>)}</ul>
      <h2>Before you rely on them</h2>
      <ul data-testid="dashboard-standing-notices">{status.standing.map(notice => <li key={notice}>{notice}</li>)}</ul>
    </div>
  </section>;
}
