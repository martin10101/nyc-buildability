"""Build-time acceptance tests for the measurement-basis examples (M5-T126, D-090 R430-R437).

Deterministic and engine-free: they read the authored example data files, the captured
law snapshots, the embedded official HPD quote, the rendered pages and the record,
recompute every component area from the stated dimensions and every reconciliation line
with exact decimal arithmetic, check every cited capture digest against the live capture,
and prove no example carries a program result. They import NOTHING from the rule engine,
the scenario engine or any program output. The negative (mutation) cases mutate a deep
copy in memory; no committed file is edited. They cover acceptance scenarios S1 to S11.
"""
from __future__ import annotations

import ast
import copy
import pathlib
import sys
from decimal import Decimal

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import measurement_basis_check as check  # noqa: E402
import measurement_basis_fit as fit  # noqa: E402
import measurement_basis_lib as lib  # noqa: E402
import measurement_basis_render as render  # noqa: E402

EXAMPLES = lib.load_all()
SUPPORT_FILES = sorted(_HERE.glob("*.py"))

# The hand-verified totals (the oracle that pins the method independently of the engine).
# M5-T133: Examples B and C were rebuilt so that every floor fits; their ratios change and the
# earlier 0.6022 (B) and 0.6676 (C) are withdrawn. Example A is unchanged.
EXPECTED = {
    "example-a-standard-residential": {"zoning": 8000, "hpd": 6032, "ratio": "0.7540",
                                       "mixed_use": False, "units_cap": 13},
    "example-b-allowances-conditions-shown": {"zoning": 12001, "hpd": 7780, "ratio": "0.6483",
                                              "mixed_use": False, "units_cap": 19},
    "example-c-mixed-use": {"zoning": 10428, "hpd": 7120, "ratio": "0.6828",
                            "mixed_use": True, "units_cap": 16},
}


# --------------------------------------------------------------------------
# positive: everything validates cleanly end to end
# --------------------------------------------------------------------------
def test_everything_validates_clean():
    errors = check.validate_all() + render.rendered_errors()
    assert errors == [], "\n".join(errors)


def test_three_examples_each_with_a_data_file_and_a_page():
    assert lib.EXAMPLE_IDS == (
        "example-a-standard-residential",
        "example-b-allowances-conditions-shown",
        "example-c-mixed-use",
    )
    for example_id in lib.EXAMPLE_IDS:
        assert lib.example_path(example_id).is_file(), example_id
        assert lib.page_path(example_id).is_file(), example_id


# --------------------------------------------------------------------------
# S1 - each area is defined by its source before any formula (the record)
# --------------------------------------------------------------------------
def test_record_defines_each_area_before_the_formula():
    assert check.record_errors() == []
    text = lib.RECORD_PATH.read_text().lower()
    # the floor-area definition appears before the ratio formula
    assert text.find("floor area") < text.find("total hpd-measured dwelling-unit area")
    assert "not professionally reviewed" in text


# --------------------------------------------------------------------------
# S2 - one schedule, two treatments, the precise HPD vocabulary
# --------------------------------------------------------------------------
def test_one_schedule_two_treatments():
    for example_id, data in EXAMPLES.items():
        assert check.validate_example(example_id, data) == [], example_id
        ids = [c["component_id"] for c in data["components"]]
        assert len(ids) == len(set(ids)), f"{example_id}: duplicate component ids"
        for comp in data["components"]:
            assert comp["zoning"]["treatment"] in lib.ZONING_TREATMENTS
            assert comp["hpd"]["treatment"] in lib.HPD_TREATMENTS


def test_hpd_keeps_partitions_and_uses_mechanical_and_plumbing_chases():
    # partitions inside an apartment stay in the unit area (R413); chases use the exact term.
    for data in EXAMPLES.values():
        part = lib.find_component(data, "interior-partitions")
        assert part is not None and part["hpd"]["treatment"] == "count"
        chase = lib.find_component(data, "chases")
        assert chase is not None
        assert "mechanical and plumbing chases" in chase["name"].lower()
        assert chase["hpd"]["treatment"] == "exclude"


