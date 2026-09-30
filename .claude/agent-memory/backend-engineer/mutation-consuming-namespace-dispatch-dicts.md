---
name: mutation-consuming-namespace-dispatch-dicts
description: In-process mutation testing — patch the TRUE consuming namespace; import-time dispatch dicts hold functions by value, so patching the method is a silent false survivor
metadata:
  type: feedback
---

When writing in-process mutation tests for this repo's reader profiles (and any Python module),
install the mutant on the name that is actually resolved AT CALL TIME, not a by-value copy.

**Why:** the M5-T083 F5 lesson ("test imported read_sheet BY VALUE → naive rebind was a false
survivor") recurs with dispatch dicts. In `services/api/app/drawings/sheet_interpreter.py`,
`_PATH_HANDLERS = {"v": _StreamRun._op_v, ...}` is built at import with the ORIGINAL functions;
`_execute` calls `_PATH_HANDLERS[word](self)`. Patching `_StreamRun._op_v/_op_y/_op_c/...` therefore
does NOT reach dispatch (verified: the mutated curve came out byte-identical). The effective
consuming namespace is `_PATH_HANDLERS["v"]`. By contrast `_curveto` is reached via
`self._curveto(...)` (dynamic attribute lookup), so patching the class method there IS effective.

**How to apply:** before trusting a mutant "survived", confirm it actually took effect (the asserted
value must MOVE). For sheet_reader: facade-threaded hooks patch at `sheet_reader.*`
(`_concat_matrix`, `_flatten_cubic`, `_decode_stream`, `MAX_*`); interpreter internals patch at
`sheet_interpreter._PATH_HANDLERS[...]`, `._PAINT_STROKE/_PAINT_FILL/_PAINT_CLOSE_FIRST`,
`._IGNORED`, `._apply_matrix`; decode/memo/budget at `sheet_objects._StreamDecoder.decode_form` /
`.charge_decoded` (instance methods, dynamic lookup, effective). Keep COMMITTED tests to the public
`read_sheet` contract + stable facade names only (M5-T103 owns the reader modules and may rename
internals) — record the internal-namespace mutant red runs in the producer report instead of
committing a fragile dependency on those names. See [[env-producer-sandbox-no-exec]] for the 3.11
bare-package shim needed to run these suites locally.
