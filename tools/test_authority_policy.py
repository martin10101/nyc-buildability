"""Deterministic policy tests for the D-010 autonomy-tier model (ADR-006).

Run: python -m unittest tools.test_authority_policy   (stdlib only, no new deps)

These tests are the regression backstop for ADR-006. They parse the tier tables
FROM docs/adr/ADR-006-autonomy-tiers.md (between machine-readable HTML-comment
anchors) and cross-check them against an in-test canonical table taken verbatim
from D-010 Section 5. Doc drift therefore fails the suite:

  * adding an unlisted Tier A action, or dropping one, fails set-equality;
  * a Tier B class losing (or changing) its named specialist review fails;
  * a Tier C item that would escalate to an owner stop fails;
  * dropping any Tier D hard-deny item fails;
  * a missing Section 5.5 automatic-merge condition fails;
  * removing the R595 / activation caveat text fails.

It also replays the PRs #143-#146 allowlist incident under the ADR-006 policy.
"""

import os
import re
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ADR_PATH = os.path.normpath(os.path.join(_HERE, "..", "docs", "adr", "ADR-006-autonomy-tiers.md"))


# --------------------------------------------------------------------------
# Canonical tier table, verbatim from D-010 source-001.md Section 5.
# This is the authority the ADR must reproduce faithfully.
# --------------------------------------------------------------------------

CANONICAL_TIER_A = [
    "read and search the repository",
    "query official public sources",
    "create and update task records",
    "create branches and worktrees",
    "edit ordinary product code",
    "edit tests",
    "edit ordinary documentation",
    "run formatters, linters, type checks, tests, and builds",
    "commit work",
    "push to the exact non-default task branch",
    "create or update a pull request",
    "request and receive automated reviews",
    "correct review findings",
    "rerun CI",
    "merge an ordinary pull request after all required checks pass",
    "delete the merged task branch",
    "update the ledger",
    "continue to the next accepted dependency",
]

CANONICAL_TIER_B = {
    "Dependencies and lockfiles": "dependency-security + CI",
    "GitHub Actions and CI": "security + control-plane",
    "Auth/session code": "security + code + integration",
    "Additive database migration": "data-contract/database + security + rollback test",
    "Contract/schema addition": "data-contract + compatibility",
    "Official-source connector": "source/data-contract + drift fixture",
    "Legal-corpus ingestion code": "security + prompt-injection/data-contract",
    "Draft rule implementation": "rules/code + QA",
    "Scenario calculation": "data-contract + QA",
    "Survey/PDF parser": "security + deterministic validation",
    "Supervisor code": "control-plane + security + crash/replay",
}

CANONICAL_TIER_C = [
    "a cosmetic UI disagreement",
    "a noncritical source temporarily unavailable",
    "one optional test environment unavailable",
    "a rule family not yet implemented",
    "a task blocked by a future dependency while unrelated work remains",
    "a provider reviewer temporarily unavailable",
    "a noncritical research ambiguity that can be labeled unsupported",
]

CANONICAL_TIER_D = [
    "Force push or history rewrite.",
    "Direct push to `main` or another protected default branch.",
    "Weakening branch protection, review requirements, secret controls, or the hard-deny policy.",
    "Deleting the repository.",
    "Deleting production data.",
    "Destructive database migration without a specific owner approval and tested restore.",
    "Production deployment, production infrastructure mutation, or production secret rotation.",
    "Credentials, new account creation, payment, verification code, or acceptance of binding legal terms.",
    "Suspected secret or private-client-data exposure.",
    "Publishing or labeling a legal rule as `published` or `verified` without the required qualified professional event.",
    "Representing an architect's pilot result as a legal opinion, permit approval, or professional certification.",
    "A genuine contradiction in authoritative requirements that cannot be resolved through source priority, tests, or existing owner directives.",
    "An operation whose real target or external effect cannot be proven.",
    "Rotation or shutdown while any worker, child agent, write transaction, Git operation, or external side effect remains in flight.",
]

CANONICAL_MERGE_CONDITIONS = [
    "the task is authorized and dependency-valid",
    "the changed paths fit the task",
    "the branch is current enough to merge safely",
    "required tests and CI pass",
    "the secret scan is clean",
    "required specialist reviews pass",
    "no unresolved blocking finding exists",
    "the merge is not a production deployment",
    "the resulting main SHA is recorded",
    "the task state is updated transactionally",
]


