"""Shared strict-JSON-safety sanitizer for the scenario optimization engine (M5-T009).

Single source of truth for the sanitizer that ``ranking`` and ``sensitivity`` both apply to
their emitted echoes. Extracted (behavior-neutral) from the copies previously duplicated in
``ranking.py`` and ``sensitivity.py``: for every JSON-representable input the rendering is
byte-identical to those copies, so both consumers keep their public outputs unchanged.

The sanitizer turns an arbitrary value into a strict-JSON-safe rendering: a
NaN/+-Inf/negative/float-overflowing number or a non-JSON-serializable object becomes a TYPED,
bounded placeholder marker; ``dict``/``list``/``tuple`` are walked (tuples emit as lists);
a finite non-negative number, ``bool``, ``None`` and ``str`` pass through. The result contains
no NaN/Inf/negative number and no non-serializable value, embeds no non-deterministic object
address, and preserves insertion order, so ``json.dumps(result, allow_nan=False)`` never raises
and identical inputs render byte-identically.

Defense-in-depth (M5-T009 L2): :func:`_json_safe` walks with an EXPLICIT TRAVERSAL STACK (a heap
list), not native call recursion, so the sanitizer itself never consumes the interpreter call
stack and never raises ``RecursionError`` while building its output - regardless of the process
recursion limit or the caller's own stack depth. A container already on the current traversal PATH
(a genuine cycle) becomes a typed ``cycle`` marker via a path-scoped ancestor set; a
shared-but-acyclic sub-value (a DAG, e.g. the same dict in two list slots) is NOT a cycle and is
emitted in full at each position.

Container nesting is bounded to a fixed, documented ``_MAX_JSON_SAFE_DEPTH``: a container nested
deeper than that becomes a typed ``max_depth`` marker instead of being descended into. This bound
is REQUIRED for the strict-JSON-safety guarantee, not an optimization: ``json.dumps`` recurses once
per nesting level (in C), so an unbounded, pathologically-deep rendering - even one the iterative
sanitizer could build WITHOUT raising - would make the downstream
``json.dumps(result, allow_nan=False)`` raise ``RecursionError`` and BREAK the very contract this
module upholds. Producing deeply nested containers alone does not make ``json.dumps`` safe. The
bound sits ABOVE every depth a real scenario/derive structure (and the retired RECURSIVE sanitizer
this replaced) could ever render, so it truncates no previously-serializable output (the 410-level
acyclic regressions still render in full), and BELOW the depth at which ``json.dumps`` recurses to
``RecursionError``, so every output stays strict-JSON-serializable. It is a FIXED constant - never
sized from ``sys.getrecursionlimit()`` (which would go stale and assume the caller's stack), so
changing the recursion limit never moves it. The only values bounded to a marker are a cycle (which
could not be rendered at all) and depth beyond the documented maximum (which ``json.dumps`` could
not serialize).

Stdlib-only, deterministic, offline (no I/O). Internal underscore module: not part of the
``app.scenario`` public facade.
"""

from __future__ import annotations

import math
from typing import Any

__all__ = [
    "_bounded_repr",
    "_json_safe",
    "_json_safe_mapping",
    "_safe_key",
    "_safe_scalar_repr",
    "_unsafe_key_token",
    "_unsafe_marker",
]


#: Max characters of a malformed value's repr surfaced in its typed placeholder marker, so a
#: pathological value (e.g. a 400-digit int) cannot bloat the output.
_UNSAFE_REPR_LIMIT = 120

#: Max bit length of an integer whose EXACT decimal repr is small and safe to surface. A larger
#: integer is described by magnitude (sign + bit length) instead of decimal-expanded, because a
#: full decimal expansion is both unbounded work and, past CPython's int->str conversion ceiling
#: (4300 digits by default), a ``ValueError`` - so an UNGUARDED ``repr`` of an arbitrarily large
#: integer would raise and crash the sanitizer. 256 bits is ~77 decimal digits: comfortably under
#: ``_UNSAFE_REPR_LIMIT`` and vastly under the interpreter's conversion ceiling.
_INT_DECIMAL_SAFE_BITS = 256

