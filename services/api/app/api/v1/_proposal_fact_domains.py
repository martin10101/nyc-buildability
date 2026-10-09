"""BP-5 caller-fact vocabulary validation for POST /api/v1/proposal-checks (M5-T061, DB-039).

Extracted from :mod:`app.api.v1.proposal_checks_api` at the M5-T061 seam: once the
registry-derived NUMERIC bounds (DB-039(d)) landed beside the enum-domain discipline the route
crossed its modularity justify tier, so the caller ``lot_rule_facts`` discipline lives here as
one cohesive responsibility - the boundary label primitives (:data:`MAX_LABEL_LEN`,
:func:`_require_label`), the value-TYPE table, the fact-KEY bound, and the registry-DERIVED
enum-domain + numeric-bound checks. The route imports every name it needs from here; NOTHING here
imports the route, so there is no import cycle.

IMPORT-TIME GUARD BLAST RADIUS (DB-039(b) / M5-T057 G3-F6):
:func:`_assert_fact_type_table_covers_vocabulary`
runs at IMPORT time, and ``app/main.py`` imports the route (which imports THIS module)
unconditionally, so a drift between the value-type table and
:data:`~app.rules.proposal_checks.CALLER_RULE_INPUT_NAMES` fails the WHOLE app at boot - NOT just
the flag-gated ``/proposal-checks`` route. That blast radius is DELIBERATE and fail-closed (a
mapped input silently skipping type/domain validation is a fail-open we never want shipped, and
CI catches the drift), but it EXCEEDS the feature flag and is called out here so a future edit
knows the cost of the drift.

Domains are the registry's OWN declared vocabulary - ``InputSpec.enum`` and the numeric
``minimum`` / ``maximum`` / ``exclusive_minimum`` / ``exclusive_maximum`` bounds
(:mod:`app.rules.models`) - NEVER an invented list or limit. A name is narrowed in a dimension
only when EVERY rule that declares it constrains it in that dimension, and the effective bound
kept is the MOST PERMISSIVE across those rules, so a value refused at this boundary is one that
every declaring rule would already fail-close on (see :func:`derive_input_domains`).
"""

from __future__ import annotations

import re
import weakref
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.rules.proposal_checks import CALLER_RULE_INPUT_NAMES

if TYPE_CHECKING:
    from app.rules.registry import RuleRegistry

# --- BP-2 boundary label discipline (shared by the route) -------------------------------------
#: Length cap for a boundary label/id (``scenario_label`` / ``proposal_id`` / lot-side ids /
#: block wall ids / fact keys). Generous for a real label, far below any paste/injection length.
MAX_LABEL_LEN = 200
#: Conservative charset: alphanumerics, space, and a small set of id-safe punctuation. Anything
#: else (control chars incl. a trailing newline, markup, quotes, path separators) is a typed
#: refusal. Matched with ``fullmatch`` over the WHOLE value: an unanchored ``re.match`` (or a
#: trailing ``$``) accepts a value with a trailing newline ("foo\n" - ``$`` matches just before
#: it), so the entire string, not a prefix, must be in the charset.
_LABEL_CHARSET = re.compile(r"[A-Za-z0-9 ._:\-]+")


