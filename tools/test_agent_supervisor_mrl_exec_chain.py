"""M0-T136 C-B2: executable-chain resolution + immediately-before-spawn binding
(D-024-R561..R565). Every positive contract has a paired negative/mutation case."""
from __future__ import annotations

import os
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools.agent_supervisor import mrl_exec_chain as mec  # noqa: E402
from tools.agent_supervisor.mrl_worker_result import ContractError  # noqa: E402

# The two shim texts are verbatim copies of the npm-generated wrappers measured on the
# owner's machine (claude.cmd -> native exe; codex.cmd -> node -> codex.js).
NATIVE_SHIM = (
    '@ECHO off\r\nGOTO start\r\n:find_dp0\r\nSET dp0=%~dp0\r\nEXIT /b\r\n:start\r\nSETLOCAL\r\n'
    'CALL :find_dp0\r\n"%dp0%\\node_modules\\@anthropic-ai\\claude-code\\bin\\claude.exe"   %*\r\n'
)
NODE_SHIM = (
    '@ECHO off\r\nGOTO start\r\n:find_dp0\r\nSET dp0=%~dp0\r\nEXIT /b\r\n:start\r\nSETLOCAL\r\n'
    'CALL :find_dp0\r\n\r\nIF EXIST "%dp0%\\node.exe" (\r\n  SET "_prog=%dp0%\\node.exe"\r\n) ELSE (\r\n'
    '  SET "_prog=node"\r\n  SET PATHEXT=%PATHEXT:;.JS;=;%\r\n)\r\n\r\nendLocal & goto #_undefined_# 2>NUL '
    '|| title %COMSPEC% & "%_prog%"  "%dp0%\\node_modules\\@openai\\codex\\bin\\codex.js" %*\r\n'
)
WIN = "win32"


def _write(path: pathlib.Path, data: "bytes | str") -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        path.write_text(data, encoding="utf-8")
    else:
        path.write_bytes(data)
    return path


@pytest.fixture
def native(tmp_path: pathlib.Path) -> pathlib.Path:
    return _write(tmp_path / "bin" / "claude.exe", b"MZ-native-claude-binary-bytes")


@pytest.fixture
def claude_shim(tmp_path: pathlib.Path) -> "tuple[pathlib.Path, pathlib.Path]":
    shim = _write(tmp_path / "npm" / "claude.cmd", NATIVE_SHIM)
    target = _write(tmp_path / "npm" / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe",
                    b"MZ-claude-native-from-shim")
    return shim, target


@pytest.fixture
def codex_shim(tmp_path: pathlib.Path) -> dict[str, pathlib.Path]:
    shim = _write(tmp_path / "npm" / "codex.cmd", NODE_SHIM)
    pkg = tmp_path / "npm" / "node_modules" / "@openai" / "codex"
    entry = _write(pkg / "bin" / "codex.js", "#!/usr/bin/env node\n// entry\n")
    _write(pkg / "package.json", '{"name": "@openai/codex", "version": "0.146.0"}')
    vendor = _write(pkg / "node_modules" / "@openai" / "codex-win32-x64" / "vendor" / "x86_64-pc-windows-msvc"
                    / "bin" / "codex.exe", b"MZ-codex-vendor-binary")
    _write(pkg / "node_modules" / "@openai" / "codex-win32-x64" / "package.json",
           '{"name": "@openai/codex-win32-x64"}')
    node = _write(tmp_path / "nodejs" / "node.exe", b"MZ-node-runtime")
    return {"shim": shim, "entry": entry, "vendor": vendor, "node": node, "pkg": pkg}


def _which_for(node: pathlib.Path):
    return lambda name: str(node) if name == "node" else None


# ---------------------------------------------------------------- resolution

