"""Deterministic, offline regression tests for the lock-verifier ``--check``
reproducibility fix (task M0-T021).

Root cause repaired here: ``lock_tools.sh --check`` / ``lock_requirements.sh
--check`` compiled the fresh resolution into a BLANK ``mktemp`` output file.
``uv pip compile`` uses the versions already present in ``--output-file`` as
resolution PREFERENCES (pip-tools-compatible behaviour) and only replaces them
when ``--upgrade`` is passed or the inputs no longer permit the pinned version.
With a blank output there were no preferences, so uv resolved every package to
its LATEST upstream release and the check reduced to "is anything newer
upstream?" — turning red on every unrelated PR the instant any transitive dep
published a new version (a repo-wide merge deadlock). The fix seeds the temp
output with the committed lock before the identical (non-upgrade) compile.

These tests run WITHOUT a real ``uv`` (the owner PC is a thin client and uv is
not installed): they put a small FAKE ``uv`` first on ``PATH`` that faithfully
models the one behaviour the fix relies on —

  * a NON-empty (seeded) ``--output-file`` whose pins still satisfy the inputs
    is PRESERVED (preference behaviour); and
  * a package the seed does not (or can no longer) satisfy is resolved to the
    fake's configured "latest" version;
  * ``--generate-hashes`` always rewrites the resolved version's canonical hash
    (so a hand-edited hash cannot survive).

The tests then assert the SCRIPT's plumbing end to end: seeded ``--check``
PASSES when the committed lock reproduces, and FAILS on genuine input drift or a
tampered hash. The REAL-uv proof that uv honours the seeded output file runs in
CI (``api-lock-verify`` and ``api-tooling-lock-verify`` on a Linux runner with
the hash-pinned uv 0.11.28). No committed lock/manifest file is ever mutated:
every scenario operates on a throwaway fixture directory.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_REAL_LOCK_TOOLS = _SCRIPTS_DIR / "lock_tools.sh"
_REAL_LOCK_REQS = _SCRIPTS_DIR / "lock_requirements.sh"

# (script filename, input manifest name, committed lock name) for each mirror.
_SCRIPT_MATRIX = [
    pytest.param("lock_tools.sh", "requirements-tools.in", "requirements-tools.lock",
                 id="tooling-lock"),
    pytest.param("lock_requirements.sh", "requirements.in", "requirements.txt",
                 id="production-lock"),
]

# --------------------------------------------------------------------------- #
# The fake `uv`. A bash wrapper (found by the scripts' `command -v uv`) that
# execs the Python model below with whichever interpreter is available. Writing
# the logic in Python keeps the resolver model readable; the wrapper keeps it
# discoverable on PATH the same way a real `uv` console script would be.
# --------------------------------------------------------------------------- #
_FAKE_UV_WRAPPER = """#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# FAKE_UV_PYTHON is the exact interpreter running the test suite (set by the
# harness); falling back to `python3` would risk the Windows Store alias stub.
PY="${FAKE_UV_PYTHON:-python3}"
exec "$PY" "$DIR/fake_uv_impl.py" "$@"
"""

_FAKE_UV_IMPL = r'''#!/usr/bin/env python3
"""A deterministic stand-in for `uv pip compile` used only by M0-T021 tests.