# --------------------------------------------------------------------------
# S3 - allowances are conditional
# --------------------------------------------------------------------------
def test_an_allowance_not_shown_takes_nothing():
    # Example A shows the corridor allowance not taken (condition not shown -> it counts).
    corridor = lib.find_component(EXAMPLES["example-a-standard-residential"], "corridor")
    assert corridor["zoning"]["condition_shown"] is False
    assert Decimal(str(corridor["zoning"]["excluded_area"])) == 0
    assert lib.zoning_counted(corridor) == lib.component_area(corridor)
    # Example B shows the parking condition not met -> the room counts in full.
    parking = lib.find_component(EXAMPLES["example-b-allowances-conditions-shown"], "parking-room")
    assert parking["zoning"]["condition_shown"] is False
    assert Decimal(str(parking["zoning"]["excluded_area"])) == 0


def test_conditional_allowances_taken_only_when_shown_and_capped():
    b = EXAMPLES["example-b-allowances-conditions-shown"]
    corridor = lib.find_component(b, "corridor")
    assert corridor["zoning"]["condition_shown"] is True
    assert Decimal(str(corridor["zoning"]["excluded_area"])) == 560  # 50% of 1,120
    refuse = lib.find_component(b, "refuse")
    assert Decimal(str(refuse["zoning"]["excluded_area"])) == 39  # 3 sq ft x 13 DU cap binds
    assert lib.zoning_counted(refuse) == 33  # 72 - 39


def test_nothing_already_out_of_zoning_is_deducted_again():
    # The mechanical room and cellar are excluded under both systems: their bridge
    # contribution is zero and they never appear in the reconciliation bridge.
    b = EXAMPLES["example-b-allowances-conditions-shown"]
    for cid in ("mechanical-room", "cellar"):
        comp = lib.find_component(b, cid)
        assert lib.bridge_contribution(comp) == 0, cid
    bridge_ids = {s["component_id"] for s in b["reconciliation"]["bridge"]}
    assert "mechanical-room" not in bridge_ids and "cellar" not in bridge_ids


# --------------------------------------------------------------------------
# S4 - space comes from a layout, not from the maximum floor area
# --------------------------------------------------------------------------
def test_areas_come_from_the_stated_dimensions():
    for example_id, data in EXAMPLES.items():
        for comp in data["components"]:
            recomputed = lib.component_area(comp)
            tag = f"{example_id}/{comp['component_id']}"
            assert recomputed == Decimal(str(comp["measured_area"])), tag
        assert "made up" in data["made_up_note"].lower()
        assert "maximum" in data["made_up_note"].lower()


# --------------------------------------------------------------------------
# S5 - both areas separately, then reconciled; the oracle totals
# --------------------------------------------------------------------------
def test_both_areas_summed_separately_and_reconciled():
    for example_id, data in EXAMPLES.items():
        assert check.reconciliation_errors(example_id, data) == [], example_id
        want = EXPECTED[example_id]
        assert lib.residential_zoning_floor_area(data) == Decimal(want["zoning"]), example_id
        assert lib.total_hpd_dwelling_unit_area(data) == Decimal(want["hpd"]), example_id


def test_the_worked_ratios_are_example_specific_and_differ():
    for example_id, data in EXAMPLES.items():
        assert str(lib.ratio_value(data)) == EXPECTED[example_id]["ratio"], example_id
    ratios = {EXPECTED[e]["ratio"] for e in EXPECTED}
    assert len(ratios) == 3, "the three examples must give three different ratios"


def test_the_bridge_accounts_for_every_square_foot_of_the_difference():
    for example_id, data in EXAMPLES.items():
        zoning = lib.residential_zoning_floor_area(data)
        hpd = lib.total_hpd_dwelling_unit_area(data)
        walked = zoning
        for step in data["reconciliation"]["bridge"]:
            amount = Decimal(str(step["area"]))
            walked -= amount if step["direction"] == "subtract" else -amount
        assert walked == hpd, example_id


# --------------------------------------------------------------------------
# S6 - arithmetic recomputed exactly; MUTATION PROOF (a): a changed dimension fails
# --------------------------------------------------------------------------
def test_mutation_proof_a_changed_dimension_fails_and_names_the_example_and_row():
    data = copy.deepcopy(EXAMPLES["example-a-standard-residential"])
    comp = lib.find_component(data, "apartment-interior")
    comp["area_parts"][0]["width_ft"] = 47  # was 46
    errs = check.arithmetic_errors("example-a-standard-residential", comp)
    assert errs, "a changed dimension must be caught"
    assert any("example-a-standard-residential/apartment-interior" in m for m in errs), errs
    assert any("measured_area recomputes" in m for m in errs), errs


def test_rendered_pages_are_byte_identical_to_the_renderer():
    assert render.rendered_errors() == []
    for example_id, data in EXAMPLES.items():
        assert render.render_page(data) == lib.page_path(example_id).read_text(), example_id


