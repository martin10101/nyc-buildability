"""Read-only source audit for residential FAR; never a production calculator.

The offline default uses stdlib only. --engine additionally executes the existing
packaged rule engine using the repository's locked runtime. Every result states
its evidence layer; a matching reference is never a buildability determination.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path('tests/fixtures/residential_validation')
FIELDS = {'built_far': 'builtfar', 'reference_far': 'residfar'}


def number(value):
    """Strict finite decimal, retaining missing separately from explicit zero."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError('not a decimal number')
    text = str(value)
    if len(text) > 40 or not re.fullmatch(r'-?\d+(?:\.\d+)?', text):
        raise ValueError('not a plain finite decimal')
    try:
        parsed = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError('not a decimal number') from exc
    if not parsed.is_finite():
        raise ValueError('not finite')
    return parsed


def normalize_bbl(value):
    parsed = number(value)
    if parsed is None or parsed != parsed.to_integral_value():
        raise ValueError('BBL must be an exact integer')
    result = str(int(parsed))
    if not re.fullmatch('[1-5][0-9]{9}', result):
        raise ValueError('BBL must contain borough and ten digits')
    return result


def check(layer, case, status, expected=None, observed=None, reason=None):
    result = {'layer': layer, 'case': case, 'status': status,
              'expected': expected, 'observed': observed}
    if reason:
        result['reason'] = reason
    return result


def compare_number(layer, case, expected, observed):
    try:
        left, right = number(expected), number(observed)
    except ValueError as exc:
        return check(layer, case, 'fail', expected, observed, str(exc))
    if left is None or right is None:
        return check(layer, case, 'gap', expected, observed, 'Missing is not zero.')
    if left < 0 or right < 0:
        return check(layer, case, 'fail', expected, observed, 'Negative FAR/area.')
    return check(layer, case, 'pass' if left == right else 'fail', expected, observed)


SOURCE_URLS = {
    '23-21': 'https://zr.planning.nyc.gov/article-ii/chapter-3/23-21',
    '23-22': 'https://zr.planning.nyc.gov/article-ii/chapter-3/23-22',
    '12-10': 'https://zr.planning.nyc.gov/article-i/chapter-2/12-10',
}


def normalized(text):
    return re.sub(r'\s+([,.])', r'\1', ' '.join(text.split()))


def load_source_captures(root, matrix):
    results, texts = [], {}
    permitted = (root / FIXTURES).resolve()
    ids = [source.get('id') for source in matrix['sources']]
    results.append(check('source_identity', 'source_set',
                         'pass' if sorted(ids) == sorted(SOURCE_URLS) else 'fail',
                         sorted(SOURCE_URLS), ids))
    for source in matrix['sources']:
        section = source.get('id')
        results.append(check('source_authority', str(section),
                             'pass' if section in SOURCE_URLS
                             and source.get('url') == SOURCE_URLS[section] else 'fail',
                             SOURCE_URLS.get(section), source.get('url')))
        path = (root / source['text_path']).resolve()
        if not path.is_relative_to(permitted) or not path.is_file():
            results.append(check('source_capture', str(section), 'fail',
                                 reason='Missing or out-of-scope source capture.'))
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        results.append(check('source_capture', str(section),
                             'pass' if actual == source['text_sha256'] else 'fail',
                             source['text_sha256'], actual))
        texts[section] = path.read_text()
    return results, texts


def verify_source_captures(root, matrix):
    return load_source_captures(root, matrix)[0]


