#!/usr/bin/env python3
"""M0-T064 Unit A2 tests: byte-identical assembly driver (D-013-R032/R037/R079).

These pin the generator-coupled replica to the REAL `code_graph.build_graph`:
if the generator changes and this module is not updated in lock-step, the parity
assertions fail (the intended tripwire), and in production the version guard
forces the real builder rather than emitting divergent bytes.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools import repo_index_assembly as asm  # noqa: E402
from tools.code_graph import generate as cg  # noqa: E402


def _git(repo: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class AssemblyRepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self._tmp.name) / "repo"
        (self.repo / "services" / "api").mkdir(parents=True)
        _git(self.repo, "init", "-q")
        _git(self.repo, "config", "user.email", "t@t.t")
        _git(self.repo, "config", "user.name", "t")
        self.addCleanup(self._tmp.cleanup)

    def write(self, rel: str, text: str) -> None:
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")

    def real_bytes(self) -> bytes:
        graph, _, _ = cg.build_graph(str(self.repo))
        return cg.serialize(graph)


class ColdParity(AssemblyRepoCase):
    def setUp(self) -> None:
        super().setUp()
        self.write("services/api/a.py", "from services.api.g import g\n\ndef f():\n    return g()\n")
        self.write("services/api/g.py", "import os\n\ndef g():\n    return os.getpid()\n")

    def test_cold_export_and_meta_match_real(self) -> None:
        graph, meta, _ = cg.build_graph(str(self.repo))
        res = asm.drive(self.repo)
        self.assertEqual(res.export_bytes, cg.serialize(graph))
        self.assertEqual(res.meta, meta)
        self.assertEqual(res.files_reused, 0)
        self.assertGreater(res.files_parsed, 0)


class WarmParity(AssemblyRepoCase):
    def setUp(self) -> None:
        super().setUp()
        self.write("services/api/a.py", "def f():\n    return 1\n")
        self.write("services/api/g.py", "def g():\n    return 2\n")

    def test_warm_no_change_reuses_all_zero_parsed(self) -> None:
        cold = asm.drive(self.repo)
        warm = asm.drive(self.repo, prior_bundles=cold.bundles,
                         prior_schema_nodes=cold.schema_nodes,
                         changed=frozenset(), input_files=cold.input_files)
        self.assertEqual(warm.files_parsed, 0)
        self.assertEqual(warm.files_reused, len(cold.input_files))
        self.assertEqual(warm.export_bytes, self.real_bytes())

    def test_warm_one_change_reparses_one_still_identical(self) -> None:
        cold = asm.drive(self.repo)
        self.write("services/api/g.py", "def g():\n    return 999\n")
        warm = asm.drive(self.repo, prior_bundles=cold.bundles,
                         prior_schema_nodes=cold.schema_nodes,
                         changed=frozenset({"services/api/g.py"}),
                         input_files=cold.input_files)
        self.assertEqual(warm.files_parsed, 1)
        self.assertEqual(warm.export_bytes, self.real_bytes())


class ContractPartitionGuard(AssemblyRepoCase):
    """The per-file contract-edge computation must sum to the real global pass."""

    def setUp(self) -> None:
        super().setUp()
        self.write("packages/contracts/schemas/thing.schema.json",
                   '{"$id": "https://x/thing", "type": "object"}')
        self.write("services/api/uses.py",
                   "# references thing.schema.json and property\nTHING = 'thing'\n")

    def test_partition_matches_real_contract_edges(self) -> None:
        res = asm.drive(self.repo)
        files_text = {rel: asm._read_text(str(self.repo), rel)
                      for rel in res.input_files}
        real = cg._EdgeSet()
        cg._contract_edges(files_text, res.schema_nodes, real)
        part = cg._EdgeSet()
        for rel in res.input_files:
            for e in res.bundles[rel]["contract_edges"]:
                part.add_edge(e["type"], e["from"], e["to"], e["confidence"],
                              e["line"], e["specifier"], e["resolution"])
        self.assertEqual(real.sorted_edges(), part.sorted_edges())


class GeneratorGuard(AssemblyRepoCase):
    def test_recognized_on_current_generator(self) -> None:
        self.assertTrue(asm.generator_recognized())
        self.assertEqual(asm.generator_identity(),
                         f"{cg.GENERATOR_VERSION}/{cg.SCHEMA_VERSION}")

    def test_drive_refuses_unknown_generator(self) -> None:
        self.write("services/api/a.py", "X = 1\n")
        original = cg.GENERATOR_VERSION
        try:
            cg.GENERATOR_VERSION = original + "-nope"
            with self.assertRaises(asm.UnknownGeneratorError):
                asm.drive(self.repo)
        finally:
            cg.GENERATOR_VERSION = original


class RealRepoAssemblyParity(unittest.TestCase):
    def test_cold_drive_matches_real_on_this_repo(self) -> None:
        root = pathlib.Path(__file__).resolve().parent.parent
        graph, meta, _ = cg.build_graph(str(root))
        res = asm.drive(root)
        self.assertEqual(res.export_bytes, cg.serialize(graph))
        self.assertEqual(res.meta, meta)


if __name__ == "__main__":
    unittest.main()
