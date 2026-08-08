"""Survey / official-document ingestion module (M2-T015).

Document-level ingestion for uploaded surveys and official documents: the document
lifecycle state machine (``state.py``) and the typed domain models for the document
ingestion record and its per-fact link to the ``survey_evidence`` contract
(``models.py``). Grounded in docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md and
docs/SURVEY_EVIDENCE_CONTRACT.md.

Doctrine (non-negotiable): AI retrieves, classifies, drafts, and explains;
deterministic code calculates, normalizes, reconstructs, and validates; qualified
humans approve. The backend state machine is the only writer of document state — no
AI or model-derived input can trigger, veto, or propose a transition. Storage is
B-001-honest: no production storage binding exists anywhere in this module; the
immutable-original SHA-256 digest, not a storage id, is the content identity.
"""
