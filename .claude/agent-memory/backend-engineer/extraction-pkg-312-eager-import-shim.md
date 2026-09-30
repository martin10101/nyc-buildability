---
name: extraction-pkg-312-eager-import-shim
description: Any test importing app.documents.extraction.* is UN-collectible under the 3.11 sandbox (extraction __init__ eagerly imports units.py 3.12 generic syntax); a sys.modules package-stub shim runs the real tests locally
metadata:
  type: project
---

`app/documents/extraction/__init__.py` eagerly imports `survey_pipeline` -> `checks` ->
`app/documents/units.py`, which uses Python-3.12 generic syntax (`def _match_unit[UnitT:
enum.Enum](...`, line ~276). Under the sandbox interpreter (Python **3.11.9**; the repo
targets 3.12) that is a hard `SyntaxError: expected '('` at IMPORT time. Consequences:

- `import app.documents.extraction.pdf_xref` (or any sibling submodule) fails under 3.11 —
  importing a submodule runs the parent package `__init__`, which pulls units.py. So a
  strict-reader consumer (e.g. `app.drawings.sheet_reader`) and its test are BOTH
  un-collectible locally; the documented `python -m pytest ...` exits 2 on a collection
  SyntaxError. It runs green in CI (Python 3.12). Keeping YOUR code 3.11-compatible is NOT
  enough — the blocker is the transitive eager import.
- No Python 3.12/3.13 is launchable in this sandbox: `py -0p` lists 3.11 + 3.13 but the
  3.13 binary fails to start ("system cannot find the file specified"); 3.12 is absent.

Fix that gives real OBSERVED local test evidence (touches no repo file): a scratchpad shim
pre-registers a BARE package chain in `sys.modules` so the real submodules load from
`__path__` WITHOUT running the eager `__init__`:

```python
import pathlib, sys, types
API = pathlib.Path(r"...\services\api"); sys.path.insert(0, str(API))
for name, rel in [("app","app"),("app.documents","app/documents"),
                  ("app.documents.extraction","app/documents/extraction"),
                  ("app.drawings","app/drawings")]:
    if name not in sys.modules:
        m = types.ModuleType(name); m.__path__=[str(API/rel)]; m.__package__=name
        sys.modules[name] = m
```

Then `import shim` before `pytest.main([<test file>])` from a scratchpad runner. `pdf_lexer/
pdf_objects/pdf_xref/pdf_content` import only each other (no units), so they load fine. The
canonical documented command still gets ROUTED TO CI HARVEST; the shim is only to prove the
test LOGIC locally. Used in M5-T083 (sheet_reader profile): shimmed `23 passed`, canonical
`exit=2` blocked. Related: [[env-producer-sandbox-no-exec]] (the 3.11-vs-3.12 note there is
the shallow version of this).

Also: `tools/modularity_check.py` is string/regex based (no `ast.parse`), and `ruff` uses its
own Rust parser with `target-version = py312`, so BOTH run fine under 3.11 even on the
3.12-syntax files — only CPython import/pytest is blocked.