Models the single documented behaviour the lock-verify fix depends on: an
existing --output-file supplies version PREFERENCES that are kept whenever they
still satisfy the input manifest; otherwise the package resolves to a
configured "latest" version (env FAKE_UV_LATEST="name=version,name2=version2").
--generate-hashes always emits the resolved version's canonical hash, so a
hand-edited hash in the seed never survives a re-resolve.
"""
import hashlib
import os
import re
import sys


def canonical_hash(name, version):
    return hashlib.sha256(("%s==%s" % (name, version)).encode()).hexdigest()


def norm(name):
    return name.strip().lower().replace("_", "-")


def ver_tuple(v):
    parts = []
    for p in re.split(r"[.\-]", v):
        parts.append((0, int(p)) if p.isdigit() else (1, p))
    return tuple(parts)


def parse_requirement(line):
    line = line.split("#", 1)[0].strip()
    if not line:
        return None
    m = re.match(r"^([A-Za-z0-9._-]+)\s*(==|>=)?\s*([A-Za-z0-9._-]+)?$", line)
    if not m:
        return None
    return norm(m.group(1)), m.group(2), m.group(3)


def parse_seed(path):
    pins = {}
    if not path or not os.path.exists(path):
        return pins
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^([A-Za-z0-9._-]+)==([A-Za-z0-9._-]+)", line.strip())
            if m:
                pins[norm(m.group(1))] = m.group(2)
    return pins


def satisfies(version, op, bound):
    if op == ">=" and bound:
        return ver_tuple(version) >= ver_tuple(bound)
    # bare requirement (no operator) => unbounded, any pin satisfies.
    return True


def load_latest():
    out = {}
    for item in os.environ.get("FAKE_UV_LATEST", "").split(","):
        item = item.strip()
        if item:
            k, v = item.split("=", 1)
            out[norm(k)] = v
    return out


def main(argv):
    if argv[:1] == ["--version"]:
        sys.stdout.write("uv 0.11.28\n")
        return 0
    if argv[:2] != ["pip", "compile"]:
        sys.stderr.write("fake uv: unsupported invocation: %r\n" % argv)
        return 2

    rest = argv[2:]
    out_file = None
    positional = []
    i = 0
    while i < len(rest):
        a = rest[i]
        if a == "--output-file":
            out_file = rest[i + 1]
            i += 2
            continue
        if a == "--python-version":
            i += 2
            continue
        if a.startswith("--"):
            i += 1
            continue
        positional.append(a)
        i += 1

    if out_file is None or not positional:
        sys.stderr.write("fake uv: need an input file and --output-file\n")
        return 2
    in_file = positional[0]

    seed = parse_seed(out_file)
    latest = load_latest()

    resolved = []
    with open(in_file, encoding="utf-8") as fh:
        for line in fh:
            req = parse_requirement(line)
            if req is None:
                continue
            name, op, bound = req
            if op == "==" and bound:
                version = bound  # exact input pin dictates the version
            else:
                seeded = seed.get(name)
                if seeded is not None and satisfies(seeded, op, bound):
                    version = seeded  # PREFERENCE: keep the committed pin
                else:
                    version = latest.get(name)
                    if version is None:
                        sys.stderr.write("fake uv: no latest for %s\n" % name)
                        return 2
            resolved.append((name, version))

    resolved.sort()
    lines = []
    for name, version in resolved:
        lines.append("%s==%s \\" % (name, version))
        lines.append("    --hash=sha256:%s" % canonical_hash(name, version))
    with open(out_file, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
'''


def _write_fake_uv(bin_dir: Path) -> None:
    bin_dir.mkdir(parents=True, exist_ok=True)
    (bin_dir / "fake_uv_impl.py").write_text(_FAKE_UV_IMPL, encoding="utf-8")
    uv = bin_dir / "uv"
    uv.write_text(_FAKE_UV_WRAPPER, encoding="utf-8", newline="\n")
    os.chmod(uv, 0o755)


def _env_with_fake_uv(bin_dir: Path, latest: str = "") -> dict:
    env = dict(os.environ)
    # Fake uv first; the running interpreter's dir guarantees python/python3.
    env["PATH"] = os.pathsep.join(
        [str(bin_dir), os.path.dirname(sys.executable), env.get("PATH", "")]
    )
    # Hand the wrapper the exact interpreter (forward slashes so Git-Bash can
    # exec a Windows path) rather than letting it resolve `python3` on PATH,
    # which on Windows may be the Microsoft Store alias stub.
    env["FAKE_UV_PYTHON"] = sys.executable.replace("\\", "/")
    env["FAKE_UV_LATEST"] = latest
    return env


class _Fixture:
    def __init__(self, root: Path, script: str, in_name: str, out_name: str):
        self.root = root
        self.bin = root / "bin"
        self.script = root / "scripts" / script
        self.in_file = root / in_name
        self.out_file = root / out_name

    def run(self, *args: str, latest: str = ""):
        return subprocess.run(
            ["bash", str(self.script), *args],
            env=_env_with_fake_uv(self.bin, latest),
            capture_output=True,
            text=True,
        )

    def generate(self, latest: str = ""):
        r = self.run(latest=latest)
        assert r.returncode == 0, f"generate failed: {r.stderr}"
        return r

    def check(self, latest: str = ""):
        return self.run("--check", latest=latest)


def _make_fixture(tmp_path: Path, script: str, in_name: str, out_name: str,
                  manifest: str) -> _Fixture:
    real = {"lock_tools.sh": _REAL_LOCK_TOOLS,
            "lock_requirements.sh": _REAL_LOCK_REQS}[script]
    fx = _Fixture(tmp_path, script, in_name, out_name)
    (tmp_path / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(real, fx.script)
    _write_fake_uv(fx.bin)
    fx.in_file.write_text(manifest, encoding="utf-8")
    return fx


# --------------------------------------------------------------------------- #
# AS-1: committed lock consistent + fake resolver reproduces the seed -> PASS.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("script,in_name,out_name", _SCRIPT_MATRIX)
def test_as1_consistent_lock_check_passes(tmp_path, script, in_name, out_name):
    fx = _make_fixture(tmp_path, script, in_name, out_name, "demo==1.0.0\n")
    fx.generate()  # write a committed lock the same way generation does
    r = fx.check()
    assert r.returncode == 0, r.stderr + r.stdout
    assert "byte-identical" in r.stdout


# --------------------------------------------------------------------------- #
# AS-2 (core fix): a NEWER version exists upstream, but the seeded committed pin
# still satisfies the inputs -> --check PASSES (does NOT pull the newer one).
# This is exactly the repo-wide-deadlock regression the fix removes.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("script,in_name,out_name", _SCRIPT_MATRIX)
def test_as2_newer_upstream_does_not_break_check(tmp_path, script, in_name, out_name):
    # Range input; committed lock generated while "latest" was 1.5.0.
    fx = _make_fixture(tmp_path, script, in_name, out_name, "demo>=1.0.0\n")
    fx.generate(latest="demo=1.5.0")
    committed = fx.out_file.read_text(encoding="utf-8")
    assert "demo==1.5.0" in committed

    # Upstream now publishes 2.0.0. The SEEDED check must keep 1.5.0 -> PASS.
    r = fx.check(latest="demo=2.0.0")
    assert r.returncode == 0, r.stderr + r.stdout
    assert "byte-identical" in r.stdout

    # Prove this is a real regression guard: an UNSEEDED (blank) resolve — the
    # pre-fix behaviour — would have pulled 2.0.0 and diverged from the lock.
    blank = tmp_path / "blank.out"
    blank.write_text("", encoding="utf-8")
    subprocess.run(
        ["bash", str(fx.bin / "uv"), "pip", "compile", "--universal",
         "--python-version", "3.12", "--generate-hashes", "--no-header",
         str(fx.in_file), "--output-file", str(blank)],
        env=_env_with_fake_uv(fx.bin, latest="demo=2.0.0"),
        capture_output=True, text=True, check=True,
    )
    assert "demo==2.0.0" in blank.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# AS-3: genuine drift — the inputs changed so the committed lock no longer
# reproduces -> --check FAILS with a diff.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("script,in_name,out_name", _SCRIPT_MATRIX)
def test_as3_genuine_input_drift_fails(tmp_path, script, in_name, out_name):
    fx = _make_fixture(tmp_path, script, in_name, out_name, "demo==1.0.0\n")
    fx.generate()
    # Someone bumped the manifest exact pin but forgot to regenerate the lock.
    fx.in_file.write_text("demo==2.0.0\n", encoding="utf-8")
    r = fx.check()
    assert r.returncode == 1, r.stdout + r.stderr
    assert "NOT byte-identical" in r.stderr
    assert ("demo==1.0.0" in r.stdout) and ("demo==2.0.0" in r.stdout)


# --------------------------------------------------------------------------- #
# AS-4: tamper — a hash line in the committed lock is altered -> --check FAILS
# (the seed's version is kept but --generate-hashes rewrites the true hash).
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("script,in_name,out_name", _SCRIPT_MATRIX)
def test_as4_tampered_hash_fails(tmp_path, script, in_name, out_name):
    fx = _make_fixture(tmp_path, script, in_name, out_name, "demo==1.0.0\n")
    fx.generate()
    text = fx.out_file.read_text(encoding="utf-8")
    assert "--hash=sha256:" in text
    # Flip one hex digit of the committed hash (in-place tamper of the lock copy
    # inside the throwaway fixture — never a real committed file).
    idx = text.index("--hash=sha256:") + len("--hash=sha256:")
    flipped = "0" if text[idx] != "0" else "1"
    tampered = text[:idx] + flipped + text[idx + 1:]
    fx.out_file.write_text(tampered, encoding="utf-8")
    r = fx.check()
    assert r.returncode == 1, r.stdout + r.stderr
    assert "NOT byte-identical" in r.stderr


# --------------------------------------------------------------------------- #
# AS-5: the age gate is untouched and still enforces the 604800s boundary. We
# import the sibling module (the same one exercised by
# test_dependency_age_gate.py, which runs in the SAME `pytest scripts/tests`
# CI step) and assert the boundary; we do NOT modify dependency_age_gate.py.
# --------------------------------------------------------------------------- #
def _load_age_gate():
    path = _SCRIPTS_DIR / "dependency_age_gate.py"
    spec = importlib.util.spec_from_file_location("dependency_age_gate_m0t021", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # Register before exec so the module's dataclasses can resolve their own
    # __module__ (scripts/ is not a package).
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_as5_age_gate_boundary_preserved():
    import datetime as dt

    age_gate = _load_age_gate()
    assert age_gate.MIN_AGE_SECONDS == 604800  # not weakened
    now = dt.datetime(2026, 7, 20, 12, 0, 0, tzinfo=dt.UTC)
    sha = "a" * 64

    def artifact(seconds_old):
        uploaded = now - dt.timedelta(seconds=seconds_old)
        return {
            "digests": {"sha256": sha},
            "upload_time_iso_8601": uploaded.isoformat().replace("+00:00", "Z"),
            "yanked": False,
        }

    pkg = age_gate.PinnedPackage("demo", "1.0.0", frozenset({sha}))
    assert age_gate.decide(pkg, [artifact(604800)], now).passed is True
    assert age_gate.decide(pkg, [artifact(604799)], now).passed is False


# --------------------------------------------------------------------------- #
# AS-6: BOTH mirror scripts received the identical seed-the-temp fix.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("real", [_REAL_LOCK_TOOLS, _REAL_LOCK_REQS],
                         ids=["lock_tools.sh", "lock_requirements.sh"])
def test_as6_both_scripts_seed_the_temp(real):
    text = real.read_text(encoding="utf-8")
    # The seeding copy must appear inside the --check branch, before the compile.
    check_idx = text.index('MODE')
    seed_idx = text.index('cp "${OUT_FILE}" "${TMP}"')
    compile_idx = text.index('--output-file "${TMP}"')
    assert check_idx < seed_idx < compile_idx
    # And no --upgrade sneaked into executable code (comments may mention it).
    code_lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("#")]
    assert all("--upgrade" not in ln for ln in code_lines)
