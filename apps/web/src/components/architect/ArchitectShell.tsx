"use client";
import Link from "next/link";
import { InternalBanner } from "@/components/property/InternalBanner";
import { useState, type ReactNode } from "react";
import { propertyHref, VIEW_LABELS, type WorkspaceView } from "@/lib/architect/navigation";
const PRIMARY: WorkspaceView[] = ["overview", "facts", "zoning", "scenarios", "proposal", "evidence", "documents", "issues", "report"];
const PLANNED: WorkspaceView[] = ["envelope", "units", "financials"];
export function ArchitectShell({ bbl, active, children, surveyEnabled = false }: {
    bbl?: string | null;
    active: WorkspaceView | "search" | "survey";
    children: ReactNode;
    surveyEnabled?: boolean;
}) {
    const [menuOpen, setMenuOpen] = useState(false);
    return (<div className="architect-shell">
      <a className="architect-skip" href="#architect-content">Skip to workspace</a>
      <header className="architect-topbar">
        <Link href={propertyHref()} className="architect-brand" aria-label="NYC Buildability — search">
          <svg width="27" height="30" viewBox="0 0 27 30" fill="none" aria-hidden="true">
          <path d="M1 28h25M4 28V14h7v14M11 28V2h9v26M20 8h4v20" stroke="currentColor" strokeWidth="1.7"/>
        </svg>
          <span>NYC BUILDABILITY</span>
        </Link>
        <details className="architect-environment">
        <summary>Internal development build</summary>
        <InternalBanner />
      </details>
        <button className="secondary-button architect-menu-toggle" type="button" aria-expanded={menuOpen} aria-controls="architect-navigation" onClick={() => setMenuOpen(value => !value)}>Navigation</button>
      </header>
      {/* M5-T119 (D-086 P3a, DB-087 g / DISC-P2-1, ledger A01/A03): the shell's
          own environment disclosure (.architect-environment) and the nav
          professional-review footnote are display:none ≤700px (architect.css),
          so on a phone a loaded workspace surface previously showed NEITHER the
          internal-build / no-access-control / do-not-share / "nothing here is a
          legal determination" restriction (A01/LS-P01) NOR the professional-
          review requirement (A03). This phone-only strip (display:none ≥701px in
          architect.css, so no desktop duplication) restores both on every loaded
          surface. It is NOT shown on the search landing (active === "search"),
          which already carries its own always-visible environment+review strip
          (PropertySearch, M5-T115). It reuses that accepted paraphrase verbatim
          (role=note, honest restriction text — never colour alone) rather than a
          second InternalBanner, so no duplicate `internal-banner` region appears
          on a shell-wrapped route; the topbar InternalBanner stays the desktop
          carrier. */}
      {active !== "search" ? <div className="architect-shell-environment" role="note" data-testid="shell-environment">
        <span className="architect-shell-env-badge">Internal build</span>
        <span className="architect-shell-env-note">No sign-in or access control yet, the official data shown is unreviewed, and nothing here is a legal determination — do not share outside the engineering team.</span>
        <p className="architect-shell-review" data-testid="shell-review">Preliminary analysis — professional review required before any reliance.</p>
      </div> : null}
      <div className="architect-body">
        <nav id="architect-navigation" className={`architect-nav ${menuOpen ? "is-open" : ""}`} aria-label="Architect workspace">
          <Link href={propertyHref()} aria-current={active === "search" ? "page" : undefined} onClick={() => setMenuOpen(false)}>Search property</Link>
          <p className="architect-nav-label">Property workspace</p>
          {PRIMARY.map(view => bbl ? <Link key={view} href={propertyHref(bbl, view)} aria-current={active === view ? "page" : undefined} aria-disabled={!bbl || undefined} onClick={() => setMenuOpen(false)}>
          {VIEW_LABELS[view]}
        </Link> : <span className="architect-nav-unavailable" key={view}>
          {VIEW_LABELS[view]}
        </span>)}
          {surveyEnabled ? <Link href="/survey/review" aria-current={active === "survey" ? "page" : undefined}>Survey review</Link> : <span className="architect-nav-unavailable">Survey review <small>Unavailable</small>
        </span>}
          <p className="architect-nav-label">Planning tools</p>
          {PLANNED.map(view => bbl ? <Link key={view} href={propertyHref(bbl, view)} aria-current={active === view ? "page" : undefined}>
          {VIEW_LABELS[view]} <small>Planned</small>
        </Link> : <span className="architect-nav-unavailable" key={view}>
          {VIEW_LABELS[view]} <small>Planned</small>
        </span>)}
          <p className="architect-nav-footnote">Preliminary analysis<br />Professional review required</p>
        </nav>
        <div id="architect-content" className="architect-content">
        {children}
      </div>
      </div>
    </div>);
}