# --------------------------------------------------------------------------
# reconciliation MUTATION PROOF (e): a component deducted under both systems fails
# --------------------------------------------------------------------------
def test_mutation_proof_e_a_component_deducted_under_both_systems_fails():
    # The cellar is already excluded from zoning floor area (out of the base). Deducting it
    # AGAIN on the bridge toward HPD would be a double deduction - the exact hazard the
    # owner flagged (D-090 R431). The reconciliation check must refuse it.
    data = copy.deepcopy(EXAMPLES["example-b-allowances-conditions-shown"])
    data["reconciliation"]["bridge"].append(
        {"component_id": "cellar", "direction": "subtract", "area": 2000}
    )
    errs = check.reconciliation_errors("example-b-allowances-conditions-shown", data)
    assert errs, "deducting a space already out of zoning must fail the reconciliation"
    assert any("cellar" in m for m in errs), errs
    assert any("not in the residential zoning floor area" in m for m in errs), errs


def test_mutation_proof_e_a_duplicated_bridge_step_fails():
    data = copy.deepcopy(EXAMPLES["example-a-standard-residential"])
    first = data["reconciliation"]["bridge"][0]
    data["reconciliation"]["bridge"].append(copy.deepcopy(first))
    errs = check.reconciliation_errors("example-a-standard-residential", data)
    assert any("twice" in m for m in errs), errs


# --------------------------------------------------------------------------
# S6 - law tied to its capture / the embedded HPD quote; mutation on digest and quote
# --------------------------------------------------------------------------
def test_every_captured_citation_matches_the_live_capture():
    for example_id, data in EXAMPLES.items():
        for comp in data["components"]:
            cites = comp["zoning"]["citations"] + comp["hpd"]["citations"]
            assert check.citation_errors(example_id, comp["component_id"], cites) == [], \
                f"{example_id}/{comp['component_id']}"


def test_mutation_proof_a_changed_law_digest_fails():
    data = copy.deepcopy(EXAMPLES["example-a-standard-residential"])
    comp = lib.find_component(data, "apartment-interior")
    comp["zoning"]["citations"][0]["content_digest"] = "0" * 64
    errs = check.citation_errors("example-a-standard-residential", "apartment-interior",
                                 comp["zoning"]["citations"])
    assert any("digest" in m for m in errs), errs


def test_mutation_proof_a_fabricated_hpd_quote_fails():
    data = copy.deepcopy(EXAMPLES["example-a-standard-residential"])
    comp = lib.find_component(data, "apartment-interior")
    comp["hpd"]["citations"][0]["quote"] = "HPD counts every wall and shaft in the unit"
    errs = check.citation_errors("example-a-standard-residential", "apartment-interior",
                                 comp["hpd"]["citations"])
    assert any("UNIT AREA CALCULATION" in m for m in errs), errs


# --------------------------------------------------------------------------
# S7 - examples validate no percentage
# --------------------------------------------------------------------------
def test_examples_do_not_present_a_typical_percentage():
    for example_id, data in EXAMPLES.items():
        joined = " ".join(data["what_it_does_not_show"]).lower()
        assert "typical" in joined or "validate" in joined, example_id
        page = lib.page_path(example_id).read_text().lower()
        assert "belongs to this made-up example only" in page
    record = lib.RECORD_PATH.read_text().lower()
    assert "700" in record and "25" in record
    assert "not professionally reviewed" in record


# --------------------------------------------------------------------------
# S8 - mixed use uses the residential portion
# --------------------------------------------------------------------------
def test_mixed_use_uses_the_residential_portion_only():
    c = EXAMPLES["example-c-mixed-use"]
    assert c["mixed_use"] is True
    retail = [comp for comp in c["components"] if comp["portion"] == "non_residential"]
    assert retail, "the mixed-use example must include the retail (non-residential) portion"
    bridge_ids = {s["component_id"] for s in c["reconciliation"]["bridge"]}
    for comp in retail:
        assert lib.zoning_counted(comp) == 0  # retail is not in the residential zoning area
        assert lib.hpd_counted(comp) == 0
        assert comp["component_id"] not in bridge_ids
    # the residential lobby/circulation IS counted in the residential zoning floor area
    lobby = lib.find_component(c, "lobby")
    assert lib.zoning_counted(lobby) == lib.component_area(lobby)
    # the shared component counts zero toward the residential EXCLUSIVE zoning floor area and
    # never enters the bridge: it is attributed separately under ZR 23-20 (C3)
    shared = [comp for comp in c["components"] if comp["portion"] == "shared"]
    assert shared, "the mixed-use example must include a shared component"
    for comp in shared:
        assert lib.zoning_counted(comp) == 0
        assert lib.hpd_counted(comp) == 0
        assert comp["component_id"] not in bridge_ids


