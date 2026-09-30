---
name: ruff-noqa-in-comments-warning
description: ruff emits "Invalid # noqa directive" warnings when the literal "# noqa" appears in a code comment/docstring even as prose
metadata:
  type: reference
---

`ruff check` scans every `# noqa` occurrence as a suppression directive, so
writing the literal string `# noqa` inside a normal comment or docstring (e.g.
explaining that `ruff --add-noqa` "inserts `# noqa` directives") produces
`warning: Invalid # noqa directive ... expected : followed by a comma-separated
list of codes`. "All checks passed!" still prints (it's a warning, not an
error), but it is noise a reviewer will flag.

**How to apply:** when documenting noqa-related behavior in source comments,
write "noqa suppressions" / "noqa comments" WITHOUT the leading `#`, or split
the token, so ruff does not try to parse it. Seen while reworking
[[socrata-pluto-gotchas]]-adjacent supervisor policy (tools/agent_supervisor/
policy.py) for M0-T149.
