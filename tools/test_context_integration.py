#!/usr/bin/env python3
"""M0-T075 integration + adversarial tests (D-018 reviewer proofs 1-8).

Runnable as ``python tools/test_context_integration.py`` or under pytest.
Covers the proofs the fresh reviewer must reproduce: real-task compilation
evidence, enforceable insufficiency, the two-writer lost-update race,
containment refusals (absolute/traversal/junction) without path leaks, the
entry point actually invoking the integrated compiler, and real retention.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from tools import context_paths as cpaths  # noqa: E402
from tools import repo_index_cache as ric  # noqa: E402

def _write(root: str, rel: str, content: str) -> str:
    p = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(content.encode("utf-8"))
    return p


class Proof1RealTaskCompile(unittest.TestCase):
    """Proof 1 on THIS repository's real accepted task M0-T066."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._out = tempfile.TemporaryDirectory()
        cls._cache = tempfile.TemporaryDirectory()
        p = subprocess.run(
            [sys.executable, os.path.join(_HERE, "context_pack.py"),
             "--task", "M0-T066", "--role", "worker", "--provider", "claude",
             "--max-bytes", "500000", "--out", cls._out.name,
             "--repo", _ROOT, "--index-cache-base", cls._cache.name,
             "--no-index-telemetry"], capture_output=True, text=True)
        cls.exit = p.returncode
        with open(os.path.join(cls._out.name, "context.meta.json"),
                  encoding="utf-8") as fh:
            cls.meta = json.load(fh)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._out.cleanup()
        cls._cache.cleanup()

    def test_real_paths_resolve_and_requirements_present(self) -> None:
        self.assertEqual(self.exit, 0)
        integ = self.meta["integration"]
        self.assertIn("tools/subsystem_resolver.py",
                      integ["implementation_paths"])
        req = integ["requirements"]
        self.assertTrue(req["in_regime"])
        self.assertGreaterEqual(len(req["applicable_ids"]), 20)
        groups = {f["group"] for f in self.meta["included_files"]}
        self.assertIn("requirements", groups)
        self.assertIn("source_excerpts", groups)  # >=1 authoritative excerpt
        self.assertTrue(self.meta["sufficiency"]["code_evidence_resolved"])

    def test_prose_is_never_a_literal_seed(self) -> None:
        # every prose candidate is recorded, and NO whole prose sentence
        # appears as a seed — only strict extracted, existing paths do.
        integ = self.meta["integration"]
        for rec in integ["prose_extraction"]:
            self.assertNotIn(" ", rec["token"])  # tokens, never sentences
        for q in self.meta["graph_queries"]:
            self.assertNotIn(" ", q["seed"])

    def test_unresolved_seeds_recorded(self) -> None:
        self.assertIsInstance(self.meta["integration"]["unresolved_seeds"], list)