class TestResolution:
    def test_native_executable_is_a_one_link_chain(self, native):
        chain = mec.resolve_chain(str(native), "claude", sys_platform=WIN)
        assert chain.shape == mec.SHAPE_NATIVE
        assert chain.links == (("claude-executable", str(native)),)

    def test_native_shim_resolves_wrapper_then_runtime(self, claude_shim):
        shim, target = claude_shim
        chain = mec.resolve_chain(str(shim), "claude", sys_platform=WIN)
        assert chain.shape == mec.SHAPE_SHIM_NATIVE
        assert chain.links == (("claude-wrapper", str(shim)), ("claude-runtime", str(target)))

    def test_node_shim_resolves_wrapper_node_entrypoint_vendor(self, codex_shim):
        chain = mec.resolve_chain(str(codex_shim["shim"]), "codex", which=_which_for(codex_shim["node"]),
                                  sys_platform=WIN, machine="AMD64")
        assert chain.shape == mec.SHAPE_SHIM_NODE_VENDOR
        assert [role for role, _ in chain.links] == ["codex-wrapper", "codex-runtime", "codex-entrypoint",
                                                     "codex-vendor"]
        assert chain.links[1][1] == str(codex_shim["node"])
        assert chain.links[2][1] == str(codex_shim["entry"])
        assert chain.links[3][1] == str(codex_shim["vendor"])

    def test_node_shim_prefers_dp0_node_exe_when_present(self, codex_shim):
        local = _write(codex_shim["shim"].parent / "node.exe", b"MZ-local-node")
        chain = mec.resolve_chain(str(codex_shim["shim"]), "codex", which=_which_for(codex_shim["node"]),
                                  sys_platform=WIN, machine="AMD64")
        assert chain.links[1][1] == str(local)

    def test_node_shim_without_node_anywhere_refuses(self, codex_shim):
        with pytest.raises(ContractError, match="needs `node` on PATH"):
            mec.resolve_chain(str(codex_shim["shim"]), "codex", which=lambda _n: None,
                              sys_platform=WIN, machine="AMD64")

    def test_vendor_missing_refuses_instead_of_partial_chain(self, codex_shim):
        codex_shim["vendor"].unlink()
        with pytest.raises(ContractError, match="vendor binary"):
            mec.resolve_chain(str(codex_shim["shim"]), "codex", which=_which_for(codex_shim["node"]),
                              sys_platform=WIN, machine="AMD64")

    def test_vendor_fallback_under_package_vendor_dir(self, codex_shim):
        # No platform package anywhere on the ancestor walk -> codex.js falls back to <pkg>/vendor.
        import shutil
        shutil.rmtree(codex_shim["pkg"] / "node_modules")
        fallback = _write(codex_shim["pkg"] / "vendor" / "x86_64-pc-windows-msvc" / "bin" / "codex.exe",
                          b"MZ-fallback")
        chain = mec.resolve_chain(str(codex_shim["shim"]), "codex", which=_which_for(codex_shim["node"]),
                                  sys_platform=WIN, machine="AMD64")
        assert chain.links[3][1] == str(fallback)

    def test_non_codex_entrypoint_has_no_vendor_link(self, codex_shim):
        (codex_shim["pkg"] / "package.json").write_text('{"name": "@other/tool"}', encoding="utf-8")
        chain = mec.resolve_chain(str(codex_shim["shim"]), "codex", which=_which_for(codex_shim["node"]),
                                  sys_platform=WIN, machine="AMD64")
        assert chain.shape == mec.SHAPE_SHIM_NODE and len(chain.links) == 3

    def test_cmd_without_dp0_reference_is_not_a_shim(self, tmp_path):
        bogus = _write(tmp_path / "x.cmd", "@echo off\r\nclaude %*\r\n")
        with pytest.raises(ContractError, match="not a parseable npm shim"):
            mec.resolve_chain(str(bogus), "claude", sys_platform=WIN)

    def test_shim_targeting_missing_file_refuses(self, claude_shim):
        shim, target = claude_shim
        target.unlink()
        with pytest.raises(ContractError, match="targets missing file"):
            mec.resolve_chain(str(shim), "claude", sys_platform=WIN)

    @pytest.mark.parametrize("bad", ["", "   "])
    def test_empty_executable_refuses(self, bad):
        with pytest.raises(ContractError):
            mec.resolve_chain(bad, "claude", sys_platform=WIN)

    def test_relative_path_refuses(self):
        with pytest.raises(ContractError, match="absolute"):
            mec.resolve_chain("claude.exe", "claude", sys_platform=WIN)

    def test_missing_file_refuses(self, tmp_path):
        with pytest.raises(ContractError, match="is not a file"):
            mec.resolve_chain(str(tmp_path / "nope.exe"), "claude", sys_platform=WIN)

    def test_unknown_kind_refuses(self, native):
        with pytest.raises(ContractError, match="unknown chain kind"):
            mec.resolve_chain(str(native), "gemini", sys_platform=WIN)

    def test_unsupported_suffix_on_windows_refuses(self, tmp_path):
        js = _write(tmp_path / "claude.ps1", "x")
        with pytest.raises(ContractError, match="unsupported suffix"):
            mec.resolve_chain(str(js), "claude", sys_platform=WIN)

    def test_triple_map_and_unsupported_host(self):
        assert mec.codex_target_triple("win32", "AMD64") == "x86_64-pc-windows-msvc"
        assert mec.codex_target_triple("linux", "aarch64") == "aarch64-unknown-linux-musl"
        with pytest.raises(ContractError):
            mec.codex_target_triple("win32", "i686")
        with pytest.raises(ContractError):
            mec.codex_target_triple("freebsd", "AMD64")


