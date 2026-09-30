# Memory index

- [NYC source fetch channels](project_nyc-source-fetch-channels.md) — nyc.gov 403s to non-browser sessions; s-media PDFs + Socrata endpoints reliable; SODA omits null fields
- [NYC street-width source](project_nyc-street-width-source.md) — DCM Street Center Line (ArcGIS primary, SODA g6zj-tzgn stale) is the mapped-width source; Streetwidth is FREE TEXT (fail closed to narrow); Geoclient streetWidth killed (paved)
- [Zoning lot-lookup semantics](zoning-lot-lookup-semantics.md) — ZTLDB=authoritative lot-level (omits condo 75xx billing lots); nyzd bbox over-captures (use centroid); PLUTO bbl float-string + no ordinal in address; corner/range address may have no PLUTO row; GeoSearch empty here