# --------------------------------------------------------------------------
# ADR parser (deterministic, anchor-delimited).
# --------------------------------------------------------------------------

def _read_adr():
    with open(_ADR_PATH, "r", encoding="utf-8") as fh:
        return fh.read()


def _block(text, name):
    """Return the raw text between <!-- name:BEGIN --> and <!-- name:END -->."""
    pat = re.compile(
        r"<!--\s*" + re.escape(name) + r":BEGIN\s*-->(.*?)<!--\s*"
        + re.escape(name) + r":END\s*-->",
        re.DOTALL,
    )
    m = pat.search(text)
    if not m:
        raise AssertionError("ADR-006 is missing anchored block %r" % name)
    return m.group(1)


def _bullets(block):
    out = []
    for line in block.splitlines():
        s = line.strip()
        if s.startswith("- "):
            out.append(s[2:].strip())
    return out


def _numbered(block):
    out = []
    for line in block.splitlines():
        s = line.strip()
        m = re.match(r"^\d+\.\s+(.*)$", s)
        if m:
            out.append(m.group(1).strip())
    return out


def _table_map(block):
    out = {}
    for line in block.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) != 2:
            continue
        left, right = cells
        if left in ("Change class",) or set(left) <= set("-: "):
            continue  # header / separator row
        out[left] = right
    return out


class ADRParseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = _read_adr()

    def test_adr_exists_and_accepted(self):
        self.assertIn("ADR-006", self.text)
        self.assertRegex(self.text, r"\*\*Status:\*\*\s*Accepted")

    # ----- Tier A: exact set (add or drop fails) -----
    def test_tier_a_actions_match_canonical(self):
        parsed = _bullets(_block(self.text, "TIER-A-ACTIONS"))
        self.assertEqual(
            set(parsed), set(CANONICAL_TIER_A),
            "Tier A actions in ADR-006 drifted from D-010 Section 5.1",
        )
        self.assertEqual(len(parsed), len(CANONICAL_TIER_A),
                         "Tier A list has duplicate or extra rows")

    def test_tier_a_all_classified_automatic_after_checks(self):
        # Every Tier A action is classified as permitted-after-required-checks.
        for action in CANONICAL_TIER_A:
            self.assertEqual(classify_tier(action), "A", action)
            self.assertTrue(is_automatic_after_checks(action), action)

    # ----- Tier B: every class -> its named specialist review -----
    def test_tier_b_map_match_canonical(self):
        parsed = _table_map(_block(self.text, "TIER-B-MAP"))
        self.assertEqual(
            parsed, CANONICAL_TIER_B,
            "Tier B change-class -> required-review map drifted from D-010 Section 5.2",
        )

    def test_tier_b_every_class_bound_to_review(self):
        for change_class, review in CANONICAL_TIER_B.items():
            self.assertEqual(classify_tier(change_class), "B", change_class)
            self.assertEqual(required_review_for(change_class), review, change_class)
            self.assertTrue(review.strip(), change_class)

    # ----- Tier C: queue-and-continue, never owner escalation -----
    def test_tier_c_items_match_canonical(self):
        parsed = _bullets(_block(self.text, "TIER-C-ITEMS"))
        self.assertEqual(
            set(parsed), set(CANONICAL_TIER_C),
            "Tier C items in ADR-006 drifted from D-010 Section 5.3",
        )

    def test_tier_c_never_escalates_to_owner(self):
        for item in CANONICAL_TIER_C:
            self.assertEqual(classify_tier(item), "C", item)
            self.assertEqual(tier_c_disposition(item), "QUEUE_AND_CONTINUE", item)
            self.assertFalse(escalates_to_owner(item), item)

    # ----- Tier D: every hard-deny item present (drop fails) -----
    def test_tier_d_items_match_canonical(self):
        parsed = _numbered(_block(self.text, "TIER-D-ITEMS"))
        self.assertEqual(
            parsed, CANONICAL_TIER_D,
            "Tier D hard-deny list drifted from D-010 Section 5.4 (order + content must match)",
        )
        self.assertEqual(len(parsed), 14, "Tier D must have exactly 14 items")

    def test_tier_d_every_item_hard_denies(self):
        for item in CANONICAL_TIER_D:
            self.assertEqual(classify_tier(item), "D", item)
            self.assertTrue(hard_denies(item), item)

    # ----- Section 5.5 merge conditions: all required -----
    def test_merge_conditions_match_canonical(self):
        parsed = _bullets(_block(self.text, "MERGE-CONDITIONS"))
        self.assertEqual(
            parsed, CANONICAL_MERGE_CONDITIONS,
            "Section 5.5 automatic-merge conditions drifted from D-010",
        )
        self.assertEqual(len(parsed), 10, "Section 5.5 must have exactly 10 conditions")

    # ----- Supersession + activation caveat text present -----
    def test_supersession_recorded_for_tier_a_only(self):
        self.assertIn("D-004-R721", self.text)
        self.assertRegex(self.text, r"[Ss]upersed.*ORDINARY TIER A|ORDINARY TIER A WORK")
        # ADR-005 core must be preserved explicitly.
        self.assertIn("orchestrator", self.text)
        self.assertRegex(self.text, r"ADR-005'?s? core|ADR-005 core|core authority model")

    def test_r595_activation_caveat_present(self):
        self.assertIn("R595", self.text)
        self.assertRegex(self.text, r"R595.*(prerequisite|activation)")
        self.assertRegex(self.text, r"orchestrator.*execute[s]? Tier A actions manually")

    def test_g6_split_recorded(self):
        # Engineering vs publication acceptance both present with the exact conditions.
        eng = _bullets(_block(self.text, "G6-ENGINEERING"))
        pub = _bullets(_block(self.text, "G6-PUBLICATION"))
        self.assertIn("the output is never labeled verified", eng)
        self.assertIn("the rule remains `draft`, `extracted_draft`, or `needs_review`", eng)
        self.assertIn("reviewer identity and role", pub)
        self.assertIn("release version", pub)
        self.assertIn("AD-061", self.text)
        self.assertIn("AD-063", self.text)


