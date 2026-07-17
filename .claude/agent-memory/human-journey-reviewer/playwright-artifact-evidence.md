---
name: playwright-artifact-evidence
description: How to extract visual evidence from this repo's CI Playwright artifacts when tests passed (no PNGs, only trace.zip)
metadata:
  type: project
---

CI Playwright config uses `screenshot: "only-on-failure"` + `trace: "on"`, so a fully green run uploads NO standalone PNGs — every test dir holds only `trace.zip`.

**Why:** the M2-T001 G3 review expected per-test PNGs; they do not exist on passing runs.

**How to apply:** `trace.zip` is a plain zip containing viewport screencast frames as `resources/page@*.jpeg`, viewable with the Read tool after `unzip -o -j <trace.zip> "resources/*.jpeg" -d <tempdir>`. Frames follow the viewport at action time only — content asserted via `toContainText` (no scroll) may never appear in a frame; use frames from tests that CLICK below the fold (clicks auto-scroll). Judge unphotographed content from spec assertions + component code. The Bash tool on this machine runs bash (POSIX), not PowerShell, despite the env note.