#: Reserved prefix for the synthesized replacement of a dict key that is NOT strict-JSON-safe
#: (an arbitrary object, or a non-finite / float-overflowing numeric key). The token carries a
#: deterministic bounded descriptor of the rejected key - never an object address - so the
#: emitted output is byte-identical run-to-run; :func:`_json_safe_mapping` positionally
#: de-collides two distinct rejected keys that render to the same token.
_UNSAFE_KEY_TOKEN_PREFIX = "__unsafe_key__"

#: Maximum container-nesting depth :func:`_json_safe` renders in full before substituting a typed
#: ``max_depth`` marker for anything deeper. REQUIRED for strict-JSON-safety, NOT an optimization:
#: ``json.dumps`` recurses once per nesting level (in C), so an unbounded rendering of a
#: pathologically-deep value - which the iterative traversal could build without raising - would
#: make the downstream ``json.dumps(result, allow_nan=False)`` raise ``RecursionError`` and break
#: the guarantee this module exists to uphold. 500 sits ABOVE every real scenario/derive structure
#: and above the ~480-level ceiling at which the RETIRED recursive sanitizer would itself have
#: raised under the default 1000-frame limit (so it truncates no previously-serializable output,
#: and the 410-level acyclic regressions still render in full), yet FAR BELOW the depth at which
#: ``json.dumps`` recurses to ``RecursionError`` (~900 from a realistic call stack under the default
#: limit; the separate ~1500 C-recursion limit on 3.12), so the bounded output always serializes. A
#: FIXED constant, deliberately NOT derived from ``sys.getrecursionlimit()`` (the retired guard did,
#: and both went stale and truncated previously-successful outputs); changing the recursion limit
#: never moves it.
_MAX_JSON_SAFE_DEPTH = 500


def _bounded_repr(rendered: str) -> str:
    """An already-rendered repr truncated to a bounded length with an explicit marker."""
    if len(rendered) <= _UNSAFE_REPR_LIMIT:
        return rendered
    return rendered[:_UNSAFE_REPR_LIMIT] + "...(truncated)"


def _safe_scalar_repr(value: Any) -> str:
    """A deterministic, bounded textual rendering of ``value`` that NEVER triggers CPython's
    integer string-conversion limit and NEVER embeds a non-deterministic object address:

    * ``bool`` / ``float`` -> ``repr`` (always short and safe: ``True``, ``nan``, ``-0.5`` ...).
    * ``int`` -> its exact decimal ``repr`` when small (``bit_length <= _INT_DECIMAL_SAFE_BITS``),
      else a magnitude descriptor ``int(sign=..., bit_length=...)`` - so an arbitrarily large
      integer is DESCRIBED, never decimal-expanded (which would be unbounded work and, past the
      interpreter's ceiling, a ``ValueError``).
    * anything else -> ``<TypeName>`` (its type only; NEVER ``repr``, whose default for an
      arbitrary object embeds a transient id and would break byte-identical determinism)."""
    if isinstance(value, bool):
        return repr(value)
    if isinstance(value, int):
        if value.bit_length() <= _INT_DECIMAL_SAFE_BITS:
            return repr(value)
        return f"int(sign={'-' if value < 0 else '+'}, bit_length={value.bit_length()})"
    if isinstance(value, float):
        return repr(value)
    return f"<{type(value).__name__}>"


def _unsafe_marker(kind: str, value: Any) -> dict:
    """A TYPED, strict-JSON-safe placeholder standing in for a malformed emitted value, so a
    caller's malformed value is surfaced HONESTLY (typed) yet never echoed RAW. Numeric kinds
    (and the ``cycle`` defense-in-depth kind) carry a deterministic, bounded, decimal-repr-SAFE
    rendering (:func:`_safe_scalar_repr`, so an arbitrarily large integer is described by
    magnitude rather than decimal-expanded and can never raise CPython's int->str limit, and a
    container surfaces only its type name); an ``unsupported`` object carries only its
    (deterministic) type name - never its ``repr``, which can embed a non-deterministic object id
    and break byte-identical determinism."""
    marker = {
        "unsafe_value_removed": True,
        "unsafe_kind": kind,
        "unsafe_value_type": type(value).__name__,
    }
    if kind != "unsupported":
        marker["unsafe_value_repr"] = _bounded_repr(_safe_scalar_repr(value))
    return marker