def parse_table_capture(section, text):
    """Extract retained operative table tokens, including attached superscripts."""
    body = text.rsplit('Copy Link\n', 1)[1].split('Footer Links', 1)[0]
    if body.splitlines()[0] != SOURCE_URLS[section]:
        raise ValueError('Operative source section URL mismatch')
    content = body.split('\nDistrict\n', 1)[1]
    table, tail = re.split(r'\n1\n(?=For)', content, maxsplit=1)
    footnotes = dict(re.findall(r'(?:^|\n)([12])\n(.*?)(?=\n[12]\n|$)',
                               '1\n' + tail, re.S))
    footnotes = {key: normalized(value) for key, value in footnotes.items()}
    tokens = re.findall(r'R\d+(?:-\d+[A-Z]?|[A-Z])?|\d+\.\d+|(?<![\w.-])[12](?![\w.-])', table)
    rows, index = [], 0
    while index < len(tokens):
        districts, district_notes = [], {}
        while index < len(tokens) and tokens[index].startswith('R'):
            district = tokens[index]; districts.append(district); index += 1
            if index < len(tokens) and tokens[index] in ('1', '2'):
                district_notes[district] = [tokens[index]]; index += 1
        if not districts:
            raise ValueError('Unrecognized table row')
        values, value_notes = [], []
        for _ in range(2):
            value = tokens[index]; index += 1
            if not re.fullmatch(r'\d+\.\d+', value):
                raise ValueError('Unrecognized source FAR value')
            values.append(value); marks = []
            if index < len(tokens) and tokens[index] in ('1', '2'):
                marks.append(tokens[index]); index += 1
            value_notes.append(marks)
        for district in districts:
            marks = sorted(set(district_notes.get(district, []) + sum(value_notes, [])))
            condition = 'base'
            if section == '23-22' and '1' in marks:
                condition = ('wide_street_additional_conditions' if '2' in marks
                             else 'within_100ft_wide_street')
            rows.append({'district': district, 'condition': condition,
                         'standard_far': values[0], 'qualifying_far': values[1],
                         'source_section': section,
                         'notes': [f'{section}-footnote-{mark}' for mark in marks]})
    return rows, footnotes


def derive_source_reference(texts):
    """Read values/conditions from source text, not editable expectation metadata."""
    rows, notes = [], {}
    for section in ('23-21', '23-22'):
        parsed, footnotes = parse_table_capture(section, texts[section])
        rows.extend(parsed)
        notes.update({f'{section}-footnote-{key}': value for key, value in footnotes.items()})
    low = notes['23-21-footnote-1']
    area = re.search(r'lot area of ([\d,]+) (square feet) or more', low)
    ratio = re.search(r'equivalent floor area ratio of (\d+\.\d+)', low)
    definition = normalized(texts['12-10'])
    if not area or not ratio or ('total floor area on a zoning lot, divided by the lot area'
                                not in definition):
        raise ValueError('Operative threshold/unit/ratio definition is missing')
    conditions = {'23-21-footnote-1': {
        'minimum_lot_area_sq_ft': area[1].replace(',', ''),
        'single_dwelling_unit_equivalent_far_limit': ratio[1], 'scope': low}}
    for key in ('23-22-footnote-1', '23-22-footnote-2'):
        distance = re.search(r'within (\d+) feet of a wide street', notes[key])
        if not distance:
            raise ValueError('Operative wide-street distance is missing')
        conditions[key] = {'distance_ft': distance[1], 'scope': notes[key]}
    area_unit = {'square feet': 'square_feet'}[area[2]]
    return {'rows': rows, 'conditions': conditions,
            'units': {'lot_area_sq_ft': area_unit, 'max_residential_far': 'far',
                      'max_residential_floor_area_sq_ft': area_unit}}


def audit_reference_metadata(matrix, source):
    results = []
    for key in sorted(set(matrix['conditions']) | set(source['conditions'])):
        expected, actual = source['conditions'].get(key), matrix['conditions'].get(key)
        results.append(check('source_condition', key,
                             'pass' if expected == actual else 'fail', expected, actual))
    expected = {(r['district'], r['condition']): r for r in source['rows']}
    actual = {(r['district'], r['condition']): r for r in matrix['rows']}
    for key in sorted(set(expected) | set(actual)):
        results.append(check('source_row_binding', ':'.join(key),
                             'pass' if expected.get(key) == actual.get(key) else 'fail',
                             expected.get(key), actual.get(key)))
    return results