class _FieldRefusal(Exception):
    """An internal typed boundary refusal carrying the exact ``field`` and a message, mapped to a
    (422, "validation_error") response by the route. Never escapes the request handler."""

    def __init__(self, message: str, *, field: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.field = field


def _require_label(value: object, field: str) -> str:
    """BP-2: a required label/id string - non-empty, within MAX_LABEL_LEN, conservative charset.
    The refusal never echoes the offending value (only its length)."""
    if not isinstance(value, str) or not value.strip():
        raise _FieldRefusal(f"{field} must be a non-empty string", field=field)
    if len(value) > MAX_LABEL_LEN:
        raise _FieldRefusal(
            f"{field} exceeds MAX_LABEL_LEN ({MAX_LABEL_LEN}); got {len(value)} characters",
            field=field,
        )
    if not _LABEL_CHARSET.fullmatch(value):
        raise _FieldRefusal(
            f"{field} contains characters outside the allowed set "
            "[A-Za-z0-9 ._:-] (the whole value, including any trailing newline, is checked)",
            field=field,
        )
    return value


# --- BP-5: mapped lot_rule_fact value types (the evaluator input vocabulary) ------------------
# A caller fact whose KEY is not in CALLER_RULE_INPUT_NAMES is never fed (the B2 engine records it
# as unmapped). For the mapped keys we validate the VALUE type here, and - for enum/numeric
# constrained inputs - the VALUE DOMAIN against the registry's OWN declared vocabulary (see
# _derive_input_domains; never an invented list/limit), both typed-and-field-named, fail-closed
# BEFORE the engine runs. The evaluator stays fail-closed on anything the boundary does not narrow.
_BOOL_FACTS = frozenset(
    {"overlay_present", "special_district_present", "historic_district", "large_site"}
)
_STR_FACTS = frozenset({"zoning_district", "street_width_class", "site_class"})
_NUM_FACTS = frozenset({"lot_depth_ft"})


def _assert_fact_type_table_covers_vocabulary() -> None:
    """Import-time guard: the BP-5 value-type table partitions the engine's caller-input
    vocabulary exactly, so a new mapped input can never silently skip type validation. See the
    module docstring for the (deliberate) whole-app boot blast radius (DB-039(b))."""
    typed = _BOOL_FACTS | _STR_FACTS | _NUM_FACTS
    if typed != set(CALLER_RULE_INPUT_NAMES):
        raise ValueError(
            "BP-5 lot_rule_fact type table is out of step with CALLER_RULE_INPUT_NAMES "
            f"(typed={sorted(typed)}, vocabulary={sorted(CALLER_RULE_INPUT_NAMES)})"
        )


_assert_fact_type_table_covers_vocabulary()


def _validate_lot_rule_fact_types(facts: dict) -> None:
    """BP-5: type-check the VALUES of the mapped caller facts (the evaluator input vocabulary).
    A caller fact whose key is not mapped is untouched here (the B2 engine surfaces it as
    unmapped and never feeds it). A bad type is a typed refusal naming the exact field; the
    refusal never echoes the offending value."""
    for key, value in facts.items():
        field = f"lot_rule_facts.{key}"
        if key in _BOOL_FACTS:
            if not isinstance(value, bool):
                raise _FieldRefusal(f"{field} must be a boolean", field=field)
        elif key in _STR_FACTS:
            if not isinstance(value, str) or not value.strip():
                raise _FieldRefusal(f"{field} must be a non-empty string", field=field)
        elif key in _NUM_FACTS:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise _FieldRefusal(f"{field} must be a number", field=field)
        # else: unmapped -> not validated, never fed (B2 engine records it as unmapped).


def _validate_lot_rule_fact_keys(facts: dict) -> None:
    """BP-2-discipline bound on EVERY ``lot_rule_facts`` KEY (M5-T057 G3-F3/G5-F1): unmapped keys
    are surfaced verbatim in the 200 body's ``unmapped_lot_facts`` and rendered by B3, so a key
    gets the same length + conservative-charset ceiling as a label (every mapped key already
    conforms). The refusal echoes the key's LENGTH only, never the key."""
    for key in facts:
        if not isinstance(key, str) or not key:
            raise _FieldRefusal(
                "lot_rule_facts keys must be non-empty strings", field="lot_rule_facts"
            )
        if len(key) > MAX_LABEL_LEN:
            raise _FieldRefusal(
                f"a lot_rule_facts key exceeds MAX_LABEL_LEN ({MAX_LABEL_LEN}); "
                f"got {len(key)} characters",
                field="lot_rule_facts",
            )
        if not _LABEL_CHARSET.fullmatch(key):
            raise _FieldRefusal(
                "a lot_rule_facts key contains characters outside the allowed set "
                "[A-Za-z0-9 ._:-]",
                field="lot_rule_facts",
            )


# --- BP-5 (DB-039(d)): registry-derived enum domains + numeric bounds -------------------------
@dataclass(frozen=True)
class _NumericBounds:
    """The effective, registry-DERIVED numeric acceptance window for one caller input. Each field
    that is set carries a value copied from a rule's ``InputSpec`` (never invented). At most one
    lower field (``minimum`` XOR ``exclusive_minimum``) and one upper field are ever set - the
    most-permissive across the declaring rules."""

    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: float | None = None
    exclusive_maximum: float | None = None

    def refusal_reason(self, value: float) -> str | None:
        """The bound the value violates (as a short accepted-range phrase), or ``None`` if the
        value is within the window. Never echoes the value."""
        if self.minimum is not None and value < self.minimum:
            return f">= {self.minimum}"
        if self.exclusive_minimum is not None and value <= self.exclusive_minimum:
            return f"> {self.exclusive_minimum}"
        if self.maximum is not None and value > self.maximum:
            return f"<= {self.maximum}"
        if self.exclusive_maximum is not None and value >= self.exclusive_maximum:
            return f"< {self.exclusive_maximum}"
        return None

    def describe(self) -> str:
        parts: list[str] = []
        if self.minimum is not None:
            parts.append(f">= {self.minimum}")
        if self.exclusive_minimum is not None:
            parts.append(f"> {self.exclusive_minimum}")
        if self.maximum is not None:
            parts.append(f"<= {self.maximum}")
        if self.exclusive_maximum is not None:
            parts.append(f"< {self.exclusive_maximum}")
        return " and ".join(parts)


@dataclass(frozen=True)
class _InputDomains:
    """The registry-derived acceptance vocabulary for the caller-mappable inputs: enum sets for
    string inputs, numeric windows for number inputs. Both derived from the SAME registry object
    and memoized against it (:func:`input_domains_for`)."""

    enums: dict[str, frozenset[str]]
    numeric: dict[str, _NumericBounds]


def _rule_lower(spec: object) -> tuple[float, bool] | None:
    """The rule's own acceptance FLOOR as ``(value, inclusive)``, or ``None`` if the rule leaves
    the input unbounded below. When a rule declares both ``minimum`` and ``exclusive_minimum`` the
    MORE RESTRICTIVE (higher floor; exclusive wins a tie) is that rule's floor."""
    cands: list[tuple[float, bool]] = []
    minimum = getattr(spec, "minimum", None)
    exclusive = getattr(spec, "exclusive_minimum", None)
    if minimum is not None:
        cands.append((float(minimum), True))
    if exclusive is not None:
        cands.append((float(exclusive), False))
    if not cands:
        return None
    # most restrictive floor = highest value; tie -> exclusive (does not accept the endpoint).
    return max(cands, key=lambda c: (c[0], 0 if c[1] else 1))


def _rule_upper(spec: object) -> tuple[float, bool] | None:
    """The rule's own acceptance CEILING as ``(value, inclusive)``, or ``None`` if unbounded
    above. Both bounds declared -> the MORE RESTRICTIVE (lower ceiling; exclusive wins a tie)."""
    cands: list[tuple[float, bool]] = []
    maximum = getattr(spec, "maximum", None)
    exclusive = getattr(spec, "exclusive_maximum", None)
    if maximum is not None:
        cands.append((float(maximum), True))
    if exclusive is not None:
        cands.append((float(exclusive), False))
    if not cands:
        return None
    # most restrictive ceiling = lowest value; tie -> exclusive.
    return min(cands, key=lambda c: (c[0], 0 if not c[1] else 1))


def _combine_lower(
    a: tuple[float, bool] | None, b: tuple[float, bool] | None
) -> tuple[float, bool] | None:
    """Most-permissive lower bound across rules = lowest floor; a tie keeps the inclusive one (it
    accepts the endpoint). A value below the result is below EVERY rule's floor."""
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b, key=lambda c: (c[0], 0 if c[1] else 1))