# ---------------------------------------------------------------- binding now (no cache)

class TestBindingNow:
    def test_bind_then_verify_matches(self, claude_shim):
        chain = mec.resolve_chain(str(claude_shim[0]), "claude", sys_platform=WIN)
        identity = mec.bind_chain_now(chain)
        assert mec.verify_chain_now(chain, identity.combined_sha256).combined_sha256 == identity.combined_sha256
        record = mec.chain_record(chain, identity)
        assert record["shape"] == mec.SHAPE_SHIM_NATIVE and len(record["links"]) == 2
        assert all(len(link["sha256"]) == 64 for link in record["links"])

    def test_same_size_restored_mtime_replacement_is_detected(self, claude_shim):
        shim, target = claude_shim
        chain = mec.resolve_chain(str(shim), "claude", sys_platform=WIN)
        pinned = mec.bind_chain_now(chain).combined_sha256
        st = target.stat()
        original = target.read_bytes()
        replaced = original[:-1] + bytes([original[-1] ^ 0x01])   # identical size, one bit flipped
        target.write_bytes(replaced)
        os.utime(target, ns=(st.st_atime_ns, st.st_mtime_ns))     # restore mtime exactly
        assert target.stat().st_size == st.st_size and target.stat().st_mtime_ns == st.st_mtime_ns
        with pytest.raises(ContractError, match="does not match the pinned"):
            mec.verify_chain_now(chain, pinned)

    def test_wrapper_retargeting_is_detected(self, claude_shim, tmp_path):
        shim, _target = claude_shim
        chain = mec.resolve_chain(str(shim), "claude", sys_platform=WIN)
        pinned = mec.bind_chain_now(chain).combined_sha256
        other = _write(tmp_path / "npm" / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "other.exe",
                       b"MZ-other")
        shim.write_text(NATIVE_SHIM.replace("claude.exe", "other.exe"), encoding="utf-8")
        rechain = mec.resolve_chain(str(shim), "claude", sys_platform=WIN)
        assert rechain.links[1][1] == str(other)
        with pytest.raises(ContractError, match="does not match the pinned"):
            mec.verify_chain_now(rechain, pinned)
        # Even verifying the OLD chain object refuses, because the wrapper bytes changed.
        with pytest.raises(ContractError, match="does not match the pinned"):
            mec.verify_chain_now(chain, pinned)

    def test_entrypoint_replacement_is_detected(self, codex_shim):
        chain = mec.resolve_chain(str(codex_shim["shim"]), "codex", which=_which_for(codex_shim["node"]),
                                  sys_platform=WIN, machine="AMD64")
        pinned = mec.bind_chain_now(chain).combined_sha256
        codex_shim["entry"].write_text("#!/usr/bin/env node\n// tampered entry\n", encoding="utf-8")
        with pytest.raises(ContractError, match="does not match the pinned"):
            mec.verify_chain_now(chain, pinned)

    def test_vendor_binary_replacement_is_detected(self, codex_shim):
        chain = mec.resolve_chain(str(codex_shim["shim"]), "codex", which=_which_for(codex_shim["node"]),
                                  sys_platform=WIN, machine="AMD64")
        pinned = mec.bind_chain_now(chain).combined_sha256
        codex_shim["vendor"].write_bytes(b"MZ-codex-vendor-binarZ")
        with pytest.raises(ContractError, match="does not match the pinned"):
            mec.verify_chain_now(chain, pinned)

    def test_verify_without_pinned_identity_refuses(self, native):
        chain = mec.resolve_chain(str(native), "claude", sys_platform=WIN)
        for bad in ("", None, "abc", "x" * 63):
            with pytest.raises(ContractError, match="no pinned 64-hex"):
                mec.verify_chain_now(chain, bad)  # type: ignore[arg-type]

    def test_every_call_rehashes_no_cache(self, native, monkeypatch):
        chain = mec.resolve_chain(str(native), "claude", sys_platform=WIN)
        calls = {"n": 0}
        real = mec.bind_executable_chain

        def counting(links):
            calls["n"] += 1
            return real(links)

        monkeypatch.setattr(mec, "bind_executable_chain", counting)
        monkeypatch.setattr(mec, "verify_executable_chain",
                            lambda links, exp: counting(links))
        mec.bind_chain_now(chain)
        mec.bind_chain_now(chain)
        mec.verify_chain_now(chain, "0" * 64)
        assert calls["n"] == 3


