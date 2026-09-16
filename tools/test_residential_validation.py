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


if __name__ == '__main__':
    unittest.main()