def _combine_upper(
    a: tuple[float, bool] | None, b: tuple[float, bool] | None
) -> tuple[float, bool] | None:
    """Most-permissive upper bound across rules = highest ceiling; a tie keeps the inclusive one.
    A value above the result is above EVERY rule's ceiling."""
    if a is None:
        return b
    if b is None:
        return a
    return max(a, b, key=lambda c: (c[0], 1 if c[1] else 0))


def derive_input_domains(registry: RuleRegistry) -> _InputDomains:
    """Derive the accepted-value vocabulary of each caller-mappable input from the registry's OWN
    declared input specs (M5-T057 G3-F5 renamed + DB-039(d) extended).

    - ENUM (string inputs): a name is narrowed only when EVERY rule that declares it constrains it
      with an ``enum``; the domain is the UNION of those enums (a value outside the union is
      outside every rule's enum, so refusing it changes nothing the engine would accept).
    - NUMERIC (number inputs): a name is bounded in a DIRECTION only when EVERY declaring rule
      bounds that direction; the kept bound is the MOST PERMISSIVE across rules. A value below the
      derived floor is below every rule's floor (and likewise above the ceiling), so refusing it
      is never a fabricated legal limit - every bound value comes from an ``InputSpec`` field.

    Restricted to the caller-mappable names; a rule-only input is irrelevant at this boundary."""
    enum_declared: dict[str, set[str]] = {}
    enum_free: set[str] = set()
    numeric_state: dict[str, dict] = {}

    for rule_id in registry.rule_ids():
        for spec in registry.rule(rule_id).inputs:
            name = spec.name
            if name not in CALLER_RULE_INPUT_NAMES:
                continue
            # enum side
            if spec.enum:
                enum_declared.setdefault(name, set()).update(spec.enum)
            else:
                enum_free.add(name)
            # numeric side (per-direction every-declaring-rule conservatism)
            st = numeric_state.setdefault(
                name, {"lower_all": True, "upper_all": True, "lower": None, "upper": None}
            )
            lower = _rule_lower(spec)
            if lower is None:
                st["lower_all"] = False
            else:
                st["lower"] = _combine_lower(st["lower"], lower)
            upper = _rule_upper(spec)
            if upper is None:
                st["upper_all"] = False
            else:
                st["upper"] = _combine_upper(st["upper"], upper)

    enums = {
        name: frozenset(values)
        for name, values in enum_declared.items()
        if name not in enum_free
    }

    numeric: dict[str, _NumericBounds] = {}
    for name, st in numeric_state.items():
        minimum = maximum = excl_min = excl_max = None
        if st["lower_all"] and st["lower"] is not None:
            value, inclusive = st["lower"]
            if inclusive:
                minimum = value
            else:
                excl_min = value
        if st["upper_all"] and st["upper"] is not None:
            value, inclusive = st["upper"]
            if inclusive:
                maximum = value
            else:
                excl_max = value
        if any(v is not None for v in (minimum, maximum, excl_min, excl_max)):
            numeric[name] = _NumericBounds(
                minimum=minimum,
                maximum=maximum,
                exclusive_minimum=excl_min,
                exclusive_maximum=excl_max,
            )

    return _InputDomains(enums=enums, numeric=numeric)