def audit_rule_contract(rule, source):
    results = []
    for name, unit in source['units'].items():
        declarations = rule['inputs'] if name == 'lot_area_sq_ft' else rule['outputs']
        actual = [d.get('unit') for d in declarations if d.get('name') == name]
        results.append(check('rule_unit', rule['rule_id'] + ':' + name,
                             'pass' if actual == [unit] else 'fail', [unit], actual))
    sections = {r['source_section'] for r in source['rows']
                if r['district'] in rule['applicability']['values']}
    expected = {'zr-' + section for section in sections}
    for param in rule['parameters']:
        ref = param.get('citation_ref')
        cited = [c.get('section') for c in rule['citations'] if c.get('snapshot_id') == ref]
        valid = len(expected) == 1 and ref in expected and cited == list(sections)
        results.append(check('parameter_provenance', rule['rule_id'] + ':' + param['name'],
                             'pass' if valid else 'fail', sorted(expected), ref))
    return results


def audit_rule_limitations(rule, source):
    results = []
    rows = [r for r in source['rows'] if r['district'] in rule['applicability']['values']]
    notes = {n for row in rows for n in row['notes']}
    definitions = [
        ('23-21-footnote-1', 'single_dwelling_unit_equivalent_far_cap'),
        ('23-22-footnote-1', 'wide_street_far_alternative'),
        ('23-22-footnote-2', 'r8_wide_street_qualifying_footnote_2'),
    ]
    for footnote, exception_id in definitions:
        needed = footnote in notes
        found = [e for e in rule['exceptions'] if e['id'] == exception_id]
        valid = len(found) == int(needed)
        if needed and len(found) == 1:
            note, condition = found[0], source['conditions'][footnote]
            text = normalized(note['description']).lower()
            if footnote == '23-21-footnote-1':
                area = re.search(r'lot area of ([\d,]+) square feet or more', text)
                ratio = re.search(r'equivalent floor area ratio of (\d+\.\d+)', text)
                valid = bool(area and ratio and area[1].replace(',', '') ==
                             condition['minimum_lot_area_sq_ft'] and ratio[1] ==
                             condition['single_dwelling_unit_equivalent_far_limit'])
                valid = valid and note.get('condition') is None
            else:
                distance = re.search(r'within (\d+) feet of a wide street', text)
                valid = bool(distance and distance[1] == condition['distance_ft'])
                if footnote == '23-22-footnote-1':
                    valid = valid and note.get('condition') is None
                else:
                    districts = {r['district'] for r in rows if footnote in r['notes']}
                    valid = valid and len(districts) == 1 and note.get('condition') == {
                        'op': 'equals', 'input': 'zoning_district', 'value': next(iter(districts))}
                    compound = (r'outside a mandatory inclusionary housing area and '
                                r'within \d+ feet of a wide street and '
                                r'containing uap developments or qualifying senior housing')
                    valid = valid and bool(re.search(compound, text))
            expected_effect = ('conditional_alternative' if footnote == '23-22-footnote-1'
                               else 'documented_limitation')
            valid = valid and note.get('effect') == expected_effect
        results.append(check('rule_condition_binding', rule['rule_id'] + ':' + footnote,
                             'pass' if valid else 'fail', 'source-bound limitation/absence',
                             found))
    return results