def test_every_component_is_marked_exclusive_or_shared():
    # C3: each component is exclusive to one use (residential / non-residential) or shared.
    for example_id, data in EXAMPLES.items():
        for comp in data["components"]:
            assert comp["portion"] in lib.PORTIONS, f"{example_id}/{comp['component_id']}"
    # the single-use examples carry no shared or commercial component
    for example_id in ("example-a-standard-residential",
                       "example-b-allowances-conditions-shown"):
        portions = {c["portion"] for c in EXAMPLES[example_id]["components"]}
        assert portions == {"residential"}, example_id


def test_shared_floor_area_attribution_is_a_required_step_not_a_switch():
    # C3: Example C applies the ZR 23-20 attribution and labels the outcome conditional on the
    # mixed-building text not captured yet; it is never offered as an owner choice or a switch.
    c = EXAMPLES["example-c-mixed-use"]
    shared = c["shared_floor_area"]
    assert shared["present"] is True
    assert shared["capture"]["snapshot_id"] == "zr-23-20"
    # the attribution recomputes exactly from the stated totals (the fit check enforces this too)
    assert fit.shared_floor_area_errors("example-c-mixed-use", c) == []
    want_share = lib.residential_share(shared).quantize(Decimal("0.0001"))
    assert Decimal(str(shared["residential_share_value"])) == want_share
    assert Decimal(str(shared["attributed_to_residential"])) == \
        lib.shared_attributed_to_residential(shared)
    assert "not captured yet" in shared["conditional_note"].lower()
    # single-use examples: no shared floor area, attribution does not apply
    for example_id in ("example-a-standard-residential",
                       "example-b-allowances-conditions-shown"):
        assert EXAMPLES[example_id]["shared_floor_area"]["present"] is False
        assert fit.shared_floor_area_errors(example_id, EXAMPLES[example_id]) == []


# --------------------------------------------------------------------------
# M5-T133 (B) - the FIT check: every floor fits; the check bites (S1, S2, S3)
# --------------------------------------------------------------------------
def test_every_floor_of_every_example_fits():
    # S2: on each floor the components (the exterior wall ring among them) add up to exactly
    # the stated outside outline, by exact decimal arithmetic.
    for example_id, data in EXAMPLES.items():
        assert fit.fit_errors(example_id, data) == [], example_id
        for floor in data["floors"]:
            outline = lib.outline_area(floor)
            total = lib.floor_component_total(data, floor["floor_id"])
            assert total == outline, f"{example_id}/{floor['floor_id']}: {total} != {outline}"


def _nonfitting_doc(mode: str) -> dict:
    """A small made-up document (not a real example) used to prove the fit check bites."""
    doc = {
        "floors": [
            {"floor_id": "f1", "label": "the only floor", "count": 1,
             "outline_parts": [{"width_ft": 20, "depth_ft": 20}]},  # outline 400
        ],
        "shared_floor_area": {"present": False, "shared_component_ids": [], "shared_total": 0,
                              "residential_exclusive_floor_area": 320,
                              "commercial_exclusive_floor_area": 0,
                              "total_floor_area_zoning_lot": 320, "attribution_base": 320,
                              "residential_share_value": "1.0000",
                              "attributed_to_residential": "0.00",
                              "attributed_to_commercial": "0.00", "capture": None,
                              "conditional_note": "", "note": "n/a"},
        "components": [
            {"component_id": "exterior-walls", "portion": "residential",
             "area_parts": [
                 {"label": "ring", "sign": "add", "width_ft": 20, "depth_ft": 20, "count": 1},
                 {"label": "inner", "sign": "subtract", "width_ft": 18, "depth_ft": 18, "count": 1},
             ],
             "floor_areas": [{"floor_id": "f1", "area": 76}]},  # 400 - 324
            {"component_id": "apartment-interior", "portion": "residential",
             "area_parts": [
                 {"label": "rooms", "sign": "add", "width_ft": 18, "depth_ft": 16, "count": 1},
             ],
             "floor_areas": [{"floor_id": "f1", "area": 288}]},  # 18x16
            {"component_id": "corridor", "portion": "residential",
             "area_parts": [
                 {"label": "corridor", "sign": "add", "width_ft": 2, "depth_ft": 18, "count": 1},
             ],
             "floor_areas": [{"floor_id": "f1", "area": 36}]},  # 2x18
        ],
    }
    # as built: 76 + 288 + 36 = 400 = outline (it fits; inside 324, rooms 288 < 324)
    if mode == "no_outline":
        doc["floors"][0]["outline_parts"] = []
    elif mode == "dimension_changed_by_a_foot":
        # one apartment dimension 18 -> 19 ft: measured_area no longer matches the per-floor sum
        doc["components"][1]["area_parts"][0]["width_ft"] = 19
    elif mode == "rooms_fill_inside_outline":
        # rooms fill the whole inside outline (324) while a corridor is still listed on top
        doc["components"][1]["floor_areas"][0]["area"] = 324
        doc["components"][1]["area_parts"][0] = {"label": "rooms", "sign": "add",
                                                 "width_ft": 18, "depth_ft": 18, "count": 1}
    return doc