def _unsafe_key_token(key: Any) -> str:
    """Deterministic, strict-JSON-safe replacement string for a dict key that cannot be a JSON
    object key. Built from :func:`_safe_scalar_repr`, so an arbitrary object surfaces its TYPE
    only (never its address-bearing ``repr``) and an arbitrarily large integer surfaces its
    MAGNITUDE (never an unguarded decimal expansion) - the token neither raises nor varies
    run-to-run."""
    return f"{_UNSAFE_KEY_TOKEN_PREFIX}:{_bounded_repr(_safe_scalar_repr(key))}"


def _safe_key(key: Any) -> Any:
    """A dict key guaranteed safe for ``json.dumps(..., allow_nan=False)``: a
    ``str``/``None``/``bool`` verbatim; a FINITE ``int``/``float`` verbatim (json coerces the
    latter to a string key); a non-finite / float-overflowing numeric key or ANY other type ->
    a deterministic typed :func:`_unsafe_key_token`. An arbitrary object key is therefore NEVER
    rendered through its address-bearing ``repr`` (which would leak a transient id and break
    byte-identical determinism) and an arbitrarily large integer key is NEVER decimal-expanded
    (which would raise past CPython's int->str ceiling), so no key can make ``json.dumps``
    raise or the output non-deterministic."""
    if isinstance(key, str) or key is None or isinstance(key, bool):
        return key
    if isinstance(key, int | float):
        try:
            as_float = float(key)
        except (OverflowError, ValueError):
            return _unsafe_key_token(key)
        return key if math.isfinite(as_float) else _unsafe_key_token(key)
    return _unsafe_key_token(key)


def _safe_scalar(value: Any) -> Any:
    """Strict-JSON-safe rendering of a NON-container (scalar / leaf) value: a
    NaN/+-Inf/negative/float-overflowing number or a non-JSON-serializable object becomes a typed
    :func:`_unsafe_marker`; a finite non-negative number, ``bool``, ``None`` and ``str`` pass
    through. Containers are handled by :func:`_json_safe`'s traversal, never here."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        try:
            as_float = float(value)
        except (OverflowError, ValueError):
            return _unsafe_marker("overflow", value)
        if math.isnan(as_float):
            return _unsafe_marker("nan", value)
        if math.isinf(as_float):
            return _unsafe_marker("infinity", value)
        if as_float < 0.0:
            return _unsafe_marker("negative", value)
        return value
    if value is None or isinstance(value, str):
        return value
    return _unsafe_marker("unsupported", value)


def _safe_output_key(out: dict, key: Any) -> Any:
    """The de-collided strict-JSON-safe key under which ``key``'s rendered value is stored in the
    partially-built output dict ``out``. Two DISTINCT source keys that collapse to the SAME safe
    key (e.g. two different rejected objects that render to one typed token) are de-collided with a
    deterministic ``#N`` positional suffix, so a rejected key never SILENTLY overwrites another;
    insertion order is deterministic so the suffixes are deterministic too."""
    safe_key = _safe_key(key)
    if safe_key in out:
        base = safe_key if isinstance(safe_key, str) else _unsafe_key_token(key)
        suffix = 1
        while f"{base}#{suffix}" in out:
            suffix += 1
        safe_key = f"{base}#{suffix}"
    return safe_key


class _Frame:
    """One open container on the explicit traversal stack: its SOURCE container, the OUTPUT
    container being filled for it (already linked into its parent), and the resumable ITEMS
    iterator over the source's ``(key_or_None, value)`` pairs."""

    __slots__ = ("source", "output", "items")

    def __init__(self, source: Any, output: Any, items: Any) -> None:
        self.source = source
        self.output = output
        self.items = items


def _new_output(container: Any) -> Any:
    """A fresh empty OUTPUT container mirroring ``container``'s JSON shape (dict -> dict; list or
    tuple -> list, since a tuple emits as a JSON array)."""
    return {} if isinstance(container, dict) else []


def _container_items(container: Any) -> Any:
    """A resumable iterator of ``(key_or_None, value)`` pairs for a source container: a dict
    yields ``(key, value)``; a list/tuple yields ``(None, item)`` (the key slot is unused - the
    output list appends in order)."""
    if isinstance(container, dict):
        return iter(container.items())
    return ((None, item) for item in container)


