#!/usr/bin/env python3
"""Step-P6 reference-case constants and guards (M4-T037).

Pure stdlib (no import from the rule engine, the scenario engine or any program
output). It holds the data and the extra rules the step-P6 case needs, so the
checker next to it does not grow past its focus. The step-P6 case is one
independent hand-worked example of a first building option: whether a building may
be lower than the minimum base height, a footprint and floors worked by hand for a
made-up lot and the recorded corner lot, what a floor schedule must list, and the
preliminary apartment estimate kept apart from the legal dwelling-unit ceiling.

* ``STEP_P6_READINGS`` - the two step-P6 readings, each saved unchanged below a
  short header, with the digest that pins the whole saved file (the checker's
  :func:`_reading_digest_errors` consumes it, as for the earlier pairs).
* ``STEP_P6_READING_STEMS`` - the two reading stems a step-P6 row's source
  reference must name, so a value rests on both readings.
* :func:`must_stay_not_known_errors` - the rows the two readings do not jointly
  settle (the made-up lot's street-wall place, the real lot's coverage by portion
  and the rear yard beyond the corner) must carry no value.
* :func:`block_and_word_errors` - a building row's and an estimate row's figures,
  carried as numbers in ``numbers_block``, recompute from the block's own inputs
  (the six steps); every figure is marked a legal requirement or a chosen design
  assumption; and each building and estimate row says, in plain words, what the
  example is and is not (the method of the example; the owner's starting
  assumptions labelled 'preliminary assumption'; the estimate figures never called
  a count, a limit, validated or realistic).

The checker imports this module and wires these in; nothing here imports the
checker, so there is no cycle.
"""
from __future__ import annotations

from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

STEP_P6_CASE_ID = "step-p6-worked"

# The two step-P6 readings a step-P6 row must name (a value needs both to agree).
STEP_P6_READING_STEMS = (
    "return-independent-hand-calculation-13",
    "return-independent-hand-calculation-14",
)

# The two step-P6 readings (task M4-T037), each saved unchanged below a short
# header. The digest pins the whole saved file so any later edit is caught.
STEP_P6_READINGS = {
    "return-independent-hand-calculation-13.md": {
        "marker": "ONE HARD RULE",
        "digest": "b1cf6454749eb1966dac78ed56e49c182b174ae2d36db429f8de157dee5cbbd7",
    },
    "return-independent-hand-calculation-14.md": {
        "marker": "one hard rule",
        "digest": "e30eb39ed3acc9528b93cc7a15a95436fc505738af1f91652d7a1f460cb1240c",
    },
}

# Rows the two step-P6 readings do not jointly settle to a single value (both read
# "not known", or the two readings differ on the measured figure): they must carry
# no value. The made-up lot's street-wall place (the 35-ft neighbours do not count
# and the prevailing frontage is unknown); the real lot's whole-lot coverage (read
# per portion, the two readers' measured areas differ); the rear yard beyond the
# corner (the adjoining lot-line types are missing).
MUST_STAY_NOT_KNOWN = {
    STEP_P6_CASE_ID: {
        "made-up-street-wall",
        "real-lot-coverage-by-portion",
        "real-lot-rear-yard-variants",
    },
}


def must_stay_not_known_errors(case_id: str, data: dict) -> list[str]:
    """A step-P6 row the two readings do not jointly settle (or where they differ on
    the measured figure) must be "not known"; giving it a value is refused (a value
    needs both readings to agree on the same basis)."""
    rows = MUST_STAY_NOT_KNOWN.get(case_id, set())
    errs: list[str] = []
    for row in data.get("rows", []):
        if row.get("row_id") in rows:
            kind = row.get("expected", {}).get("kind")
            if kind != "not_known":
                errs.append(
                    f"{case_id}/{row.get('row_id')}: the two step-P6 readings do not jointly "
                    f"settle this (or they differ on the measured figure), so it must be 'not "
                    f"known', not {kind!r}"
                )
    return errs


# --------------------------------------------------------------------------
# the numbers block (the six steps as numbers): recompute, marks, words
# --------------------------------------------------------------------------
_VALID_MARKS = ("legal_requirement", "design_assumption")
# Roles that are a chosen design assumption (must be marked design_assumption).
_ASSUMPTION_ROLES = (
    "floor_to_floor", "same_plan_stack", "apartment_size", "share_range",
    "floor_area_held", "plan_placement", "derived",
)
# Roles that are a legal requirement (must be marked legal_requirement).
_LEGAL_ROLES = ("maximum_floor_area", "footprint_bound", "height_limit", "unit_factor")
# A building row says, in plain words, what the example is and is not (point 5).
_BUILDING_WORDS = (
    "method of the example", "not a rule of law", "not a recommendation", "maximum base height",
)
# An estimate row says it is arithmetic on the owner's assumptions and carries the
# 'preliminary assumption' label; it never calls its figures a count, a limit,
# validated or realistic (point 5(c)/(e), point 14).
_ESTIMATE_REQUIRED = ("arithmetic", "preliminary assumption")
_ESTIMATE_FORBIDDEN = (
    "validated", "realistic", "is a count", "are a count", "is a limit", "the legal limit on",
)
PRELIM = "preliminary assumption"