# ---------------------------------------------------------------- child env

class TestChildEnv:
    def test_updater_disabled_passes(self):
        mec.verify_child_env({"DISABLE_AUTOUPDATER": "1", "PATH": "x"})

    @pytest.mark.parametrize("env", [
        {"PATH": "x"},                                     # re-enabled by omission
        {"DISABLE_AUTOUPDATER": "0"},                      # re-enabled explicitly
        {"DISABLE_AUTOUPDATER": "true"},                   # wrong literal
        {"DISABLE_AUTOUPDATER": "1", "DISABLE_UPDATES": "1"},  # prohibited blunt switch (R280)
    ])
    def test_updater_reenablement_refuses(self, env):
        with pytest.raises(ContractError):
            mec.verify_child_env(env)

    def test_none_env_refuses(self):
        with pytest.raises(ContractError, match="mapping passed to Popen"):
            mec.verify_child_env(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------- runtime identity

class TestRuntimeIdentity:
    def test_parse_version_forms(self):
        assert mec.parse_version("2.1.252 (Claude Code)") == "2.1.252"
        assert mec.parse_version("codex-cli 0.146.0\n") == "0.146.0"
        assert mec.parse_version("") == ""
        assert mec.parse_version("no version here") == ""

    def test_observe_version_uses_bound_chain_head(self, native):
        chain = mec.resolve_chain(str(native), "claude", sys_platform=WIN)
        seen = {}

        def run(argv):
            seen["argv"] = list(argv)
            return 0, "2.1.252 (Claude Code)\n", ""

        assert mec.observe_version(chain, run=run) == "2.1.252"
        assert seen["argv"] == [str(native), "--version"]

    def test_observe_version_nonzero_or_raise_yields_empty(self, native):
        chain = mec.resolve_chain(str(native), "claude", sys_platform=WIN)
        assert mec.observe_version(chain, run=lambda a: (1, "2.1.252", "")) == ""

        def boom(_a):
            raise OSError("cannot exec")

        assert mec.observe_version(chain, run=boom) == ""

    def test_observed_model_helper_is_gone(self):
        # M0-T142 (D-024-R686): the exactly-one-modelUsage-key helper was deleted -
        # modelUsage is a session-wide aggregate; the one-shot settlement proves the
        # primary model via mrl_runtime_identity.verify_primary_model instead.
        assert not hasattr(mec, "observed_model_from_result")
        assert "observed_model_from_result" not in mec.__all__

    def test_verify_runtime_identity_pass_and_mismatches(self):
        mec.verify_runtime_identity(expected_model="m", expected_version="2.1.252",
                                    observed_model="m", observed_version="2.1.252")
        with pytest.raises(ContractError, match="model"):
            mec.verify_runtime_identity(expected_model="m", expected_version="2.1.252",
                                        observed_model="other", observed_version="2.1.252")
        with pytest.raises(ContractError, match="version"):
            mec.verify_runtime_identity(expected_model="m", expected_version="2.1.252",
                                        observed_model="m", observed_version="2.1.251")
        with pytest.raises(ContractError, match="reported no"):
            mec.verify_runtime_identity(expected_model="m", expected_version="2.1.252",
                                        observed_model="", observed_version="2.1.252")
