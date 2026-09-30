---
name: strict-pdf-reader-sideload-under-311
description: Run app.documents.extraction strict PDF reader round-trip tests under the 3.11 sandbox by sideloading its self-contained subgraph from source
metadata:
  type: feedback
---

To exercise the in-repo strict survey PDF reader (`read_pdf_container` +
`interpret_content`) in a test that must also pass CI, do NOT import the
`app.documents.extraction` package normally in the 3.11 developer sandbox: the
package `__init__` pulls in pipeline modules (routing -> checks -> `app/documents/
units.py`) that use Python 3.12-only PEP 695 syntax, so the import raises
`SyntaxError` and the WHOLE test file fails to collect (the repo's own
`tests/documents/test_pdf_container.py` also fails to collect under 3.11).

**Why:** sandbox is Python 3.11; repo/CI target is 3.12 (ruff `target-version=py312`).
See also [[env-producer-sandbox-no-exec]] and [[m2t015-python312-and-gate-lessons]].

**How to apply:** write a `_reader()` helper that (a) tries the plain
`from app.documents.extraction.pdf_container import ...` first (works in CI 3.12,
and is what reviewers expect), and (b) on `SyntaxError` sideloads ONLY the
self-contained reader subgraph from source — `pdf_lexer`, `pdf_objects`,
`pdf_xref`, `pdf_container`, `pdf_content`, in that dependency order. Register
placeholder `types.ModuleType` for `app.documents` and `app.documents.extraction`
(with `__path__=[]`) in `sys.modules` so relative (`.pdf_lexer`) and absolute
(`app.documents.extraction.pdf_lexer`, used by `pdf_content`) imports resolve
without running the real `__init__`; keep the real `app` package (needed for
`app.cad`). Load each via `importlib.util.spec_from_file_location(full_name, path)`
with `module.__package__ = "app.documents.extraction"`. This runs the IDENTICAL
reader source, never edits the extraction package, and gives local green for
round-trip tests. Worked example: `services/api/tests/cad/test_pdf_sheet_writer.py`
(M5-T085). A dependency-free PDF *writer* that only emits the reader's subset
(straight lines `m/l/h`, `re` rectangles, horizontal text under a translation-only
CTM; uncompressed stream with a direct `/Length`; classic xref with exact 10-digit
offsets) round-trips cleanly through this reader.
