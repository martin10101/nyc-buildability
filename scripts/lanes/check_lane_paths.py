#!/usr/bin/env python3
"""Lane path check (task M0-T164, D-090; derived lane plan docs/lanes/PARALLEL_BUILD_PLAN.md §7).

Two checks, stdlib only:

* ``--coverage``: every tracked file (``git ls-files``) has exactly one owning lane in
  ``docs/lanes/OWNERSHIP.yaml``. The first matching rule wins, so a file has one owner by
  construction; a file no rule matches is an orphan and fails the check.
* branch check (default): on a branch named ``lane-<x>/...`` every file the branch changes
  relative to its base must be owned by lane ``x``. Branches without the ``lane-`` prefix
  (``task/``, ``control/``, the integration branch) are not lane branches and pass. Locally
  the base is the merge-base with ``origin/<integration_branch>``; in a pull_request CI run
  (``--pr-merge``) it is the first parent recorded in GitHub's merge commit, never the event's
  ``base.sha``, which is stale when the base advanced before the run.

Exit status: 0 pass, 1 violation, 2 usage or environment error (fail closed).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OWNERSHIP = REPO_ROOT / "docs" / "lanes" / "OWNERSHIP.yaml"
LANE_BRANCH_RE = re.compile(r"^lane-([a-e])/", re.IGNORECASE)
SHA_RE = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")
MAX_LISTED = 50


class OwnershipError(ValueError):
    """The ownership file is malformed (fail closed)."""


# ---------------------------------------------------------------------------
# Minimal YAML-subset reader: block mappings, block sequences, scalars, comments.
# ---------------------------------------------------------------------------


def _strip_comment(line: str) -> str:
    out, quote = [], None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _scalar(text: str):
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def _split_key(text: str, lineno: int):
    match = re.fullmatch(r"([^:]+?):(?:\s+(.*))?", text)
    if not match:
        raise OwnershipError(f"line {lineno}: expected 'key: value', got {text!r}")
    key = _scalar(match.group(1))
    return str(key), match.group(2)


def parse_yaml_subset(source: str):
    lines = []
    for lineno, raw in enumerate(source.splitlines(), start=1):
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise OwnershipError(f"line {lineno}: tabs are not allowed in indentation")
        body = _strip_comment(raw)
        if body.strip():
            lines.append((len(body) - len(body.lstrip(" ")), body.strip(), lineno))
    value, index = _parse_block(lines, 0, 0)
    if index != len(lines):
        raise OwnershipError(f"line {lines[index][2]}: unexpected indentation")
    return value


def _parse_block(lines, index, indent):
    if index >= len(lines):
        return None, index
    if lines[index][1].startswith("- ") or lines[index][1] == "-":
        return _parse_sequence(lines, index, indent)
    return _parse_mapping(lines, index, indent)


def _parse_mapping(lines, index, indent):
    result = {}
    while index < len(lines):
        col, text, lineno = lines[index]
        if col < indent:
            break
        if col > indent:
            raise OwnershipError(f"line {lineno}: unexpected indentation")
        if text.startswith("-"):
            break
        key, rest = _split_key(text, lineno)
        if key in result:
            raise OwnershipError(f"line {lineno}: duplicate key {key!r}")
        index += 1
        if rest:
            result[key] = _scalar(rest)
        elif index < len(lines) and lines[index][0] > indent:
            result[key], index = _parse_block(lines, index, lines[index][0])
        elif index < len(lines) and lines[index][0] == indent and lines[index][1].startswith("-"):
            result[key], index = _parse_sequence(lines, index, indent)
        else:
            result[key] = None
    return result, index


def _parse_sequence(lines, index, indent):
    result = []
    while index < len(lines):
        col, text, lineno = lines[index]
        if col != indent or not text.startswith("-"):
            if col > indent:
                raise OwnershipError(f"line {lineno}: unexpected indentation")
            break
        item = text[1:].strip()
        index += 1
        if not item:
            if index < len(lines) and lines[index][0] > indent:
                value, index = _parse_block(lines, index, lines[index][0])
            else:
                value = None
            result.append(value)
            continue
        if re.fullmatch(r"[^\"'][^:]*:(\s.*)?", item):
            # "- key: value" opens a mapping whose further keys sit at indent + 2.
            child_indent = indent + 2
            key, rest = _split_key(item, lineno)
            mapping = {}
            if rest:
                mapping[key] = _scalar(rest)
            elif index < len(lines) and lines[index][0] > child_indent:
                mapping[key], index = _parse_block(lines, index, lines[index][0])
            elif (index < len(lines) and lines[index][0] == child_indent
                  and lines[index][1].startswith("-")):
                mapping[key], index = _parse_sequence(lines, index, child_indent)
            else:
                mapping[key] = None
            if index < len(lines) and lines[index][0] == child_indent \
                    and not lines[index][1].startswith("-"):
                more, index = _parse_mapping(lines, index, child_indent)
                for extra_key in more:
                    if extra_key in mapping:
                        raise OwnershipError(f"line {lineno}: duplicate key {extra_key!r}")
                mapping.update(more)
            result.append(mapping)
        else:
            result.append(_scalar(item))
    return result, index


# ---------------------------------------------------------------------------
# Ownership model
# ---------------------------------------------------------------------------


def glob_to_regex(pattern: str) -> re.Pattern:
    parts, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            parts.append("(?:[^/]+/)*")
            i += 3
        elif pattern.startswith("**", i):
            parts.append(".*")
            i += 2
        elif pattern[i] == "*":
            parts.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            parts.append("[^/]")
            i += 1
        else:
            parts.append(re.escape(pattern[i]))
            i += 1
    return re.compile("^" + "".join(parts) + "$")


@dataclass(frozen=True)
class Rule:
    lane: str
    glob: str
    regex: re.Pattern


class Ownership:
    def __init__(self, lanes: dict, rules: list[Rule], integration_branch: str):
        self.lanes = lanes
        self.rules = rules
        self.integration_branch = integration_branch

    @classmethod
    def load(cls, path: Path) -> Ownership:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise OwnershipError(f"cannot read {path}: {exc}") from exc
        return cls.from_text(text)

    @classmethod
    def from_text(cls, text: str) -> Ownership:
        data = parse_yaml_subset(text)
        if not isinstance(data, dict):
            raise OwnershipError("top level must be a mapping")
        lanes = data.get("lanes")
        if not isinstance(lanes, dict) or sorted(lanes) != ["A", "B", "C", "D", "E"]:
            raise OwnershipError("'lanes' must define exactly A, B, C, D, E")
        raw_rules = data.get("rules")
        if not isinstance(raw_rules, list) or not raw_rules:
            raise OwnershipError("'rules' must be a non-empty list")
        rules = []
        for n, entry in enumerate(raw_rules, start=1):
            if not isinstance(entry, dict) or set(entry) != {"lane", "globs"}:
                raise OwnershipError(f"rule {n}: needs exactly 'lane' and 'globs'")
            lane, globs = entry["lane"], entry["globs"]
            if lane not in lanes:
                raise OwnershipError(f"rule {n}: unknown lane {lane!r}")
            if not isinstance(globs, list) or not globs:
                raise OwnershipError(f"rule {n}: 'globs' must be a non-empty list")
            for glob in globs:
                if not isinstance(glob, str) or not glob or glob.startswith("/"):
                    raise OwnershipError(f"rule {n}: bad glob {glob!r}")
                rules.append(Rule(lane, glob, glob_to_regex(glob)))
        branch = data.get("integration_branch")
        if not isinstance(branch, str) or not branch:
            raise OwnershipError("'integration_branch' is required")
        return cls(lanes, rules, branch)

    def owner(self, path: str) -> str | None:
        for rule in self.rules:
            if rule.regex.match(path):
                return rule.lane
        return None


def lane_of_branch(branch: str) -> str | None:
    match = LANE_BRANCH_RE.match(branch or "")
    return match.group(1).upper() if match else None


def orphans(ownership: Ownership, files: list[str]) -> list[str]:
    return [f for f in files if ownership.owner(f) is None]


def violations(ownership: Ownership, lane: str, files: list[str]) -> list[tuple[str, str]]:
    found = []
    for path in files:
        owner = ownership.owner(path)
        if owner != lane:
            found.append((path, owner or "no owner"))
    return found


# ---------------------------------------------------------------------------
# git plumbing
# ---------------------------------------------------------------------------


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout


def tracked_files() -> list[str]:
    return [line for line in _git("ls-files", "-z").split("\0") if line]


def is_shallow() -> bool:
    return _git("rev-parse", "--is-shallow-repository").strip() == "true"


def ownership_at(commit: str, path: Path) -> str | None:
    """OWNERSHIP.yaml text as committed at ``commit``, or None when that commit has none."""
    rel = path.resolve().relative_to(REPO_ROOT).as_posix()
    completed = subprocess.run(
        ["git", "show", f"{commit}:{rel}"], cwd=REPO_ROOT, capture_output=True, text=True,
        check=False,
    )
    return completed.stdout if completed.returncode == 0 else None


def changed_files(base: str, fetch: bool) -> list[str]:
    ref = f"origin/{base}"
    if fetch:
        refspec = f"+refs/heads/{base}:refs/remotes/{ref}"
        if is_shallow():
            # Only an already-shallow clone (CI) gets depth-limited fetches; a --depth fetch
            # would silently make a full clone, and every worktree sharing it, shallow.
            _git("fetch", "--no-tags", "--depth=500", "origin", refspec)
            _git("fetch", "--no-tags", "--deepen=500", "origin")
        else:
            _git("fetch", "--no-tags", "origin", refspec)
    merge_base = _git("merge-base", ref, "HEAD").strip()
    output = _git("diff", "--name-only", "--no-renames", "-z", merge_base, "HEAD")
    return [line for line in output.split("\0") if line]


def commit_parents(commit: str = "HEAD") -> list[str]:
    """Parent ids recorded in ``commit``'s own object. Read with ``git cat-file`` rather than
    ``HEAD^1``: a shallow checkout grafts its boundary commit to have no parents, so revision
    syntax cannot see them there, while the raw object still lists them."""
    raw = _git("cat-file", "commit", commit)
    header = raw.split("\n\n", 1)[0]
    parents = [line[len("parent "):].strip() for line in header.splitlines()
               if line.startswith("parent ")]
    for parent in parents:
        if not SHA_RE.fullmatch(parent):
            raise RuntimeError(f"{commit} records a malformed parent id {parent!r}")
    return parents


def _has_commit(sha: str) -> bool:
    completed = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=REPO_ROOT, capture_output=True,
        check=False,
    )
    return completed.returncode == 0


def merge_first_parent(fetch: bool) -> str:
    """First parent of HEAD, where HEAD must be GitHub's pull_request merge commit (the PR head
    merged onto the base tip). That parent is the base the merge was actually built on; the
    event payload's ``base.sha`` can be older when the base advanced before the run, and
    diffing from it pulls other PRs' files into this one (PR #261). Fails closed: HEAD must
    have exactly two parents and the first must be present locally or fetchable."""
    head = _git("rev-parse", "HEAD").strip()
    parents = commit_parents("HEAD")
    if len(parents) != 2:
        raise RuntimeError(
            f"HEAD {head} has {len(parents)} parent(s), not 2: it is not GitHub's pull_request "
            "merge commit, so the PR's change set cannot be established")
    first = parents[0]
    if not _has_commit(first):
        if not fetch:
            raise RuntimeError(f"merge commit's first parent {first} is not present locally "
                               "(pass --fetch to fetch it)")
        if is_shallow():
            _git("fetch", "--no-tags", "--depth=1", "origin", first)
        else:
            _git("fetch", "--no-tags", "origin", first)
        if not _has_commit(first):
            raise RuntimeError(f"merge commit's first parent {first} is still missing after "
                               "fetching it")
    return first


def changed_files_vs_merge_parent(fetch: bool) -> tuple[str, list[str]]:
    """Tree diff from HEAD's first parent to HEAD: exactly the PR's change set when HEAD is
    GitHub's merge commit. Needs only those two commits, so the CI checkout stays shallow."""
    parent = merge_first_parent(fetch)
    output = _git("diff", "--name-only", "--no-renames", "-z", parent, "HEAD")
    return parent, [line for line in output.split("\0") if line]