class Proof3TwoWriterRace(unittest.TestCase):
    """Proof 3: two synchronized writers cannot lose a node (D-018-R027..R030).

    The EXACT stale-read/lost-update interleave: writer A performs its
    load-current, then writer B fully promotes, then A proceeds. Before the
    M0-T075 fix both calls reported `promoted` and B's node vanished from the
    final generation; now the span holds the store lock, so B's interleaved
    promotion receives `concurrent_writer` and succeeds on retry — both nodes
    survive."""

    def test_synchronized_writers_cannot_lose_a_node(self) -> None:
        from tools import memory_digest as md
        from tools import memory_graph as mg
        from tools.subsystem_entities import AuthoritativeIndexes
        from tools.subsystem_resolver import load_map, version_stamp

        with tempfile.TemporaryDirectory() as root, \
             tempfile.TemporaryDirectory() as store_base:
            _write(root, "services/api/x.py", "def x():\n    return 1\n")
            _write(root, ".claude/agents/qa-engineer.md", "# qa\n")
            _write(root, "project-control/master_plan.json",
                   json.dumps({"milestones": [{"id": "M0"}]}))
            _write(root, "project-control/tasks/M0-T001.json", json.dumps(
                {"task_id": "M0-T001", "milestone_id": "M0",
                 "allowed_paths": ["services/api/x.py"],
                 "directive_refs": [{"directive_id": "D-900",
                                     "requirement_ids": "ALL"}]}))
            _write(root, "project-control/directives/index.json",
                   json.dumps({"directives": [{"directive_id": "D-900"}]}))
            _write(root, "project-control/directives/D-900-t/requirements.json",
                   json.dumps({"requirements": [{"id": "D-900-R001", "text": "t"}]}))
            map_path = _write(root, "m.json", json.dumps(
                {"map_schema_version": "1.0.0", "map_version": "0.0.1",
                 "rules": [{"subsystem_id": "services/api",
                            "prefix": "services/api"}]}))

            stamp = version_stamp(load_map(root, map_path))
            idx = AuthoritativeIndexes.load(root).digests()

            def make(outcome: str) -> dict:
                doc = {"schema_version": md.DIGEST_SCHEMA_VERSION,
                       "digest_id": "", "task_id": "M0-T001",
                       "requirement_ids": ["D-900-R001"],
                       "files": [{"path": "services/api/x.py",
                                  "content_digest": None}],
                       "agent": "qa-engineer", "outcome": outcome,
                       "repo_sha": "a" * 40,
                       "source_manifest_fingerprint": None, "branch": "b",
                       "task_index_digest": idx["task_index_digest"],
                       "directive_index_digest": idx["directive_index_digest"],
                       "resolver_version": stamp["resolver_version"],
                       "map_version": stamp["map_version"],
                       "map_digest": stamp["map_digest"],
                       "evidence_refs": [], "unresolved_links": [],
                       "advisory_tags": []}
                doc["digest_id"] = md.compute_digest_id(doc)
                return doc

            doc_a, doc_b = make("PASS"), make("INFO")
            a_loaded = threading.Event()
            b_done = threading.Event()
            b_results: list = []

            real_load = ric.IndexCache.load_current
            first_load = {"seen": False}

            def hooked_load(store_self):
                result = real_load(store_self)
                # Only writer A's FIRST in-transaction load triggers the race.
                if not first_load["seen"]:
                    first_load["seen"] = True
                    a_loaded.set()
                    b_done.wait(timeout=30)  # A pauses mid-transaction
                return result

            def writer_b():
                a_loaded.wait(timeout=30)
                try:  # B runs while A holds the transaction span
                    b_results.append(mg.promote_digest(
                        doc_b, root, base=store_base, map_path=map_path))
                except ric.CacheError as exc:
                    b_results.append({"status": "refused", "code": exc.code})
                finally:
                    b_done.set()

            t = threading.Thread(target=writer_b)
            t.start()
            with unittest.mock.patch.object(ric.IndexCache, "load_current",
                                            hooked_load):
                res_a = mg.promote_digest(doc_a, root, base=store_base,
                                          map_path=map_path)
            t.join(timeout=30)

            self.assertEqual(res_a["status"], "promoted")
            self.assertEqual(len(b_results), 1)
            self.assertEqual(b_results[0].get("code"), "concurrent_writer",
                             f"B must be explicitly refused, got {b_results[0]}")
            # B succeeds on RETRY after A finished — both nodes survive.
            res_b = mg.promote_digest(doc_b, root, base=store_base,
                                      map_path=map_path)
            self.assertEqual(res_b["status"], "promoted")
            store = mg.memory_store(root, base=store_base)
            nodes = store.load_current().load_payload()["nodes"]
            self.assertIn(doc_a["digest_id"], nodes)
            self.assertIn(doc_b["digest_id"], nodes)
            self.assertEqual(len(nodes), 2)  # a lost update is impossible