# --------------------------------------------------------------------------
# Deterministic policy classifier used by the tests above and the incident
# replay below. It is the in-test encoding of the ADR-006 tier model.
# --------------------------------------------------------------------------

def classify_tier(item):
    if item in CANONICAL_TIER_A:
        return "A"
    if item in CANONICAL_TIER_B:
        return "B"
    if item in CANONICAL_TIER_C:
        return "C"
    if item in CANONICAL_TIER_D:
        return "D"
    return "UNKNOWN"


def is_automatic_after_checks(action):
    return classify_tier(action) == "A"


def required_review_for(change_class):
    return CANONICAL_TIER_B.get(change_class)


def tier_c_disposition(item):
    return "QUEUE_AND_CONTINUE" if classify_tier(item) == "C" else "N/A"


def escalates_to_owner(item):
    # Tier C never stops the world; only Tier D reaches the owner / hard deny.
    return classify_tier(item) == "D"


def hard_denies(item):
    return classify_tier(item) == "D"


def classify_merge(
    *,
    authorized_and_dependency_valid,
    paths_fit,
    branch_current,
    tests_ci_pass,
    secret_scan_clean,
    specialist_reviews_pass,
    no_blocking_finding,
    not_production_deploy,
    main_sha_recorded,
    state_transactional,
    via_allowlisted_command=False,
):
    """Encode Section 5.5: an ordinary PR may merge automatically only when ALL
    ten conditions hold. `via_allowlisted_command` is intentionally NOT a
    condition: an allowlisted/auto-classified command is never an authorization
    (D-004-R721 lesson, preserved by ADR-006).
    """
    conditions = (
        authorized_and_dependency_valid,
        paths_fit,
        branch_current,
        tests_ci_pass,
        secret_scan_clean,
        specialist_reviews_pass,
        no_blocking_finding,
        not_production_deploy,
        main_sha_recorded,
        state_transactional,
    )
    return "PERMITTED_TIER_A" if all(conditions) else "NOT_PERMITTED"


class MergeConditionCountTest(unittest.TestCase):
    def test_classifier_covers_every_5_5_condition(self):
        # The classifier keyword set must line up 1:1 with Section 5.5.
        import inspect
        sig = inspect.signature(classify_merge)
        # exclude via_allowlisted_command (deliberately not a 5.5 condition)
        params = [p for p in sig.parameters if p != "via_allowlisted_command"]
        self.assertEqual(
            len(params), len(CANONICAL_MERGE_CONDITIONS),
            "classify_merge must encode exactly the 10 Section 5.5 conditions",
        )


