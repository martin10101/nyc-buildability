"""Tests for the shared claim-class word module (task M5-T102, D-087 PKT-A),
scenarios AS-1 (one source) and AS-3 (full coverage + drift guard).

Offline and deterministic: stdlib + pytest only, no network, no I/O beyond reading
the writer sources for the drift/AST checks. This module is the single source of
truth for the claim vocabulary and the separator-collapsing screen; the per-writer
behaviour (separator variants refused as names / caller strings / title-block text)
lives in each writer's own test file.
"""

import ast
from pathlib import Path

import pytest

from app.cad import claim_words
from app.cad.claim_words import CLAIM_CLASS_WORDS, claim_key, contains_claim_word

API_ROOT = Path(__file__).resolve().parents[2]
CAD = API_ROOT / "app" / "cad"
WRITERS = ("dxf_writer", "glb_writer", "pdf_sheet_writer")


def _source(module: str) -> str:
    return (CAD / f"{module}.py").read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# AS-3: the canonical word list, pinned BY VALUE so an edit to the list reddens.
# --------------------------------------------------------------------------- #

def test_as3_canonical_word_list_pinned_by_value():
    """HARDCODED literal (a by-value import would make the pin tautological). Any
    edit to the shared list - a dropped word (weakened guard) or a new word -
    reddens this test, which is the drift guard the three writers rely on."""
    assert CLAIM_CLASS_WORDS == (
        "PERMITTED",
        "APPROVED",
        "CERTIFIED",
        "COMPLIANT",
        "LAWFUL",
        "LEGAL",
        "ENTITLEMENT",
        "GUARANTEED",
        "MAXIMUM ALLOWED",
        "AS OF RIGHT",
        "AS-OF-RIGHT",
    )
    assert isinstance(CLAIM_CLASS_WORDS, tuple)


# --------------------------------------------------------------------------- #
# claim_key: the ONE separator-collapsing matching key.
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "text, expected",
    [
        ("As_of_right", "AS OF RIGHT"),
        ("as-of-right", "AS OF RIGHT"),
        ("MAXIMUM  ALLOWED", "MAXIMUM ALLOWED"),
        ("Maximum.allowed", "MAXIMUM ALLOWED"),
        ("MAXIMUM\tALLOWED", "MAXIMUM ALLOWED"),
        ("12 MAIN ST", "12 MAIN ST"),
        ("AS ?OF RIGHT", "AS OF RIGHT"),  # the ASCII-sanitised form of a non-ASCII sep
    ],
)
def test_claim_key_collapses_separator_runs(text, expected):
    assert claim_key(text) == expected


# --------------------------------------------------------------------------- #
# contains_claim_word: the ONE screen. Separator variants match; clean text does
# not; the printed (ASCII-sanitised) form is caught when passed alongside the raw.
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("word", CLAIM_CLASS_WORDS)
def test_every_canonical_word_is_detected(word):
    """Full coverage: every canonical word is found in a hosting string."""
    assert contains_claim_word(f"12 {word.title()} st") is not None


@pytest.mark.parametrize(
    "text",
    ["As_of_right", "as-of-right", "Maximum_allowed", "MAXIMUM  ALLOWED", "As.of.right"],
)
def test_separator_variants_are_detected(text):
    assert contains_claim_word(text) is not None


@pytest.mark.parametrize("text", ["12 MAIN ST", "12 PERMIT ST", "1 LEGACY PL", "", "Tower"])
def test_clean_text_returns_none(text):
    assert contains_claim_word(text) is None


def test_returns_the_canonical_word_in_tuple_order():
    assert contains_claim_word("As_of_right tower") == "AS OF RIGHT"
    assert contains_claim_word("Approved massing") == "APPROVED"


def test_screens_every_form_passed():
    """Callers that print a sanitised form pass BOTH forms; a match in ANY is a hit.
    'AS ſOF RIGHT' upper-cases to 'AS SOF RIGHT' (ſ -> S) and its RAW form is clean,
    but the ASCII-sanitised printed form 'AS ?OF RIGHT' is caught."""
    assert contains_claim_word("AS ſOF RIGHT") is None          # raw form alone: clean
    assert contains_claim_word("AS ſOF RIGHT", "AS ?OF RIGHT") == "AS OF RIGHT"
    assert contains_claim_word("clean text", "12 As_of_right ave") == "AS OF RIGHT"
    assert contains_claim_word() is None                              # no texts: clean


# --------------------------------------------------------------------------- #
# AS-1 (one source): the word literal and the matcher live ONLY in claim_words;
# each writer imports the shared module and dxf keeps an identity-equal alias.
# --------------------------------------------------------------------------- #

def _has_word_literal(source: str) -> bool:
    """True if the source defines a tuple/list literal of the claim vocabulary."""
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Tuple, ast.List)):
            strings = {
                elt.value
                for elt in node.elts
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
            }
            if {"PERMITTED", "ENTITLEMENT", "MAXIMUM ALLOWED"} <= strings:
                return True
    return False


def _defines_a_matcher(source: str) -> bool:
    """True if the source defines its own claim matcher (a claim_key-style function
    or the separator-collapsing regex pattern)."""
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.FunctionDef) and "claim_key" in node.name:
            return True
    return "[^A-Z0-9]" in source


def test_as1_only_claim_words_holds_the_word_literal():
    assert _has_word_literal(_source("claim_words")), "the canonical list lives here"
    for module in WRITERS:
        assert not _has_word_literal(_source(module)), f"{module} keeps a local word literal"


def test_as1_only_claim_words_holds_the_matcher():
    assert _defines_a_matcher(_source("claim_words")), "the matcher lives here"
    for module in WRITERS:
        assert not _defines_a_matcher(_source(module)), f"{module} keeps its own matcher"


def test_as1_each_writer_imports_the_shared_module():
    for module in WRITERS:
        modules = {
            node.module
            for node in ast.walk(ast.parse(_source(module)))
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        assert "app.cad.claim_words" in modules, f"{module} does not import the shared module"


def test_as1_dxf_alias_is_identity_equal_to_the_shared_tuple():
    from app.cad import dxf_writer, pdf_sheet_writer

    assert dxf_writer.CLAIM_CLASS_WORDS is CLAIM_CLASS_WORDS
    assert pdf_sheet_writer.CLAIM_CLASS_WORDS is CLAIM_CLASS_WORDS
    assert dxf_writer.contains_claim_word is contains_claim_word
    assert claim_words.contains_claim_word is contains_claim_word
