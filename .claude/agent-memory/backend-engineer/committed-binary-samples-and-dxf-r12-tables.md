---
name: committed-binary-samples-and-dxf-r12-tables
description: Byte-identity for committed sample/golden binaries needs a binary .gitattributes (repo core.autocrlf=true); DXF R12 STYLE/VPORT table facts vs the modern reference
metadata:
  type: project
---

Two reusable facts from building the M5-T096 CAD owner-samples (app/cad DXF/PDF/GLB writers).

## Committed binary/golden samples must be marked `binary` in .gitattributes
The repo has `core.autocrlf=true`. Any committed file that a test regenerates and asserts
BYTE-IDENTICAL to (samples, golden fixtures) will break unless git leaves its bytes alone:
- An ASCII-with-LF file (e.g. an ASCII DXF) is smudged LF->CRLF on Windows checkout -> the
  working-tree bytes no longer match an LF regeneration.
- A file with CR/LF but no NUL byte (e.g. this repo's vector PDF, which carries `\r\n` in its
  xref) is treated as TEXT and git strips the `\r` on `git add`, silently CORRUPTING the blob.
- A file with a NUL byte (GLB) is auto-detected binary and is safe even without an attribute.
Fix: add a `.gitattributes` **inside the sample directory** (root .gitattributes is usually
outside a producer's allowed_paths) with `*.dxf binary` / `*.pdf binary` / `*.glb binary`.
Verify with `git check-attr -a <file>` -> `binary: set, text: unset`; after commit,
`git show HEAD:<path>` piped to sha256 must equal the recorded digest. `git add` prints NO
"LF will be replaced by CRLF" warning for the binary-marked files (it still warns for the
text .md/.py, which is fine). The `.gitattributes` is a dotfile - `dir/**` globs should match
it, but flag it in the producer report in case the allowed_paths matcher excludes dotfiles.

## DXF R12 (AC1009) table facts (Autodesk DXF Reference, verified 2026-09-24)
Targeting R12 means R12 group codes, NOT the current cloudhelp page (which is the R2000+ form):
- STYLE record is STABLE across releases (CHECKED, live 2024 STYLE page
  GUID-EF68AF7C-13EF-45A1-8175-ED6CE66C8FC9): 2 name, 70 flags (1=shape,4=vertical), 40 fixed
  height (0=not fixed -> per-TEXT height), 41 width factor, 50 oblique, 71 gen-flags, 42 last
  height, 3 primary font (`txt`), 4 bigfont (blank). A TEXT with no group 7 resolves to STANDARD.
- VPORT DIVERGES: the live 2024 VPORT page (GUID-8CE7CC87-...) is R2000+ and puts VIEW HEIGHT on
  group **45** with no aspect-ratio code. In R12/AC1009 VIEW HEIGHT = group **40**, VIEWPORT
  ASPECT RATIO = group **41** (lens length 42, clipping 43/44). AutoCAD reads an AC1009 file with
  the R12 schema, so use 40/41 and mark `[recalled - verify]`. A framing VPORT: name `*ACTIVE`,
  view centre 12/22 = extents midpoint, direction 16/26/36 = (0,0,1) plan.
- Canonical R12 TABLES write order is VPORT, LTYPE, LAYER, STYLE (LTYPE before LAYER because a
  layer's group 6 references the linetype). The "About the DXF TABLES Section" overview page GUID
  I tried 404'd, so table order stayed `[recalled - verify]`; the STYLE/VPORT record pages loaded.
- A DWG-focused G1 note: an ASCII DXF from these writers round-trips the accepted reader
  `app.drawings.dxf_reader.read_dxf` -> a strong offline openability signal when AutoCAD is
  unavailable (ok=True, acad_version, units read from $INSUNITS).