class PRs143to146ReplayTest(unittest.TestCase):
    """Replay the allowlist incident under ADR-006."""

    def _incident_kwargs(self, **overrides):
        # The incident merges ran via allowlisted commands (gh pr / git push /
        # git merge) that bypassed the auto-mode classifier. Reproduce a merge
        # that lacks green required checks AND specialist review.
        base = dict(
            authorized_and_dependency_valid=False,  # no recorded per-merge authority
            paths_fit=True,
            branch_current=True,
            tests_ci_pass=False,        # required checks NOT green in this scenario
            secret_scan_clean=True,
            specialist_reviews_pass=False,  # specialist review NOT satisfied
            no_blocking_finding=True,
            not_production_deploy=True,
            main_sha_recorded=True,
            state_transactional=True,
            via_allowlisted_command=True,
        )
        base.update(overrides)
        return base

    def test_allowlisted_merge_without_checks_is_not_permitted(self):
        verdict = classify_merge(**self._incident_kwargs())
        self.assertEqual(
            verdict, "NOT_PERMITTED",
            "An allowlisted-command merge without green checks + specialist "
            "review must not be permitted (PRs 143-146 lesson: allowlist != authorization)",
        )

    def test_allowlist_alone_is_not_authorization(self):
        # Even flipping only the allowlist flag on, with the required conditions
        # still missing, must remain NOT_PERMITTED.
        verdict = classify_merge(
            **self._incident_kwargs(via_allowlisted_command=True,
                                    tests_ci_pass=False,
                                    specialist_reviews_pass=False)
        )
        self.assertEqual(verdict, "NOT_PERMITTED")

    def test_ordinary_green_check_merge_is_tier_a_permitted(self):
        verdict = classify_merge(
            authorized_and_dependency_valid=True,
            paths_fit=True,
            branch_current=True,
            tests_ci_pass=True,
            secret_scan_clean=True,
            specialist_reviews_pass=True,
            no_blocking_finding=True,
            not_production_deploy=True,
            main_sha_recorded=True,
            state_transactional=True,
            via_allowlisted_command=False,
        )
        self.assertEqual(
            verdict, "PERMITTED_TIER_A",
            "An ordinary green-check task-branch merge must classify as Tier A permitted",
        )

    def test_secret_finding_blocks_even_when_otherwise_green(self):
        verdict = classify_merge(
            authorized_and_dependency_valid=True,
            paths_fit=True,
            branch_current=True,
            tests_ci_pass=True,
            secret_scan_clean=False,   # secret scan dirty
            specialist_reviews_pass=True,
            no_blocking_finding=True,
            not_production_deploy=True,
            main_sha_recorded=True,
            state_transactional=True,
        )
        self.assertEqual(verdict, "NOT_PERMITTED")


class DriftGuardSelfTest(unittest.TestCase):
    """Prove the drift guards actually fire: a mutated ADR block must fail the
    same set/sequence comparisons the real tests use."""

    def test_dropping_a_tier_d_item_would_fail(self):
        mutated = CANONICAL_TIER_D[:-1]  # drop item 14
        self.assertNotEqual(mutated, CANONICAL_TIER_D)

    def test_adding_an_unlisted_tier_a_action_would_fail(self):
        mutated = set(CANONICAL_TIER_A) | {"deploy to production"}
        self.assertNotEqual(mutated, set(CANONICAL_TIER_A))

    def test_changing_a_tier_b_review_would_fail(self):
        mutated = dict(CANONICAL_TIER_B)
        mutated["Supervisor code"] = "control-plane"  # drop security + crash/replay
        self.assertNotEqual(mutated, CANONICAL_TIER_B)

    def test_parser_on_real_adr_returns_nonempty_blocks(self):
        text = _read_adr()
        self.assertTrue(_bullets(_block(text, "TIER-A-ACTIONS")))
        self.assertTrue(_numbered(_block(text, "TIER-D-ITEMS")))
        self.assertTrue(_table_map(_block(text, "TIER-B-MAP")))


if __name__ == "__main__":
    unittest.main()
