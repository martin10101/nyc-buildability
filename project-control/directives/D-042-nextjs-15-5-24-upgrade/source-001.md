# D-042 source-001 (original, verbatim; owner via interactive chat, 2026-09-12)

Owner message (the directive, verbatim):

> Authorize the Next.js security upgrade to 15.5.24" —

Capture context: the owner issued the exact authorization line the orchestrator proposed after
live research (the trailing quote/dash are copy artifacts of that proposal). The researched
basis, presented to the owner immediately before authorization: the pinned next@15.5.21 falls in
the affected range (13.4–15.5.23) of the critical RCE advisories patched 2026-08-25
(CVE-2026-75604 CVSS 9.0 Windows path traversal + AVIF flaw; patched releases 15.5.24
Maintenance LTS / 16.3.3 Active LTS); 15.5.24 is on the same maintenance line as the current pin
and, at 18 days since publish, passes the 7-day age gate. The owner had previously asked "how do
we safely get Next.js to work — should we downgrade?" and was advised downgrade is never the
fix (all older versions share the advisories); the owner also reviewed the download-safety chain
(official registry, lockfile integrity hashes, exact pins, min-release-age=7, provenance
signatures, CI-only installs) before authorizing.

Scope notes agreed in the same exchange: 15.5.24 EXACTLY (no 16.x major migration); the upgrade
does NOT authorize any hosted/public deployment (a separate owner decision); after the tree is
advisory-free this unblocks the maplibre-gl admission for the lot-outline web half (B-022).
Once this one-time gate is discharged, FUTURE dependency security bumps follow the standing
docs/DEPENDENCY_SECURITY_POLICY.md machinery without per-instance owner authorization (owner
involvement remains only where that policy already requires it, e.g. age-gate waivers).