def _D(value) -> Decimal:
    return Decimal(str(value))


def _r2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _is_differ(value) -> bool:
    return isinstance(value, dict) and set(value) == {"reading1", "reading2"}


def _pick(value, reading: str):
    """Return the figure for one reading. A plain value is shared by both; a
    differ value {reading1, reading2} returns its named side (the 'single' key
    reads reading1, which equals the shared value when nothing differs)."""
    if _is_differ(value):
        return value["reading2"] if reading == "reading2" else value["reading1"]
    return value


def _reading_keys(block: dict) -> list[str]:
    """['single'] when the block holds one agreed figure throughout; otherwise
    ['reading1', 'reading2'] so a figure that differs is recomputed for each."""
    fields = [block.get("footprint_area_sqft"), block.get("total_floor_area_sqft"),
              block.get("unused_floor_area_sqft"), block.get("floor_area_sqft")]
    for storey in block.get("storeys", []):
        fields += [storey.get("plan_area_sqft"), storey.get("floor_area_sqft"),
                   storey.get("running_total_sqft")]
    return ["reading1", "reading2"] if any(_is_differ(f) for f in fields) else ["single"]


def _marks_errors(tag: str, block: dict) -> list[str]:
    errs: list[str] = []
    marks = block.get("marks")
    if not isinstance(marks, list) or not marks:
        return [f"{tag}: the numbers block needs a non-empty 'marks' list (every figure marked)"]
    for mark in marks:
        if set(mark) != {"figure", "role", "mark", "basis"}:
            errs.append(f"{tag}: a marks entry's keys differ from the fixed set")
            continue
        role, kind = mark["role"], mark["mark"]
        if kind not in _VALID_MARKS:
            errs.append(f"{tag}: figure {mark['figure']!r} is marked neither a legal requirement "
                        f"nor a chosen design assumption (got {kind!r})")
            continue
        if role in _ASSUMPTION_ROLES and kind != "design_assumption":
            errs.append(f"{tag}: figure {mark['figure']!r} is a chosen design assumption called a "
                        "legal requirement")
        elif role in _LEGAL_ROLES and kind != "legal_requirement":
            errs.append(f"{tag}: figure {mark['figure']!r} is a legal requirement mis-marked "
                        f"{kind!r}")
        elif role not in _ASSUMPTION_ROLES and role not in _LEGAL_ROLES:
            errs.append(f"{tag}: figure {mark['figure']!r} has an unknown role {role!r}")
        if role in ("apartment_size", "share_range") and PRELIM not in str(mark["basis"]).lower():
            errs.append(f"{tag}: figure {mark['figure']!r} (the apartment size or share range) "
                        f"must carry the words '{PRELIM}'")
    return errs