def audit_tables(matrix, rules, root=ROOT):
    """Compare both columns, all rows, district ownership and source sections."""
    results, texts = load_source_captures(root, matrix)
    try:
        source = derive_source_reference(texts)
    except (KeyError, ValueError, IndexError) as exc:
        return results + [check('source_derivation', 'operative_text', 'fail', reason=str(exc))]
    results.extend(audit_reference_metadata(matrix, source))
    owners, expected_keys = {}, set()
    for rule in rules:
        results.extend(audit_rule_contract(rule, source))
        results.extend(audit_rule_limitations(rule, source))
        params = {p['name']: p['value'] for p in rule['parameters']}
        districts = rule['applicability']['values']
        for name in ['standard_far_by_district', 'qualifying_far_by_district']:
            actual = params.get(name, {})
            results.append(check('reference_structure', f"{rule['rule_id']}:{name}",
                                 'pass' if set(actual) == set(districts) else 'fail',
                                 sorted(districts), sorted(actual)))
        for district in districts:
            owners.setdefault(district, []).append((rule, params))
    for row in matrix['rows']:
        district, condition = row['district'], row['condition']
        key = (district, condition)
        if key in expected_keys:
            results.append(check('reference_structure', str(key), 'fail',
                                 reason='Duplicate independent expectation.'))
            continue
        expected_keys.add(key)
        matches = owners.get(district, [])
        if len(matches) != 1:
            results.append(check('reference_structure', district, 'fail', 1, len(matches),
                                 'A source district needs exactly one rule owner.'))
            continue
        rule, params = matches[0]
        cited = {c.get('section') for c in rule['citations']}
        results.append(check('reference_provenance', f'{district}:{condition}',
                             'pass' if cited == {row['source_section']} else 'fail',
                             [row['source_section']], sorted(str(s) for s in cited)))
        if condition == 'base':
            names = ['standard_far_by_district', 'qualifying_far_by_district']
        elif condition == 'within_100ft_wide_street':
            names = ['wide_street_far_by_district', 'qualifying_far_by_district']
        elif condition == 'wide_street_additional_conditions':
            names = ['wide_street_far_by_district', 'wide_street_qualifying_far_by_district']
        else:
            results.append(check('reference_structure', str(key), 'fail',
                                 reason='Unrecognized condition; no inferred comparison.'))
            continue
        for column, param in zip(['standard_far', 'qualifying_far'], names):
            actual = params.get(param, {}).get(district)
            result = compare_number('reference_value', f'{district}:{condition}:{column}',
                                    row[column], actual)
            if result['status'] == 'gap':
                result['status'] = 'fail'  # Required rule-table entry is missing.
            results.append(result)
    extra = set(owners) - {d for d, _ in expected_keys}
    for district in sorted(extra):
        results.append(check('reference_structure', district, 'fail',
                             reason='Rule has a district absent from source expectations.'))
    return results


def audit_observation(record, observation):
    """Compare a recorded UI observation with its city record, never infer cap."""
    if observation is None:
        return [check('application_display', 'not_observed', 'gap',
                      reason='No dated application observation supplied.')]
    try:
        expected_bbl = normalize_bbl(record.get('bbl'))
        seen_bbl = normalize_bbl(observation.get('bbl'))
    except ValueError as exc:
        return [check('application_identity', 'bbl', 'fail', reason=str(exc))]
    if expected_bbl != seen_bbl:
        return [check('application_identity', 'bbl', 'fail', expected_bbl, seen_bbl)]
    results = [check('application_identity', 'bbl', 'pass', expected_bbl, seen_bbl)]
    for label, source_field in FIELDS.items():
        results.append(compare_number('application_display', label,
                                      record.get(source_field), observation.get(label)))
    results.append(check('application_calculation', 'project_allowance', 'gap',
                         observed={k: observation.get(k) for k in (
                             'calculated_far', 'calculated_floor_area_sq_ft',
                             'calculation_status')},
                         reason='Display/source comparison does not validate project eligibility '
                                'or a computed allowance; no independent property case supplied.'))
    return results


