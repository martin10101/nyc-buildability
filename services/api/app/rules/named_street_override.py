"""ZR 12-10 named-street override matcher (M5-T039; DB-010) — PLACEHOLDER.

Contract-seam placeholder so the packet's content identity binds tracked files
(G0 fails closed on an empty set). The producer replaces this with the typed,
deterministic, tri-state (MATCHED_OVERRIDE / NOT_MATCHED / INDETERMINATE,
fail-closed to INDETERMINATE) matcher built from the sha256-pinned capture
docs/research/zr-snapshots/v1/zr-12-10.snapshot.json ONLY. This module
implements the capture; it is not legal advice (DRAFT pending G6; D-045-R009).
"""