def _building_block_errors(tag: str, block: dict) -> list[str]:
    errs: list[str] = []
    try:
        storeys = block["storeys"]
        f2f = _D(block["floor_to_floor_ft"])
        max_fa = _D(block["maximum_floor_area_sqft"])
        fill = block["fill_rule"]
        mbh = _D(block["min_base_height_ft"])
        height = _D(block["height_ft"])
    except (KeyError, Exception) as exc:  # noqa: BLE001
        return [f"{tag}: building block is malformed: {exc}"]
    count = len(storeys)
    if block.get("storey_count") != count:
        errs.append(f"{tag}: storey_count {block.get('storey_count')} != number of storeys {count}")
    if height != f2f * count:
        errs.append(f"{tag}: height {height} != floor-to-floor {f2f} x {count} storeys")
    for reading in _reading_keys(block):
        cum = Decimal(0)
        for i, storey in enumerate(storeys, start=1):
            top = _D(_pick(storey["top_ft"], reading))
            if top != f2f * i:
                errs.append(f"{tag} [{reading}]: storey {i} top {top} != {f2f} x {i}")
            plan = _D(_pick(storey["plan_area_sqft"], reading))
            floor = _D(_pick(storey["floor_area_sqft"], reading))
            if floor != plan:
                errs.append(f"{tag} [{reading}]: storey {i} floor area {floor} != plan area {plan}")
            cum += floor
            run = _D(_pick(storey["running_total_sqft"], reading))
            want_run = cum if fill == "widest" else _r2(max_fa * i / count)
            if run != want_run:
                errs.append(f"{tag} [{reading}]: storey {i} running total {run} != {want_run}")
        total = _D(_pick(block["total_floor_area_sqft"], reading))
        unused = _D(_pick(block["unused_floor_area_sqft"], reading))
        if fill == "widest":
            fp = _D(_pick(block["footprint_area_sqft"], reading))
            if any(_D(_pick(s["plan_area_sqft"], reading)) != fp for s in storeys):
                errs.append(f"{tag} [{reading}]: a storey plan area != the footprint {fp}")
            if total != cum:
                errs.append(f"{tag} [{reading}]: total floor area {total} != the stacked sum {cum}")
            if not (count * fp <= max_fa and (count + 1) * fp > max_fa):
                errs.append(f"{tag} [{reading}]: storey count {count} is wrong for the widest "
                            f"stack (footprint {fp}, maximum {max_fa})")
        else:  # to the minimum base height
            plan = _r2(max_fa / count)
            if any(_D(_pick(s["plan_area_sqft"], reading)) != plan for s in storeys):
                errs.append(f"{tag} [{reading}]: a storey plan area != maximum/{count} = {plan}")
            if total != max_fa:
                errs.append(f"{tag} [{reading}]: total floor area {total} != maximum {max_fa}")
            if not (count * f2f >= mbh and (count - 1) * f2f < mbh):
                errs.append(f"{tag} [{reading}]: storey count {count} is not the fewest reaching "
                            f"the minimum base height {mbh}")
        if unused != max_fa - total:
            errs.append(f"{tag} [{reading}]: unused floor area {unused} != {max_fa} - {total}")
    return errs


def _estimate_block_errors(tag: str, block: dict) -> list[str]:
    errs: list[str] = []
    try:
        low = _D(block["share_low"])
        high = _D(block["share_high"])
        apt = _D(block["apartment_size_sqft"])
    except (KeyError, Exception) as exc:  # noqa: BLE001
        return [f"{tag}: estimate block is malformed: {exc}"]
    for reading in _reading_keys(block):
        fa = _D(_pick(block["floor_area_sqft"], reading))
        for share, qkey, wbkey, wakey in (
            (low, "quotient_low", "whole_below_low", "whole_above_low"),
            (high, "quotient_high", "whole_below_high", "whole_above_high"),
        ):
            exact = fa * share / apt
            if _r2(exact) != _D(block[qkey]):
                errs.append(f"{tag} [{reading}]: {qkey} {block[qkey]} != {_r2(exact)} "
                            f"({fa} x {share} / {apt})")
            below = int(exact.to_integral_value(rounding=ROUND_DOWN))
            if block[wbkey] != below:
                errs.append(f"{tag} [{reading}]: {wbkey} {block[wbkey]} != {below}")
            if block[wakey] != below + 1:
                errs.append(f"{tag} [{reading}]: {wakey} {block[wakey]} != {below + 1}")
    return errs


def block_and_word_errors(case_id: str, data: dict) -> list[str]:
    """Recompute every building and estimate block from its own inputs, check every
    figure is marked a legal requirement or a chosen design assumption, and check
    each building and estimate row says in plain words what the example is and is
    not. Only the step-P6 case carries these blocks."""
    if case_id != STEP_P6_CASE_ID:
        return []
    errs: list[str] = []
    for row in data.get("rows", []):
        block = row.get("numbers_block")
        rid = row.get("row_id", "?")
        tag = f"{case_id}/{rid}"
        dne = str(row.get("does_not_establish", "")).lower()
        value = str(row.get("expected", {}).get("value", "")).lower()
        if block is None:
            continue
        kind = block.get("block_kind")
        errs += _marks_errors(tag, block)
        if kind == "building":
            errs += _building_block_errors(tag, block)
            for word in _BUILDING_WORDS:
                if word not in dne:
                    errs.append(f"{tag}: a building row must say what the example is and is not; "
                                f"it is missing the words {word!r}")
        elif kind == "estimate":
            errs += _estimate_block_errors(tag, block)
            text = value + " " + dne
            for word in _ESTIMATE_REQUIRED:
                if word not in text:
                    errs.append(f"{tag}: an estimate row must carry the words {word!r}")
            for bad in _ESTIMATE_FORBIDDEN:
                if bad in text:
                    errs.append(f"{tag}: an estimate row must not call its figures {bad!r}")
        else:
            errs.append(f"{tag}: a numbers block has an unknown block_kind {kind!r}")
    return errs