def audit_parcels(pluto, ztldb, observations):
    results, parcels, seen = [], [], set()
    zone_rows = {}
    for row in ztldb['records']:
        zone_rows.setdefault(normalize_bbl(row.get('bbl')), []).append(row)
    boroughs = {'1': 'MN', '2': 'BX', '3': 'BK', '4': 'QN', '5': 'SI'}
    for query in pluto['queries']:
        if query.get('error'):
            results.append(check('source_request', query['case'], 'gap',
                                 reason=query['error']))
            continue
        for record in query.get('records', []):
            bbl = normalize_bbl(record['bbl'])
            if bbl in seen:
                continue
            seen.add(bbl)
            identity = bbl == (bbl[0] + str(int(record['block'])).zfill(5)
                              + str(int(record['lot'])).zfill(4))
            identity = identity and boroughs[bbl[0]] == record['borough']
            checks = [check('city_identity', bbl, 'pass' if identity else 'fail')]
            matches = zone_rows.get(bbl, [])
            if len(matches) != 1:
                checks.append(check('city_zoning_crosscheck', bbl, 'gap', 1, len(matches),
                                    'ZTLDB match absent or ambiguous; no inferred match.'))
            else:
                left = {record[f'zonedist{i}'] for i in range(1, 5)
                        if record.get(f'zonedist{i}')}
                right = {matches[0][f'zoning_district_{i}'] for i in range(1, 5)
                         if matches[0].get(f'zoning_district_{i}')}
                checks.append(check('city_zoning_crosscheck', bbl,
                                    'pass' if left == right else 'fail',
                                    sorted(left), sorted(right)))
            checks.extend(audit_observation(record, observations.get(bbl)))
            results.extend(checks)
            contexts = []
            if record.get('splitzone') is True:
                contexts.append('split')
            if record.get('spdist1') or record.get('spdist2'):
                contexts.append('special_district')
            if '/' in record.get('zonedist1', ''):
                contexts.append('mixed_district')
            if number(record.get('condono')) not in (None, 0):
                contexts.append('condominium_billing_lot')
            if bbl == '3052960043':
                contexts.append('reported_address_alias_benchmark')
            parcels.append({'bbl': bbl, 'case': query['case'], 'address': record['address'],
                            'borough': record['borough'], 'source_record': record,
                            'source_url': query['source_url'],
                            'retrieved_at': query['retrieved_at'],
                            'contexts': contexts, 'checks': checks})
    return parcels, results


