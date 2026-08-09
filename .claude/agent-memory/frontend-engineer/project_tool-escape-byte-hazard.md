---
name: tool-escape-byte-hazard
description: Write/Edit tool params decode backslash-u escapes into literal bytes — caused the M2-T002 N1 raw-NUL defect and recurred in M2-T005; use Python byte-level writes
metadata:
  type: project
---

Writing a JavaScript escape sequence (backslash + u0000 etc.) through the
Write/Edit tool parameters gets decoded by the tool-call JSON layer into the
LITERAL control byte, silently reintroducing binary bytes into source files.

**Why:** this is exactly how the M2-T002 api.test.ts raw-NUL defect (G3 note
N1) was born, and it recurred while writing the M2-T005 producer report —
two literal NULs landed in the .md until a byte scan caught them.

**How to apply:** whenever a source file must CONTAIN an escape sequence as
text, write it with a Python heredoc using byte concatenation
(b"no_" + bytes([92]) + b"u0000match"), never through Write/Edit params.
After any file write that discussed escapes/control characters, run a byte
scan (open(p,'rb'); flag c<9, 11, 12, 13<c<32) over every touched file
before submitting. Related: [[property-profile-frontend-rules]].