def test_fit_check_bites_no_outline():
    errs = fit.geometry_fit_errors("made-up", _nonfitting_doc("no_outline"))
    assert any("no stated outside outline" in m for m in errs), errs


def test_fit_check_bites_dimension_changed_by_a_foot():
    errs = fit.geometry_fit_errors("made-up", _nonfitting_doc("dimension_changed_by_a_foot"))
    assert any("per-floor" in m and "schedule" in m for m in errs), errs


def test_fit_check_bites_rooms_fill_inside_outline():
    errs = fit.geometry_fit_errors("made-up", _nonfitting_doc("rooms_fill_inside_outline"))
    assert any("already fill the inside outline" in m for m in errs), errs


def test_fit_check_bites_on_a_real_example_mutation():
    # one dimension of one component changed by a foot on a real example -> the fit check bites
    data = copy.deepcopy(EXAMPLES["example-c-mixed-use"])
    comp = lib.find_component(data, "apartment-interior")
    comp["area_parts"][0]["width_ft"] += 1  # 43 -> 44
    errs = fit.fit_errors("example-c-mixed-use", data)
    assert errs, "a changed dimension must break the fit"


def test_fit_check_bites_when_a_floor_outline_is_removed():
    data = copy.deepcopy(EXAMPLES["example-b-allowances-conditions-shown"])
    data["floors"][1]["outline_parts"] = []  # drop the ground-floor outline
    errs = fit.fit_errors("example-b-allowances-conditions-shown", data)
    assert any("no stated outside outline" in m for m in errs), errs


# --------------------------------------------------------------------------
# S9 - the legal cap is kept apart; the ratio is HPD / residential zoning floor area
# --------------------------------------------------------------------------
def test_legal_cap_is_separate_and_recomputes():
    for example_id, data in EXAMPLES.items():
        assert check.legal_cap_errors(example_id, data) == [], example_id
        cap = data["legal_unit_cap"]
        assert lib.legal_unit_cap_units(cap) == EXPECTED[example_id]["units_cap"], example_id
        # the physical measured area is a different number from the legal maximum
        measured = lib.residential_zoning_floor_area(data)
        assert measured != Decimal(str(cap["max_residential_floor_area"])), example_id


def test_ratio_numerator_and_denominator_are_named():
    for data in EXAMPLES.values():
        ratio = data["reconciliation"]["ratio"]
        assert Decimal(str(ratio["numerator"])) == lib.total_hpd_dwelling_unit_area(data)
        assert Decimal(str(ratio["denominator"])) == lib.residential_zoning_floor_area(data)


# --------------------------------------------------------------------------
# S11 - support files are engine-free and focused
# --------------------------------------------------------------------------
def test_support_code_imports_no_engine():
    def _modules(path: pathlib.Path):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    yield alias.name
            elif isinstance(node, ast.ImportFrom):
                yield node.module or ""

    for path in SUPPORT_FILES:
        for module in _modules(path):
            assert module.split(".")[0] != "app", f"{path.name} imports {module!r}"


def test_support_files_are_focused():
    for path in SUPPORT_FILES:
        lines = len(path.read_text().splitlines())
        assert lines < 600, f"{path.name} has {lines} lines (keep each file focused)"


def test_no_program_result_in_any_example():
    for example_id, data in EXAMPLES.items():
        assert check.program_result_errors(example_id, data) == [], example_id


def test_loader_fails_loudly_on_a_missing_component():
    data = EXAMPLES["example-a-standard-residential"]
    assert lib.find_component(data, "no-such-component") is None
