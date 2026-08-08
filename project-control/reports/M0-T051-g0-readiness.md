# M0-T051 — G0 readiness (administrative)

Recorded by the orchestrator 2026-08-08.

- Directive binding: D-010 source-021 captured verbatim (R196-R207), validator green; refs stamped.
- Root cause known precisely: `/inheritance:r` strips only INHERITED ACEs and `/grant:r` replaces
  grants only for the NAMED principals, so the file's pre-existing explicit
  `Authenticated Users:(M)` ACE (from the same-volume move) survived the real apply. Doctor
  NOT_PROTECTED captured unelevated as primary evidence (R197, committed).
- Fix directions available inside the existing icacls path (producer chooses smallest correct):
  `/reset` before `/inheritance:r` (deterministic empty-explicit start), or enumerate + `/remove`
  every unexpected principal post-grant; both keep the reviewed command structure; must be
  idempotent and byte-preserving.
- Adversarial fixture is unelevated-feasible: creating a disposable file+parent and granting an
  explicit ACE on one's own file needs no elevation; the REAL hardening behavior (the same
  icacls sequence) can be driven against the fixture without admin because the fixture is
  owner-writable; evaluator probe via os_acl.evaluate_controller_config_acl.
- Gates: G0 (this), G2, G3+G5 (R206), DCV at accept; new blob returned before any elevated apply.
- Holds honored: R196 (no activation, no M2-T015/T016, config untouched, no manual ACL repair).

READY.