#: Per-registry memo of the derived domains (M5-T057 G3-F5 / DB-039(a)). Keyed WEAKLY by the
#: registry object so the derivation runs once per registry (the production registry is a process
#: global; a test-injected registry keys its own entry) and evicts when a registry is GC'd - no
#: id() reuse hazard, no unbounded growth.
_INPUT_DOMAIN_CACHE: weakref.WeakKeyDictionary[RuleRegistry, _InputDomains] = (
    weakref.WeakKeyDictionary()
)


def input_domains_for(registry: RuleRegistry) -> _InputDomains:
    """The derived domains for ``registry``, computed once and memoized against the registry
    object (DB-039(a)). The test-injected registry derives and caches its OWN domains."""
    cached = _INPUT_DOMAIN_CACHE.get(registry)
    if cached is None:
        cached = derive_input_domains(registry)
        _INPUT_DOMAIN_CACHE[registry] = cached
    return cached


def clear_input_domain_cache() -> None:
    """Drop every memoized derivation. Used by tests to assert the once-per-registry property from
    a known-cold state; production never needs to invalidate (rule data is load-once)."""
    _INPUT_DOMAIN_CACHE.clear()


def _validate_lot_rule_fact_domains(facts: dict, registry: RuleRegistry) -> None:
    """BP-5 (domains + bounds): refuse a mapped caller fact whose value is outside the registry's
    declared vocabulary for that input - a string outside its enum domain OR a number outside its
    numeric window - typed and field-named, BEFORE the engine runs. Type validation has already
    run, so mapped string facts are strings and numeric facts are numbers here. The refusal echoes
    the ACCEPTED set/range, never the offending value; free and unmapped inputs are untouched."""
    domains = input_domains_for(registry)
    for key, value in facts.items():
        allowed = domains.enums.get(key)
        if allowed is not None and isinstance(value, str) and value not in allowed:
            raise _FieldRefusal(
                f"lot_rule_facts.{key} is not one of the accepted values {sorted(allowed)}",
                field=f"lot_rule_facts.{key}",
            )
        bounds = domains.numeric.get(key)
        if bounds is not None and not isinstance(value, bool) and isinstance(value, (int, float)):
            reason = bounds.refusal_reason(value)
            if reason is not None:
                raise _FieldRefusal(
                    f"lot_rule_facts.{key} is outside the registry-declared bound "
                    f"({bounds.describe()})",
                    field=f"lot_rule_facts.{key}",
                )
