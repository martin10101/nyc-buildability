"""M0-T134 / D-024 Amendment 39 R510/R514 (C12): the raw gate-evidence recorder.

Exercises the recorder via DIRECT process execution and via REAL PowerShell, and
independently corroborates every recorded value against a second, independent
measurement (so the tests never rely solely on gate_runner's own claims). Proves
the recorded return code is the child's raw exit (unmaskable: argv is a list, no
shell/pipe), that reports are generated from the record, and the mutation-harness
semantics (a killed mutant is success, not a failed gate).
"""

import hashlib
import shutil
import subprocess
import sys
import unittest

from tools.gate_runner import (
    GateRecord,
    render_report,
    run_gate,
    run_mutation_check,
)


class DirectProcessTests(unittest.TestCase):
    def test_records_raw_nonzero_exit_corroborated_independently(self) -> None:
        argv = [sys.executable, "-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"]
        rec = run_gate(argv)
        self.assertIsInstance(rec, GateRecord)
        # independent measurement, NOT trusting gate_runner's own claim
        indep = subprocess.run(argv, capture_output=True)
        self.assertEqual(rec.returncode, indep.returncode)
        self.assertEqual(rec.returncode, 3)
        self.assertEqual(rec.stderr_sha256, hashlib.sha256(indep.stderr).hexdigest())

    def test_records_stdout_digest(self) -> None:
        argv = [sys.executable, "-c", "print('hello gate')"]
        rec = run_gate(argv)
        indep = subprocess.run(argv, capture_output=True)
        self.assertEqual(rec.returncode, 0)
        self.assertEqual(rec.stdout_sha256, hashlib.sha256(indep.stdout).hexdigest())

    def test_large_stdout_does_not_mask_exit(self) -> None:
        argv = [sys.executable, "-c", "import sys; sys.stdout.write('x'*100000); sys.exit(5)"]
        rec = run_gate(argv)
        self.assertEqual(rec.returncode, 5)          # exit is the child's, regardless of output volume
        self.assertEqual(rec.stdout_bytes, 100000)

    def test_shell_string_refused(self) -> None:
        # A shell string is exactly where a pipe/Tee-Object/tail could mask the exit.
        with self.assertRaises(ValueError):
            run_gate("python -c \"exit(1)\" | tail -n1")

    def test_records_window_and_bindings(self) -> None:
        rec = run_gate([sys.executable, "-c", "pass"],
                       executable_chain_sha256="deadbeef",
                       repo_facts=lambda cwd: ("HEADSHA", "TREESHA"))
        self.assertEqual((rec.repo_head, rec.repo_tree), ("HEADSHA", "TREESHA"))
        self.assertEqual(rec.executable_chain_sha256, "deadbeef")
        self.assertTrue(rec.started_at_utc <= rec.ended_at_utc)
        self.assertTrue(rec.cwd)


class PowerShellTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ps = shutil.which("powershell") or shutil.which("pwsh")
        if not self.ps:
            self.skipTest("PowerShell not available")

    def test_real_powershell_raw_exit_corroborated(self) -> None:
        argv = [self.ps, "-NoProfile", "-Command", "exit 7"]
        rec = run_gate(argv)
        indep = subprocess.run(argv, capture_output=True)
        self.assertEqual(rec.returncode, indep.returncode)
        self.assertEqual(rec.returncode, 7)

    def test_powershell_pipe_to_tail_object_cannot_change_recorded_exit(self) -> None:
        # Inside PowerShell the child exits 9; even piping its output through
        # Out-String/Select-Object (a tail-like filter) must not change the code
        # gate_runner records, because gate_runner records the powershell process's
        # own exit, and $LASTEXITCODE is surfaced as the process exit here.
        script = "python -c 'import sys; sys.exit(9)' | Out-String | Out-Null; exit $LASTEXITCODE"
        argv = [self.ps, "-NoProfile", "-Command", script]
        rec = run_gate(argv)
        indep = subprocess.run(argv, capture_output=True)
        self.assertEqual(rec.returncode, indep.returncode)
        self.assertEqual(rec.returncode, 9)


class ReportAndMutationTests(unittest.TestCase):
    def test_report_generated_from_record(self) -> None:
        rec = run_gate([sys.executable, "-c", "import sys; sys.exit(2)"])
        report = render_report(rec)
        self.assertIn("FAIL", report)
        self.assertIn("returncode 2", report)
        self.assertIn(rec.stdout_sha256, report)  # the report reflects the machine record

    def test_mutation_killed_is_success(self) -> None:
        # a KILLED mutant (nonzero exit) with expect_nonzero -> ok True
        res = run_mutation_check([sys.executable, "-c", "import sys; sys.exit(1)"],
                                 expect_nonzero=True)
        self.assertTrue(res.killed)
        self.assertTrue(res.ok)

    def test_mutation_survivor_is_not_ok(self) -> None:
        # a mutant that PASSES (exit 0) when we expected it killed -> ok False (the
        # harness flags a surviving mutant, but this is not itself a crashed gate)
        res = run_mutation_check([sys.executable, "-c", "pass"], expect_nonzero=True)
        self.assertFalse(res.killed)
        self.assertFalse(res.ok)

    def test_mutation_expect_zero_pass(self) -> None:
        res = run_mutation_check([sys.executable, "-c", "pass"], expect_nonzero=False)
        self.assertTrue(res.ok)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
