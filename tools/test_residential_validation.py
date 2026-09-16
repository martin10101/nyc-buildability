"""Acceptance checks for the independent residential source audit (M4-T022)."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from tools.residential_validation import (
    audit_observation, audit_tables, normalize_bbl, number, verify_source_captures,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/residential_validation'
MATRIX = json.loads((FIXTURES / 'official_far_expectations.json').read_text())
RULES = [json.loads(p.read_text()) for p in sorted(
    (ROOT / 'services/api/app/rules/rulesets').glob('*far.rule.json'))]


def failures(checks):
    return [c for c in checks if c['status'] == 'fail']


class ResidentialAuditTests(unittest.TestCase):
    def test_all_fresh_official_rows_and_both_columns_match(self):
        checks = audit_tables(MATRIX, RULES)
        self.assertEqual([], failures(checks))
        values = [c for c in checks if c['layer'] == 'reference_value']
        self.assertEqual(98, len(values))
        self.assertEqual({'pass'}, {c['status'] for c in values})

    def test_wrong_r6a_reference_is_detected(self):
        changed = copy.deepcopy(RULES)
        rule = next(r for r in changed if r['rule_id'] == 'r6-r12-residential-far')
        next(p for p in rule['parameters'] if p['name'] == 'standard_far_by_district')['value']['R6A'] = 2.61
        self.assertTrue(any('R6A' in c['case'] for c in failures(audit_tables(MATRIX, changed))))

    def test_missing_district_is_not_passed(self):
        changed = copy.deepcopy(RULES)
        changed[0]['applicability']['values'].remove('R1-1')
        self.assertTrue(failures(audit_tables(MATRIX, changed)))

    def test_missing_material_alternative_is_detected(self):
        changed = copy.deepcopy(RULES)
        rule = next(r for r in changed if 'wide-street' in r['rule_id'])
        rule['parameters'] = [p for p in rule['parameters'] if p['name'] != 'wide_street_qualifying_far_by_district']
        self.assertTrue(any('R8' in c['case'] for c in failures(audit_tables(MATRIX, changed))))

    def test_duplicate_district_owner_is_ambiguous(self):
        changed = copy.deepcopy(RULES)
        changed.append(copy.deepcopy(changed[0]))
        self.assertTrue(failures(audit_tables(MATRIX, changed)))

    def test_wrong_source_section_is_detected(self):
        changed = copy.deepcopy(RULES)
        changed[0]['citations'][0]['section'] = '23-22'
        self.assertTrue(failures(audit_tables(MATRIX, changed)))

    def test_mutated_expected_value_is_detected(self):
        changed = copy.deepcopy(MATRIX)
        changed['rows'][0]['standard_far'] = '999'
        self.assertTrue(failures(audit_tables(changed, RULES)))

    def test_source_text_digest_is_checked(self):
        self.assertEqual([], failures(verify_source_captures(ROOT, MATRIX)))
        changed = copy.deepcopy(MATRIX)
        changed['sources'][0]['text_sha256'] = '0' * 64
        self.assertTrue(failures(verify_source_captures(ROOT, changed)))

    def test_source_path_cannot_leave_fixture_directory(self):
        changed = copy.deepcopy(MATRIX)
        changed['sources'][0]['text_path'] = '../outside.txt'
        self.assertTrue(failures(verify_source_captures(ROOT, changed)))

    def test_zero_is_numeric_and_missing_is_unknown(self):
        self.assertEqual(0, number('0.00000000000'))
        self.assertIsNone(number(None))
        for invalid in [True, False, 'NaN', 'Infinity', '3oops', '', {}, []]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    number(invalid)

    def test_bbl_is_exact_and_no_fraction_is_silently_dropped(self):
        self.assertEqual('3052960043', normalize_bbl('3052960043.00000000'))
        for value in ['3052960043.1', 'nan', '30529600430', None, True]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_bbl(value)

    def test_record_and_display_values_are_distinct_from_calculation(self):
        record = {'bbl': '3052960043.00000000', 'builtfar': '2.61', 'residfar': '3'}
        observed = {'bbl': '3052960043', 'built_far': 2.61, 'reference_far': 3,
                    'calculated_far': None, 'calculated_floor_area_sq_ft': None,
                    'calculation_status': 'not_calculated'}
        checks = audit_observation(record, observed)
        self.assertEqual([], failures(checks))
        self.assertEqual(['gap'], [c['status'] for c in checks if c['layer'] == 'application_calculation'])

    def test_wrong_bbl_does_not_pass_equal_numbers(self):
        checks = audit_observation({'bbl': '3052960043', 'residfar': '3'},
                                   {'bbl': '3052960044', 'reference_far': 3})
        self.assertTrue(failures(checks))
        self.assertFalse(any(c['status'] == 'pass' for c in checks))

    def test_built_far_used_as_allowed_far_is_detected(self):
        checks = audit_observation({'bbl': '3052960043', 'builtfar': '2.61', 'residfar': '3'},
                                   {'bbl': '3052960043', 'built_far': 2.61, 'reference_far': 2.61})
        self.assertTrue(any(c['case'] == 'reference_far' for c in failures(checks)))

    def test_unobserved_app_does_not_pass(self):
        checks = audit_observation({'bbl': '3052960043'}, None)
        self.assertEqual({'gap'}, {c['status'] for c in checks})

    def test_missing_reference_is_not_replaced_with_zero(self):
        checks = audit_observation({'bbl': '3052960043', 'builtfar': '0'},
                                   {'bbl': '3052960043', 'built_far': 0, 'reference_far': 0})
        self.assertTrue(any(c['case'] == 'reference_far' and c['status'] == 'gap' for c in checks))
        self.assertTrue(any(c['case'] == 'built_far' and c['status'] == 'pass' for c in checks))

    def test_observed_calculation_is_not_legal_validation_without_expected_case(self):
        checks = audit_observation({'bbl': '3052960043', 'residfar': '3'},
                                   {'bbl': '3052960043', 'reference_far': 3,
                                    'calculated_far': 3, 'calculated_floor_area_sq_ft': 7200,
                                    'calculation_status': 'calculated'})
        self.assertEqual(['gap'], [c['status'] for c in checks if c['layer'] == 'application_calculation'])


class AuditDriftReworkTests(unittest.TestCase):
    def test_input_and_output_unit_mutations_fail(self):
        fields = [('inputs', 'lot_area_sq_ft', 'square_meters'),
                  ('outputs', 'max_residential_far', 'square_feet'),
                  ('outputs', 'max_residential_floor_area_sq_ft', 'far')]
        for group, name, wrong in fields:
            for mutation in [wrong, None]:
                with self.subTest(field=name, unit=mutation):
                    changed = copy.deepcopy(RULES)
                    target = next(x for x in changed[0][group] if x['name'] == name)
                    if mutation is None:
                        target.pop('unit')
                    else:
                        target['unit'] = mutation
                    self.assertTrue(failures(audit_tables(MATRIX, changed)))
        changed = copy.deepcopy(RULES)
        a, b = changed[0]['outputs']
        a['unit'], b['unit'] = b['unit'], a['unit']
        with self.subTest(swap='output units'):
            self.assertTrue(failures(audit_tables(MATRIX, changed)))
        changed = copy.deepcopy(RULES)
        area = next(d for d in changed[0]['inputs'] if d['name'] == 'lot_area_sq_ft')
        far = next(d for d in changed[0]['outputs'] if d['name'] == 'max_residential_far')
        area['unit'], far['unit'] = far['unit'], area['unit']
        with self.subTest(swap='input/output units'):
            self.assertTrue(failures(audit_tables(MATRIX, changed)))

    def test_parameter_citation_mutations_fail(self):
        for mutation in ['wrong-source', 'zr-23-22', None]:
            with self.subTest(citation=mutation):
                changed = copy.deepcopy(RULES)
                if mutation is None:
                    changed[0]['parameters'][0].pop('citation_ref')
                else:
                    changed[0]['parameters'][0]['citation_ref'] = mutation
                self.assertTrue(failures(audit_tables(MATRIX, changed)))
        changed = copy.deepcopy(RULES)
        changed[0]['citations'] = []
        self.assertTrue(failures(audit_tables(MATRIX, changed)))

    def test_source_authority_and_section_url_mutations_fail(self):
        for url in ['https://example.invalid/not-official',
                    'https://zr.planning.nyc.gov/article-ii/chapter-3/23-22',
                    'http://zr.planning.nyc.gov/article-ii/chapter-3/23-21']:
            with self.subTest(url=url):
                changed = copy.deepcopy(MATRIX)
                changed['sources'][0]['url'] = url
                self.assertTrue(failures(verify_source_captures(ROOT, changed)))

    def test_condition_numbers_are_bound_to_operative_source(self):
        for footnote, field, wrong in [
            ('23-21-footnote-1', 'minimum_lot_area_sq_ft', '4001'),
            ('23-21-footnote-1', 'single_dwelling_unit_equivalent_far_limit', '0.61'),
            ('23-22-footnote-1', 'distance_ft', '101'),
            ('23-22-footnote-2', 'distance_ft', '99'),
        ]:
            with self.subTest(footnote=footnote, field=field):
                changed = copy.deepcopy(MATRIX)
                changed['conditions'][footnote][field] = wrong
                self.assertTrue(failures(audit_tables(changed, RULES)))

    def test_footnote_district_assignment_is_bound_to_source(self):
        changed = copy.deepcopy(MATRIX)
        next(r for r in changed['rows'] if r['district'] == 'R6A')['notes'] = ['23-22-footnote-1']
        with self.subTest(assignment='wrong district'):
            self.assertTrue(failures(audit_tables(changed, RULES)))
        changed = copy.deepcopy(MATRIX)
        next(r for r in changed['rows'] if r['condition'] == 'within_100ft_wide_street')['notes'] = []
        with self.subTest(assignment='missing note'):
            self.assertTrue(failures(audit_tables(changed, RULES)))

    def test_removed_r8_compound_conditions_fail(self):
        changed = copy.deepcopy(MATRIX)
        changed['conditions']['23-22-footnote-2']['scope'] = 'Within 100 feet of a wide street.'
        with self.subTest(compound='removed clauses'):
            self.assertTrue(failures(audit_tables(changed, RULES)))
        changed = copy.deepcopy(MATRIX)
        changed['conditions'].pop('23-22-footnote-2')
        with self.subTest(compound='missing footnote'):
            self.assertTrue(failures(audit_tables(changed, RULES)))


    def test_rule_limitation_numeric_drift_fails(self):
        for rule_fragment, exception_id, before, after in [
            ('r1-r2-r3', 'single_dwelling_unit_equivalent_far_cap', '4,000', '4,001'),
            ('r1-r2-r3', 'single_dwelling_unit_equivalent_far_cap', '0.60', '0.61'),
            ('wide-street', 'wide_street_far_alternative', '100 feet', '101 feet'),
        ]:
            with self.subTest(exception=exception_id, change=after):
                changed = copy.deepcopy(RULES)
                rule = next(r for r in changed if rule_fragment in r['rule_id'])
                note = next(e for e in rule['exceptions'] if e['id'] == exception_id)
                note['description'] = note['description'].replace(before, after)
                self.assertTrue(failures(audit_tables(MATRIX, changed)))

    def test_rule_compound_r8_limitation_cannot_lose_a_condition(self):
        for text in ['outside a Mandatory Inclusionary Housing area AND ',
                     'within 100 feet of a wide street AND ',
                     'containing UAP developments or qualifying senior housing']:
            with self.subTest(removed=text):
                changed = copy.deepcopy(RULES)
                rule = next(r for r in changed if 'wide-street' in r['rule_id'])
                note = next(e for e in rule['exceptions']
                            if e['id'] == 'r8_wide_street_qualifying_footnote_2')
                note['description'] = note['description'].replace(text, '')
                self.assertTrue(failures(audit_tables(MATRIX, changed)))

    def test_rule_footnote_cannot_be_assigned_to_wrong_district(self):
        changed = copy.deepcopy(RULES)
        rule = next(r for r in changed if 'wide-street' in r['rule_id'])
        note = next(e for e in rule['exceptions']
                    if e['id'] == 'r8_wide_street_qualifying_footnote_2')
        note['condition']['value'] = 'R6'
        self.assertTrue(failures(audit_tables(MATRIX, changed)))


if __name__ == '__main__':
    unittest.main()