class Proof4Containment(unittest.TestCase):
    """Proof 4: absolute/traversal/junction escapes refuse without leaking."""

    def test_shared_rule_refuses_every_form(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            _write(root, "docs/ok.md", "fine\n")
            for bad in ("C:/Windows/win.ini", "/etc/passwd", "docs/../../x",
                        "docs//ok.md", "docs\\ok.md", "./docs/ok.md", ".."):
                with self.assertRaises(cpaths.PathContainmentError) as cm:
                    cpaths.contained_repo_path(root, bad)
                self.assertEqual(cm.exception.code, "non_canonical_path", bad)
                # NEVER a private absolute path in the error (R034)
                self.assertNotIn(root.replace("\\", "/"),
                                 cm.exception.detail.replace("\\", "/"))
            # the happy path still works
            self.assertTrue(cpaths.contained_repo_path(root, "docs/ok.md").is_file())

    def test_junction_or_symlink_escape_refused(self) -> None:
        with tempfile.TemporaryDirectory() as outer:
            root = os.path.join(outer, "repo")
            os.makedirs(os.path.join(root, "docs"))
            secret_dir = os.path.join(outer, "secret")
            os.makedirs(secret_dir)
            _write(outer, "secret/leak.txt", "OUTSIDE\n")
            link = os.path.join(root, "docs", "link")
            made = False
            try:  # symlink first (POSIX / privileged Windows)
                os.symlink(secret_dir, link, target_is_directory=True)
                made = True
            except OSError:
                if os.name == "nt":  # junction needs no privilege on Windows
                    p = subprocess.run(["cmd", "/c", "mklink", "/J", link,
                                        secret_dir], capture_output=True)
                    made = p.returncode == 0
            if not made:
                self.skipTest("cannot create symlink/junction in this environment")
            with self.assertRaises(cpaths.PathContainmentError) as cm:
                cpaths.contained_repo_path(root, "docs/link/leak.txt")
            self.assertEqual(cm.exception.code, "path_escapes_repository")
            self.assertNotIn("secret", cm.exception.detail)
            self.assertNotIn(outer.replace("\\", "/"),
                             cm.exception.detail.replace("\\", "/"))

    def test_deep_view_and_include_and_memory_paths_covered(self) -> None:
        # spot-check three adopting surfaces reject through the ONE rule
        from tools import repo_views as rv
        with self.assertRaises(rv.ViewsError) as cm:
            rv.deep_view(None, None, _ROOT, "docs/../secret.md", 1, 2)
        self.assertEqual(cm.exception.code, "non_canonical_path")
        from tools.memory_grounding import ground_file_link
        g = ground_file_link("../outside.py", {"allowed_paths": [],
                                               "cited_directives": []}, [], [], [])
        self.assertEqual(g["reason"], "non_canonical_path")
        from tools.subsystem_entities import _RX_TASK  # canonical import check
        self.assertTrue(_RX_TASK.match("M0-T001"))


class D019ContainmentRedactionInsufficiency(unittest.TestCase):
    """M0-T076 / D-019-R022..R025: --ci-summary joins the shared containment
    rule; a refused EXPLICIT --include/--ci-summary is insufficient (nonzero) and
    NEVER leaks its marker/absolute path into context.md, metadata, evidence,
    stdout or stderr; the omission reason is redacted."""

    def _run(self, extra):
        out = tempfile.mkdtemp()
        cache = tempfile.mkdtemp()
        p = subprocess.run(
            [sys.executable, os.path.join(_HERE, "context_pack.py"),
             "--task", "M0-T066", "--role", "worker", "--provider", "claude",
             "--max-bytes", "500000", "--out", out, "--repo", _ROOT,
             "--index-cache-base", cache, "--no-index-telemetry", *extra],
            capture_output=True, text=True)
        with open(os.path.join(out, "context.meta.json"), encoding="utf-8") as fh:
            meta = json.load(fh)
        # The disclosure-relevant surfaces: streams + the omission/echo channels
        # where a SUPPLIED path would be repeated (never unrelated source excerpts,
        # which legitimately contain strings like "/etc/passwd" as test data).
        omission_text = json.dumps(meta["omitted_categories"]) + json.dumps(
            meta["generated_from"])
        return p.returncode, meta, omission_text, p.stdout + p.stderr, out

    def test_absolute_ci_summary_refused_no_leak(self) -> None:
        # Assemble the marker at RUNTIME so the literal string exists in no source
        # file (else it would appear in a legitimate source excerpt of the packet
        # and confound the leak scan — not a containment leak).
        marker = "".join(["CIMK", "R", "%08x" % (os.getpid() & 0xFFFFFFFF), "END"])
        secret = os.path.join(tempfile.mkdtemp(), "private_ci.txt")
        with open(secret, "w", encoding="utf-8") as fh:
            fh.write(marker + "\n")
        rc, meta, omission, streams, out = self._run(["--ci-summary", secret])
        self.assertNotEqual(rc, 0)                       # R025 insufficiency
        self.assertFalse(meta["sufficiency"]["sufficient"])
        # the unique marker + absolute dir must appear NOWHERE (content + every file)
        whole = streams
        for base, _d, files in os.walk(out):
            for fn in files:
                with open(os.path.join(base, fn), encoding="utf-8",
                          errors="replace") as fh:
                    whole += fh.read()
        self.assertNotIn(marker, whole)                  # content never read
        self.assertNotIn(os.path.dirname(secret).replace("\\", "/"),
                         whole.replace("\\", "/"))        # R024 no abs path anywhere
        self.assertEqual(meta["generated_from"]["ci_summary"]["status"], "refused")
        self.assertEqual(meta["generated_from"]["ci_summary"]["ref"],
                         "[redacted:non_canonical_path]")

    def test_absolute_include_refused_redacted_and_insufficient(self) -> None:
        rc, meta, omission, streams, _ = self._run(
            ["--include", r"C:\Windows\System32\drivers\etc\hosts"])
        self.assertNotEqual(rc, 0)
        self.assertFalse(meta["sufficiency"]["sufficient"])
        # the SUPPLIED absolute path is redacted in every echo channel
        self.assertNotIn("System32", omission)
        self.assertNotIn("System32", streams)
        self.assertIn("[redacted", omission)
        self.assertEqual(meta["generated_from"]["include"], [])
        self.assertEqual(meta["generated_from"]["include_refused"][0]["ref"],
                         "[redacted:non_canonical_path]")

    def test_traversal_include_refused_and_insufficient(self) -> None:
        rc, meta, omission, streams, _ = self._run(["--include", "../../../etc/passwd"])
        self.assertNotEqual(rc, 0)
        self.assertFalse(meta["sufficiency"]["sufficient"])
        # the supplied traversal string is redacted where it would be echoed
        self.assertNotIn("etc/passwd", omission.replace("\\", "/"))
        self.assertNotIn("etc/passwd", streams.replace("\\", "/"))


class D019RacedEscapingLink(unittest.TestCase):
    """M0-T076 / D-019 proof 3: containment is applied AT READ TIME, so an
    escaping junction/symlink swapped in BEFORE the read still refuses — the
    canonical-string check alone never authorizes a later read."""

    def test_link_present_at_read_time_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as outer:
            root = os.path.join(outer, "repo")
            os.makedirs(os.path.join(root, "docs"))
            secret_dir = os.path.join(outer, "secret")
            os.makedirs(secret_dir)
            _write(outer, "secret/leak.txt", "OUTSIDE\n")
            rel = "docs/link/leak.txt"
            # The canonical STRING check passes (no absolute/traversal); the
            # escape only exists once the junction is materialized. Containment
            # must still refuse because it re-resolves the real path at read time.
            self.assertTrue(cpaths.is_canonical_repo_path(rel))
            link = os.path.join(root, "docs", "link")
            made = False
            try:
                os.symlink(secret_dir, link, target_is_directory=True)
                made = True
            except OSError:
                if os.name == "nt":
                    pr = subprocess.run(["cmd", "/c", "mklink", "/J", link, secret_dir],
                                        capture_output=True)
                    made = pr.returncode == 0
            if not made:
                self.skipTest("cannot create symlink/junction here")
            with self.assertRaises(cpaths.PathContainmentError) as cm:
                cpaths.contained_read_bytes(root, rel)
            self.assertEqual(cm.exception.code, "path_escapes_repository")
            self.assertNotIn("secret", cm.exception.detail)
            self.assertNotIn(outer.replace("\\", "/"),
                             cm.exception.detail.replace("\\", "/"))


class D019FrozenDiffBase(unittest.TestCase):
    """M0-T076 / D-019-R026..R028: the orchestrator resolves the task's frozen G0
    base instead of silently diffing HEAD, so a COMMITTED reviewer packet still
    contains the committed hunks; a missing frozen base + no explicit override is
    REFUSED rather than defaulting to HEAD; full provenance is recorded."""

    def _git(self, repo, *args):
        env = dict(os.environ)
        env.update({"GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@x",
                    "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@x",
                    "GIT_CONFIG_NOSYSTEM": "1"})
        subprocess.run(["git", *args], cwd=repo, env=env, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _repo_with_committed_change(self, tmp):
        from tools.context_pack_io import run_git
        self._git(tmp, "init", "-q")
        self._git(tmp, "commit", "--allow-empty", "-q", "-m", "root", "--no-verify")
        _write(tmp, "tools/widget.py", "def widget():\n    return 1\n")
        self._git(tmp, "add", "-A")
        self._git(tmp, "commit", "-q", "-m", "base", "--no-verify")
        base_sha = run_git(tmp, ["rev-parse", "HEAD"])[1].strip()
        # record the frozen G0 gate for the task at this base
        _write(tmp, "project-control/gates/M0-T500-G0.json",
               json.dumps({"task_id": "M0-T500", "gate_id": "G0",
                           "reviewed_sha": base_sha}))
        # now COMMIT a change on top (the reviewer must still see it)
        _write(tmp, "tools/widget.py",
               "def widget():\n    return 2  # COMMITTED_CHANGE_MARKER\n")
        self._git(tmp, "add", "-A")
        self._git(tmp, "commit", "-q", "-m", "work", "--no-verify")
        head_sha = run_git(tmp, ["rev-parse", "HEAD"])[1].strip()
        return base_sha, head_sha

    def test_committed_change_visible_against_frozen_base(self) -> None:
        from tools import context_orchestrate as co
        from tools.context_pack_io import run_git
        with tempfile.TemporaryDirectory() as tmp:
            base_sha, head_sha = self._repo_with_committed_change(tmp)
            base, prov = co.resolve_diff_base(tmp, "M0-T500", "reviewer", None)
            self.assertEqual(prov["resolution"], "frozen_g0_gate_sha")
            self.assertEqual(base, base_sha)
            self.assertNotEqual(base, head_sha)          # NOT silently HEAD
            self.assertEqual(prov["head_sha"], head_sha)
            self.assertEqual(prov["diff_command"], f"git diff {base_sha}")
            # the committed hunk is present in the diff against the frozen base
            out = run_git(tmp, ["diff", base])[1]
            self.assertIn("COMMITTED_CHANGE_MARKER", out)
            # ... and empty against HEAD (the exact former reviewer failure mode)
            self.assertEqual(run_git(tmp, ["diff", head_sha])[1].strip(), "")

    def test_no_frozen_base_refuses_instead_of_head(self) -> None:
        from tools import context_orchestrate as co
        with tempfile.TemporaryDirectory() as tmp:
            self._git(tmp, "init", "-q")
            _write(tmp, "a.py", "x=1\n")
            self._git(tmp, "add", "-A")
            self._git(tmp, "commit", "-q", "-m", "c", "--no-verify")
            base, prov = co.resolve_diff_base(tmp, "M0-T999", "reviewer", None)
            self.assertIsNone(base)                       # refuses; never HEAD
            self.assertEqual(prov["resolution"], "unresolved_require_explicit")
            self.assertIsNotNone(prov["error"])

    def test_explicit_trusted_base_resolves(self) -> None:
        from tools import context_orchestrate as co
        from tools.context_pack_io import run_git
        with tempfile.TemporaryDirectory() as tmp:
            base_sha, head_sha = self._repo_with_committed_change(tmp)
            base, prov = co.resolve_diff_base(tmp, "M0-T500", "worker", base_sha)
            self.assertEqual(base, base_sha)
            self.assertEqual(prov["resolution"], "explicit_trusted_diff_base")
            # an unresolvable explicit base is refused, not silently accepted
            b2, p2 = co.resolve_diff_base(tmp, "M0-T500", "worker", "deadbeef" * 5)
            self.assertIsNone(b2)
            self.assertEqual(p2["resolution"], "explicit_unresolvable")


class Proof7EntryPoint(unittest.TestCase):
    """Proof 7: the canonical entry point ACTUALLY calls the integrated
    compiler + grounded router (never a second packet)."""

    def test_entry_point_invokes_integrated_compiler(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             tempfile.TemporaryDirectory() as cache:
            p = subprocess.run(
                [sys.executable, os.path.join(_HERE, "context_orchestrate.py"),
                 "prepare", "--task", "M0-T066", "--role", "worker",
                 "--provider", "claude", "--max-bytes", "500000",
                 "--out", out, "--repo", _ROOT,
                 # M0-T066 is compiled here from an UNRELATED HEAD (not its own
                 # branch), so the caller supplies an explicit trusted diff base
                 # rather than the task's frozen G0 (M0-T076, D-019-R026). This
                 # test asserts the entry point invokes the integrated compiler,
                 # not diff-base semantics (covered by D019FrozenDiffBase).
                 "--diff-base", "HEAD",
                 "--index-cache-base", cache, "--no-index-telemetry"],
                capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            # the INTEGRATED packet exists (context.md from context_pack.emit)
            with open(os.path.join(out, "context.meta.json"),
                      encoding="utf-8") as fh:
                meta = json.load(fh)
            self.assertIn("integration", meta)  # the integrated compiler ran
            with open(os.path.join(out, "dispatch_manifest.json"),
                      encoding="utf-8") as fh:
                man = json.load(fh)
            self.assertEqual(man["schema"], "context_dispatch_manifest/v1")
            self.assertIn("OWNER-GATED", man["supervisor_boundary"])

    def test_routing_signals_derived_and_recorded(self) -> None:
        # a fixture model config exercises route+record end-to-end; missing
        # evidence must raise ambiguity, never silently LOW.
        from tools import context_orchestrate as co
        meta = {"integration": {"implementation_paths": [], "requirements":
                                {"in_regime": True, "error": "boom"},
                                "subsystems_touched": 0},
                "provenance": {}, "sufficiency": {"sufficient": False},
                "included_files": [], "actuals": {}}
        signals, notes = co.derive_signals(meta, 3)
        self.assertTrue(signals.ambiguity_or_missing_evidence)
        self.assertTrue(any("requirement evidence" in n for n in notes))


class RetentionReal(unittest.TestCase):
    def test_generation_prune_keeps_current_plus_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as checkout, \
             tempfile.TemporaryDirectory() as base:
            cache = ric.IndexCache(checkout, base=base)
            for i in range(7):
                cache.write_generation(f"fp{i:02d}", {"n": i})
            pruned = cache.prune(keep=2)
            gens = {g.name for g in cache.generations_dir.glob("*") if g.is_dir()}
            self.assertIn("fp06", gens)          # current survives
            self.assertGreaterEqual(len(gens), 2)  # rollback preserved
            self.assertLessEqual(len(gens), 3)
            self.assertTrue(pruned)

    def test_jsonl_rotation_bounds_the_log(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, "t.jsonl")
            for i in range(200):
                ric.append_jsonl_rotated(log, {"i": i, "pad": "x" * 200},
                                         max_bytes=5_000, keep=1)
            self.assertLess(os.path.getsize(log), 5_500)
            self.assertTrue(os.path.exists(log + ".1"))  # rotation kept


import unittest.mock  # noqa: E402  (used by Proof3)

if __name__ == "__main__":
    unittest.main()
