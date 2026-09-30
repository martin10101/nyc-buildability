---
name: ast-source-scan-soundness
description: Soundness holes to check when a supervisor test enforces a "no forbidden surface" property via an AST identifier-extraction scan
metadata:
  type: feedback
---

Supervisor packs enforce invariants like "one-way only / no code-execution surface" with a
`functional_text(path)` helper: it AST-parses a source file, drops docstrings, and collects
`ast.Name.id` + `ast.Attribute.attr` + non-docstring `ast.Constant` strings into a lowercased
blob, then `assertNotIn(token, blob)`.

**Why:** M0-T111 (telegram sink, unit L) L4 one-way scan looked airtight but had dead checks.

**How to apply — when reviewing any such scan, verify each forbidden token can actually match:**
- Tokens containing a PAREN (`"exec("`, `"eval("`) are DEAD: identifier extraction produces the
  bare name `exec`/`eval`, never with the paren, so the assertion can never fire. Confirmed by
  probe: a source literally calling `exec("x")` yields `"exec(" in blob == False`, `"exec" == True`.
- `import subprocess` / `from subprocess import run` EVADE the scan: `ast.Import`/`ast.ImportFrom`
  module & alias names are none of Name/Attribute/Constant, so `subprocess` is never collected
  unless the module is later USED as `subprocess.<attr>` (which DOES surface via the Name node).
- String-concat obfuscation (`"get"+"Updates"`) evades: the two literals are newline-joined so the
  contiguous token isn't present.
- Check the matrix wording vs the actual token list: a row may claim "no receive/approval surface"
  while the scan only lists getUpdates/webhook/setWebhook/getMe (Telegram-specific methods ARE
  caught) and never scans "receive"/"approval".

Fix guidance: check bare identifiers (`"exec"`,`"eval"`) or walk `ast.Call` func names; add
`ast.Import`/`ast.ImportFrom` module names to the blob; and extend the sibling raw-source token
list (the R248-style `source.lower()` check) to include subprocess/exec/eval. Always corroborate
the property by DIRECT source read + a grep — the scan is a backstop, not the primary evidence.