def audit_engine(matrix, rules, root):
    """Run existing draft engine, using fresh source values as the oracle."""
    sys.path.insert(0, str(root / 'services/api'))
    from app.rules import RuleRegistry
    from app.rules.integration import evaluate_property

    registry = RuleRegistry().load()  # Default packaged snapshots; no bypass.
    owners = {d: r['rule_id'] for r in rules for d in r['applicability']['values']}
    results = []
    for row in matrix['rows']:
        if row['condition'] != 'base':
            results.append(check('engine_conditional_coverage', row['district'], 'gap',
                                 reason='Conditional wide-street value is stored; property '
                                        'eligibility and higher-value selection not validated here.'))
            continue
        inputs = {'zoning_district': row['district'], 'lot_area_sq_ft': 2500}
        trace = registry.evaluate(owners[row['district']], inputs,
                                  as_of_date='2026-09-15').export()
        for name, expected in [('max_residential_far', row['standard_far']),
                               ('max_residential_floor_area_sq_ft',
                                str(number(row['standard_far']) * 2500))]:
            results.append(compare_number('draft_engine_value', row['district'] + ':' + name,
                                          expected, trace['outputs'].get(name)))
        results.append(check('draft_engine_status', row['district'],
                             'pass' if trace['coverage_status'] != 'verified'
                             and trace['rule_status'] == 'needs_review' else 'fail',
                             'needs_review; not verified',
                             [trace['rule_status'], trace['coverage_status']]))
        exceptions = {e['id'] for e in trace['exceptions_applied']}
        if row['district'] in {'R6', 'R7-1', 'R7-2', 'R8'}:
            results.append(check('engine_conditional_guard', row['district'],
                                 'pass' if 'wide_street_far_alternative' in exceptions else 'fail',
                                 'wide-street alternative retained', sorted(exceptions)))
        if '23-21-footnote-1' in row['notes']:
            results.append(check('engine_limitation_guard', row['district'],
                                 'pass' if 'single_dwelling_unit_equivalent_far_cap'
                                 in exceptions else 'fail',
                                 'per-unit limitation retained', sorted(exceptions)))
        results.append(check('engine_qualifying_coverage', row['district'], 'gap',
                             reason='Qualifying FAR is a recorded alternative; qualifying '
                                    'site/project eligibility not calculated by this audit.'))
    for label, area in [('missing', None), ('zero', 0), ('negative', -1),
                        ('malformed', '2400garbage'), ('boolean', True)]:
        trace = registry.evaluate('r6-r12-residential-far',
                                  {'zoning_district': 'R6A', 'lot_area_sq_ft': area}).export()
        results.append(check('engine_refusal', label,
                             'pass' if not trace['outputs'] else 'fail', {}, trace['outputs']))
    for district in ['R10H', 'M1-2/R6A']:
        traces = [registry.evaluate(r['rule_id'], {'zoning_district': district,
                  'lot_area_sq_ft': 2400}).export() for r in rules]
        emitted = [t['outputs'] for t in traces if t['outputs']]
        results.append(check('engine_refusal', district, 'pass' if not emitted else 'fail',
                             [], emitted, 'Refusal is not numerical coverage.'))
    for label, spatial in [('missing_spatial', None),
                           ('split_lot', {'lot_overall_class': 'split_lot'}),
                           ('conflict', {'lot_overall_class': 'data_conflict'})]:
        profile = {'identity': {'bbl': '3052960043'}, 'spatial_intersection': spatial}
        result = evaluate_property(profile, registry=registry)
        results.append(check('profile_refusal', label,
                             'pass' if not result.evaluations else 'fail', [],
                             result.evaluations, 'Refusal is not numerical coverage.'))
    for family in ['height', 'yards', 'lot_coverage']:
        results.append(check('bulk_coverage', family, 'gap',
                             reason='Not established by this residential FAR audit.'))
    return results


def run(root, engine=False):
    def read(name):
        return json.loads((root / FIXTURES / name).read_text())
    matrix = read('official_far_expectations.json')
    rules = [json.loads(p.read_text()) for p in sorted(
        (root / 'services/api/app/rules/rulesets').glob('*far.rule.json'))]
    checks = audit_tables(matrix, rules, root)
    observation_path = root / FIXTURES / 'application_observations.json'
    observations = json.loads(observation_path.read_text()) if observation_path.exists() else {}
    parcels, parcel_checks = audit_parcels(read('pluto_sample.json'),
                                         read('ztldb_sample.json'), observations)
    checks.extend(parcel_checks)
    if engine:
        checks.extend(audit_engine(matrix, rules, root))
    else:
        checks.append(check('draft_engine_execution', 'not_run', 'gap',
                            reason='Use --engine in the locked API runtime.'))
    summary = Counter(c['status'] for c in checks)
    return {'schema_version': 1, 'scope': 'Independent reference and representative checks only',
            'summary': dict(summary), 'checks': checks, 'parcels': parcels,
            'legal_approval': False, 'citywide_buildability_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-fixtures', action='store_true')
    parser.add_argument('--engine', action='store_true')
    parser.add_argument('--full', action='store_true', help='Print all layer results as JSON.')
    args = parser.parse_args()
    try:
        result = run(ROOT, args.engine)
    except (KeyError, ValueError, TypeError, OSError, ImportError) as exc:
        print(json.dumps({'status': 'fail', 'error': type(exc).__name__, 'reason': str(exc)}))
        return 1
    print(json.dumps(result if args.full else {
        'summary': result['summary'], 'parcels': len(result['parcels']),
        'legal_approval': False, 'citywide_buildability_verified': False}, indent=2))
    return int(result['summary'].get('fail', 0) > 0)


if __name__ == '__main__':
    raise SystemExit(main())
