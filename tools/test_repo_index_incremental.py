#!/usr/bin/env python3
"""M0-T064 Unit A2 tests: incremental indexing (D-013-R032/R037/R079 et al.).

Two proofs carry the unit:
  * PARITY (D-013-R079/R037): the incremental export equals a clean full rebuild
    (via the REAL generator) byte-for-byte, across cold build, warm reuse, and
    every change class.
  * SELECTIVE REPARSE (D-013-R032/R059): a warm no-change run reparses zero
    files; a local content edit reparses ONLY the changed files (not a full
    rebuild); structural changes and global invalidators full-rebuild with a
    recorded reason. Plus exact change classification, the deterministic
    importer closure over real edges, fail-closed on a corrupt generation,
    idempotent retry, rich run records (R024/R052), and append-only external
    telemetry (R050). Deterministic, stdlib-only; the cache base is a temp dir.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools import repo_fingerprint as rf  # noqa: E402
from tools import repo_index_assembly as asm  # noqa: E402
from tools import repo_index_cache as ric  # noqa: E402
from tools import repo_index_incremental as inc  # noqa: E402


def _git(repo: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class RepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._cbase = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self._tmp.name) / "repo"
        (self.repo / "services" / "api").mkdir(parents=True)
        _git(self.repo, "init", "-q")
        _git(self.repo, "config", "user.email", "t@t.t")
        _git(self.repo, "config", "user.name", "t")
        self.cbase = self._cbase.name
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(self._cbase.cleanup)

    def add(self, rel: str, text: str, msg: str = "c") -> None:
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-q", "-m", msg)

    def build(self, **kw):
        return inc.build_incremental(self.repo, cache_base=self.cbase, **kw)

    def full_bytes(self) -> bytes:
        return inc.clean_full_build_bytes(self.repo)


class ParityInvariant(RepoCase):
    """D-013-R037/R079: incremental export == clean full rebuild, byte-identical."""

    def setUp(self) -> None:
        super().setUp()
        self.add("services/api/a.py", "def f():\n    return g()\n")
        self.add("services/api/g.py", "def g():\n    return 1\n")

    def test_cold_build_matches_full(self) -> None:
        r = self.build()
        self.assertFalse(r.reused)
        self.assertEqual(r.mode, "full")
        self.assertEqual(r.export_bytes, self.full_bytes())

    def test_warm_reuse_matches_full(self) -> None:
        first = self.build()
        warm = self.build()
        self.assertTrue(warm.reused)
        self.assertEqual(warm.mode, "reuse")
        self.assertEqual(warm.export_bytes, first.export_bytes)
        self.assertEqual(warm.export_bytes, self.full_bytes())

    def test_parity_holds_after_each_change_class(self) -> None:
        self.build()  # seed
        # content change -> INCREMENTAL, reparse only the one changed file
        self.add("services/api/g.py", "def g():\n    return 2\n", "modify")
        r = self.build()
        self.assertFalse(r.reused)
        self.assertEqual(r.mode, "incremental")
        self.assertIn("services/api/g.py", r.change_set.content_modified)
        self.assertEqual(r.files_parsed, 1)          # D-013-R032: only the change
        self.assertGreaterEqual(r.files_reused, 1)   # the rest reused
        self.assertEqual(r.export_bytes, self.full_bytes())
        # add -> structural -> full rebuild
        self.add("services/api/h.py", "def h():\n    return 3\n", "add")
        r = self.build()
        self.assertEqual(r.mode, "full")
        self.assertIn("services/api/h.py", r.change_set.added)
        self.assertEqual(r.export_bytes, self.full_bytes())
        # delete -> structural -> full rebuild
        (self.repo / "services" / "api" / "h.py").unlink()
        _git(self.repo, "commit", "-aqm", "del")
        r = self.build()
        self.assertEqual(r.mode, "full")
        self.assertIn("services/api/h.py", r.change_set.deleted)
        self.assertEqual(r.export_bytes, self.full_bytes())


class SelectiveReparse(RepoCase):
    """D-013-R032/R059: reparse only changed files; no full rebuild on a local edit."""

    def setUp(self) -> None:
        super().setUp()
        for i in range(5):
            self.add(f"services/api/m{i}.py", f"X{i} = {i}\n")

    def test_warm_no_change_reparses_zero(self) -> None:
        self.build()
        warm = self.build()
        self.assertTrue(warm.reused)
        self.assertEqual(warm.files_parsed, 0)       # R059: zero reparse
        self.assertEqual(warm.telemetry["cache_result"], "hit")

    def test_local_edit_reparses_only_changed_no_full_rebuild(self) -> None:
        self.build()
        self.add("services/api/m2.py", "X2 = 999\n", "edit m2")
        r = self.build()
        self.assertEqual(r.mode, "incremental")      # R059: not a full rebuild
        self.assertEqual(r.change_set.content_modified, ["services/api/m2.py"])
        self.assertEqual(r.files_parsed, 1)          # R032: only m2
        self.assertEqual(r.files_reused, 4)          # the other four reused
        self.assertEqual(r.export_bytes, self.full_bytes())

    def test_two_file_edit_reparses_two(self) -> None:
        self.build()
        (self.repo / "services/api/m1.py").write_text("X1 = 11\n", newline="\n")
        (self.repo / "services/api/m3.py").write_text("X3 = 33\n", newline="\n")
        _git(self.repo, "commit", "-aqm", "edit two")
        r = self.build()
        self.assertEqual(r.mode, "incremental")
        self.assertEqual(r.files_parsed, 2)
        self.assertEqual(r.export_bytes, self.full_bytes())


class GeneratorFallback(RepoCase):
    """Unknown generator version -> fail-safe full rebuild via the REAL generator,
    still byte-identical; no silent divergence."""

    def setUp(self) -> None:
        super().setUp()
        self.add("services/api/a.py", "Z = 1\n")

    def test_unrecognized_generator_falls_back_to_real_builder(self) -> None:
        from tools.code_graph import generate as cg
        original = cg.GENERATOR_VERSION
        try:
            cg.GENERATOR_VERSION = original + "-unknown"
            self.assertFalse(asm.generator_recognized())
            r = self.build()
            self.assertEqual(r.mode, "full")
            self.assertIn("unrecognized generator", r.rebuild_reason)
            self.assertEqual(r.export_bytes, self.full_bytes())
        finally:
            cg.GENERATOR_VERSION = original

    def test_assembly_refuses_unknown_generator(self) -> None:
        from tools.code_graph import generate as cg
        original = cg.SCHEMA_VERSION
        try:
            cg.SCHEMA_VERSION = original + "-x"
            with self.assertRaises(asm.UnknownGeneratorError):
                asm.drive(self.repo)
        finally:
            cg.SCHEMA_VERSION = original


class ChangeClassification(RepoCase):
    def test_rename_is_detected_by_content_digest(self) -> None:
        self.add("services/api/a.py", "def a():\n    return 1\n")
        self.build()
        _git(self.repo, "mv", "services/api/a.py", "services/api/b.py")
        _git(self.repo, "commit", "-qm", "rename")
        r = self.build()
        self.assertIn(("services/api/a.py", "services/api/b.py"),
                      r.change_set.renamed)
        self.assertNotIn("services/api/b.py", r.change_set.added)
        self.assertNotIn("services/api/a.py", r.change_set.deleted)
        self.assertEqual(r.mode, "full")            # rename is structural
        self.assertEqual(r.export_bytes, self.full_bytes())

    def test_global_invalidator_forces_full_rebuild(self) -> None:
        self.add("services/api/a.py", "X = 1\n")
        self.build()
        fp = rf.compute_fingerprint(self.repo)
        prior = {"files": [e.to_dict() for e in fp.file_manifest],
                 "config_versions": {**fp.config_versions, "fingerprint": "0.0.0"}}
        cs = inc.classify_changes(prior, fp)
        self.assertTrue(cs.global_invalidators)
        self.assertTrue(cs.is_structural())

    def test_metadata_only_change_is_classified_separately(self) -> None:
        self.add("services/api/a.py", "X = 1\n")
        fp1 = rf.compute_fingerprint(self.repo)
        prior = {"files": [e.to_dict() for e in fp1.file_manifest],
                 "config_versions": fp1.config_versions}
        import copy
        cur = copy.deepcopy(fp1)
        cur.file_manifest[0].mode["is_symlink"] = not cur.file_manifest[0].mode["is_symlink"]
        cs = inc.classify_changes(prior, cur)
        self.assertIn(fp1.file_manifest[0].path, cs.metadata_modified)
        self.assertNotIn(fp1.file_manifest[0].path, cs.content_modified)


class ImporterClosure(RepoCase):
    def test_importer_closure_is_transitive_and_deterministic(self) -> None:
        # bundles keyed by file; import edges resolve `to` a target FILE path.
        bundles = {
            "a.py": {"import_edges": []},
            "b.py": {"import_edges": [{"to": "a.py"}]},   # b imports a
            "c.py": {"import_edges": [{"to": "b.py"}]},   # c imports b
            "d.py": {"import_edges": [{"to": "external:x"}]},  # unrelated
        }
        inputs = ["a.py", "b.py", "c.py", "d.py"]
        closure = inc.importer_closure({"a.py"}, bundles, inputs)
        self.assertEqual(closure, {"a.py", "b.py", "c.py"})
        self.assertEqual(inc.importer_closure({"a.py"}, bundles, inputs), closure)

    def test_closure_on_real_bundles(self) -> None:
        # a real repo where a imports g; editing g must flag a as affected.
        self.add("services/api/g.py", "def g():\n    return 1\n")
        self.add("services/api/a.py", "from services.api.g import g\n")
        self.build()
        self.add("services/api/g.py", "def g():\n    return 2\n", "edit g")
        r = self.build()
        self.assertEqual(r.mode, "incremental")
        self.assertIn("services/api/a.py", r.affected_files)


class RunRecordAndTelemetry(RepoCase):
    """D-013-R024/R052 rich run record; D-013-R050 append-only external JSONL."""

    def setUp(self) -> None:
        super().setUp()
        self.add("services/api/a.py", "X = 1\n")

    def test_run_record_has_required_fields(self) -> None:
        r = self.build()
        rec = r.telemetry
        for key in ("schema", "unit_id", "repo_identity", "head_sha", "branch",
                    "dirty_state_digest", "source_manifest_digest",
                    "snapshot_fingerprint", "versions", "generator_identity",
                    "census", "change_set", "mode", "cache_result",
                    "rebuild_reason", "files_examined", "files_parsed",
                    "files_reused", "affected_dependents", "graph_nodes_before",
                    "graph_edges_before", "graph_nodes_after", "graph_edges_after",
                    "export_digest", "estimated_tokens", "provider_tokens"):
            self.assertIn(key, rec, f"missing run-record field {key!r}")
        self.assertIsNone(rec["estimated_tokens"])       # never fabricated
        self.assertIsNone(rec["provider_tokens"])

    def test_no_absolute_path_in_record(self) -> None:
        r = self.build()
        blob = json.dumps(r.telemetry)
        self.assertNotIn(str(self.repo), blob)           # redacted: identity is a sha

    def test_telemetry_is_appended_jsonl(self) -> None:
        self.build()
        self.build()                                     # a second run appends
        cache = ric.IndexCache(self.repo, base=self.cbase)
        log = cache.root / inc.TELEMETRY_FILENAME
        lines = [ln for ln in log.read_text(encoding="utf-8").splitlines() if ln]
        self.assertGreaterEqual(len(lines), 2)           # append-only
        for ln in lines:
            json.loads(ln)                               # each line is valid JSON

    def test_persist_telemetry_can_be_disabled(self) -> None:
        r = self.build(persist_telemetry=False)
        cache = ric.IndexCache(self.repo, base=self.cbase)
        self.assertFalse((cache.root / inc.TELEMETRY_FILENAME).exists())
        self.assertTrue(r.telemetry)                     # record still returned


class ReuseAndRecovery(RepoCase):
    def setUp(self) -> None:
        super().setUp()
        self.add("services/api/a.py", "X = 1\n")

    def test_unchanged_snapshot_reuses_without_rebuild(self) -> None:
        self.build()
        r = self.build()
        self.assertTrue(r.reused)
        self.assertEqual(r.telemetry["cache_result"], "hit")
        self.assertEqual(r.telemetry["files_parsed"], 0)

    def test_idempotent_retry(self) -> None:
        a = self.build()
        b = self.build()
        self.assertEqual(a.export_digest(), b.export_digest())

    def test_corrupt_generation_is_recovered_and_rebuilt(self) -> None:
        self.build()
        cache = ric.IndexCache(self.repo, base=self.cbase)
        cur = cache.load_current()
        (cur.path / "payload.json").write_text('{"broken": true}', encoding="utf-8")
        r = self.build()
        self.assertEqual(r.export_bytes, self.full_bytes())

    def test_full_rebuild_always_available_as_reference(self) -> None:
        self.build()
        self.assertEqual(inc.clean_full_build_bytes(self.repo), self.full_bytes())


class RealRepoSmoke(unittest.TestCase):
    def test_parity_on_this_repo(self) -> None:
        root = pathlib.Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as cbase:
            r = inc.build_incremental(root, cache_base=cbase, persist_telemetry=False)
            self.assertEqual(r.export_bytes, inc.clean_full_build_bytes(root))
            warm = inc.build_incremental(root, cache_base=cbase, persist_telemetry=False)
            self.assertTrue(warm.reused)
            self.assertEqual(warm.files_parsed, 0)


if __name__ == "__main__":
    unittest.main()