def _place(frame: _Frame, src_key: Any, rendered: Any) -> None:
    """Store an already-rendered child in its parent's OUTPUT container: append to a list, or
    insert under a de-collided strict-JSON-safe key (:func:`_safe_output_key`) into a dict."""
    out = frame.output
    if isinstance(out, list):
        out.append(rendered)
    else:
        out[_safe_output_key(out, src_key)] = rendered


def _json_safe(value: Any) -> Any:
    """A strict-JSON-safe rendering of ``value`` (insertion order preserved): a
    NaN/+-Inf/negative/float-overflowing number or a non-JSON-serializable object becomes a
    typed :func:`_unsafe_marker`; ``dict``/``list``/``tuple`` are walked (tuples emit as
    lists); a finite non-negative number, ``bool``, ``None`` and ``str`` pass through. The
    result contains no NaN/Inf/negative number and no non-serializable value, so
    ``json.dumps(result, allow_nan=False)`` never raises. Never mutates ``value`` (it builds
    fresh containers), so the caller's input stays byte-unchanged.

    Defense-in-depth (L2): the walk uses an EXPLICIT TRAVERSAL STACK (a heap list of
    :class:`_Frame`), not native call recursion, so building the output never consumes the
    interpreter call stack and never raises ``RecursionError`` - independent of
    ``sys.getrecursionlimit()`` and of the caller's own stack depth. ``ancestors`` holds the ``id``
    of every source container on the CURRENT traversal path (added on descent, removed when a
    container's frame is exhausted); a child whose ``id`` is already in it is a genuine cycle and
    becomes a typed ``cycle`` marker. Because ``ancestors`` is path-scoped, a shared-but-ACYCLIC
    sub-value emitted in more than one position is rendered in full each time. Container nesting is
    bounded to :data:`_MAX_JSON_SAFE_DEPTH`: a container deeper than that becomes a typed
    ``max_depth`` marker rather than being descended into - REQUIRED so the downstream
    ``json.dumps(result, allow_nan=False)`` (which itself recurses once per nesting level) never
    raises; deeply nested containers alone do not make ``json.dumps`` safe. The bound sits above
    every real structure and above the 410-level regressions (which still render in full) and below
    ``json.dumps``'s own recursion ceiling, so no previously-serializable output is truncated; the
    only bounded values are a cycle (which could not be rendered at all) and depth beyond the
    documented maximum (which ``json.dumps`` could not serialize)."""
    if not isinstance(value, dict | list | tuple):
        return _safe_scalar(value)

    root = _new_output(value)
    ancestors: set[int] = {id(value)}
    stack: list[_Frame] = [_Frame(value, root, _container_items(value))]

    while stack:
        frame = stack[-1]
        descended = False
        for src_key, item in frame.items:
            if isinstance(item, dict | list | tuple):
                if id(item) in ancestors:
                    _place(frame, src_key, _unsafe_marker("cycle", item))
                    continue
                if len(stack) >= _MAX_JSON_SAFE_DEPTH:
                    # Descending would push output nesting past the documented bound; ``json.dumps``
                    # recurses per level, so the deeper value is truncated to a typed ``max_depth``
                    # marker to keep ``json.dumps(result, allow_nan=False)`` from raising.
                    _place(frame, src_key, _unsafe_marker("max_depth", item))
                    continue
                child_out = _new_output(item)
                _place(frame, src_key, child_out)
                ancestors.add(id(item))
                stack.append(_Frame(item, child_out, _container_items(item)))
                descended = True
                break
            _place(frame, src_key, _safe_scalar(item))
        if not descended:
            ancestors.discard(id(frame.source))
            stack.pop()
    return root


def _json_safe_mapping(value: dict) -> dict:
    """Strict-JSON-safe rendering of a mapping (insertion order preserved): each key is made
    JSON-safe and de-collided by :func:`_safe_output_key` and each value by :func:`_json_safe`.
    Never raises (keys are already safe; values go through the iterative, RecursionError-free
    :func:`_json_safe`)."""
    out: dict = {}
    for key, item in value.items():
        out[_safe_output_key(out, key)] = _json_safe(item)
    return out