def current_branch() -> str:
    for var in ("LANE_BRANCH", "GITHUB_HEAD_REF", "GITHUB_REF_NAME"):
        if os.environ.get(var):
            return os.environ[var]
    return _git("rev-parse", "--abbrev-ref", "HEAD").strip()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_list(title: str, rows: list[str]) -> None:
    print(title)
    for row in rows[:MAX_LISTED]:
        print(f"  - {row}")
    if len(rows) > MAX_LISTED:
        print(f"  ... and {len(rows) - MAX_LISTED} more")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ownership", type=Path, default=DEFAULT_OWNERSHIP)
    parser.add_argument("--coverage", action="store_true",
                        help="check that every tracked file has an owning lane")
    parser.add_argument("--branch", help="branch name (default: CI env or current branch)")
    parser.add_argument("--base", help="base branch (default: integration_branch)")
    parser.add_argument("--pr-merge", action="store_true",
                        help="HEAD is GitHub's pull_request merge commit: diff its first parent "
                             "(read from the commit itself) to HEAD (CI pull_request runs)")
    parser.add_argument("--fetch", action="store_true",
                        help="fetch the base branch first, or with --pr-merge the merge's first "
                             "parent when it is missing (CI)")
    parser.add_argument("--files", nargs="*", help="check these paths instead of a git diff")
    args = parser.parse_args(argv)

    try:
        ownership = Ownership.load(args.ownership)
    except OwnershipError as exc:
        print(f"LANE PATH CHECK ERROR: {args.ownership}: {exc}")
        return 2

    try:
        if args.coverage:
            files = args.files if args.files is not None else tracked_files()
            missing = orphans(ownership, files)
            if missing:
                _print_list(f"LANE COVERAGE FAIL: {len(missing)} file(s) have no owning lane "
                            f"in {args.ownership.name}:", missing)
                return 1
            print(f"LANE COVERAGE PASS: {len(files)} file(s), each owned by exactly one lane.")
            return 0

        branch = args.branch if args.branch else current_branch()
        lane = lane_of_branch(branch)
        if lane is None:
            print(f"LANE PATH CHECK SKIPPED: {branch!r} is not a lane-<x>/ branch.")
            return 0
        base = args.base or ownership.integration_branch
        if args.files is not None:
            files = args.files
        elif args.pr_merge:
            parent, files = changed_files_vs_merge_parent(args.fetch)
            print(f"LANE PATH CHECK: diffing merge commit HEAD against its first parent {parent}.")
            if lane != "C":
                # A lane other than C (which owns the map) is judged by the map at its base, so
                # a PR cannot widen its own paths by editing OWNERSHIP.yaml.
                base_text = ownership_at(parent, args.ownership)
                if base_text is not None:
                    ownership = Ownership.from_text(base_text)
        else:
            files = changed_files(base, args.fetch)
    except (RuntimeError, OwnershipError) as exc:
        print(f"LANE PATH CHECK ERROR: {exc}")
        return 2

    bad = violations(ownership, lane, files)
    if bad:
        _print_list(f"LANE PATH CHECK FAIL: branch {branch!r} is lane {lane}; "
                    f"{len(bad)} of {len(files)} changed file(s) belong elsewhere "
                    "(write docs/lanes/requests/<X>-<n>.md instead):",
                    [f"{path} (owner: {owner})" for path, owner in bad])
        return 1
    print(f"LANE PATH CHECK PASS: branch {branch!r} (lane {lane}) changes {len(files)} "
          "file(s), all owned by its lane.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
