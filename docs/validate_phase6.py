"""Independent SQLite aggregation and notebook-output validation for Phase 6."""

import csv
import hashlib
import json
from pathlib import Path
import sqlite3

import nbformat

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT / 'data/processed/phase6'
    result = json.loads((out / 'eda_results.json').read_text())
    phase5 = json.loads((ROOT / 'docs/phase5_audit.json').read_text())
    with sqlite3.connect(':memory:') as db:
        db.execute('CREATE TABLE demand (week INTEGER, orders INTEGER, category TEXT, meal TEXT, center TEXT, kind TEXT)')
        with (ROOT / 'data/processed/train_prepared.csv').open(newline='', encoding='utf-8') as stream:
            db.executemany('INSERT INTO demand VALUES (?,?,?,?,?,?)',
                           ((int(r['week']), int(r['num_orders']), r['category'], r['meal_id'], r['center_id'], r['center_type']) for r in csv.DictReader(stream)))
        count, total = db.execute('SELECT COUNT(*),SUM(orders) FROM demand').fetchone()
        assert count == result['input_rows'] == 456548
        assert total == result['input_orders'] == 119557485
        weekly = dict(db.execute('SELECT week,SUM(orders) FROM demand GROUP BY week'))
        assert weekly == {r['week']: r['orders'] for r in result['weekly']}
        for r in result['weekly']:
            previous = weekly.get(r['week'] - 1)
            expected = 100 * (r['orders'] - previous) / previous if previous else None
            assert r['change_pct'] == expected
        for field, column in [('categories', 'category'), ('meals', 'meal')]:
            totals = dict(db.execute(f'SELECT {column},SUM(orders) FROM demand GROUP BY {column}'))
            concentration = result[field]
            assert totals == {r['key']: r['orders'] for r in concentration['ranking']}
            ranking = sorted(totals.items(), key=lambda pair: (-pair[1], pair[0]))
            running = 0; expected_count = 0
            while 5 * running < 4 * total:
                running += ranking[expected_count][1]; expected_count += 1
            assert expected_count == concentration['threshold_count']
            assert running == concentration['selected_orders']
            assert concentration['previous_share_pct'] < 80 <= concentration['selected_share_pct']
        db.execute('CREATE TABLE center_week AS SELECT center,kind,week,SUM(orders) orders FROM demand GROUP BY center,kind,week')
        centers = {c: (n, w, avg) for c, n, w, avg in db.execute('SELECT center,SUM(orders),COUNT(*),AVG(orders) FROM center_week GROUP BY center')}
        for center in result['centers']:
            assert centers[center['center_id']] == (center['orders'],center['observed_weeks'],center['average_observed_week_orders'])
        types = {t: (n, c, w, avg) for t,n,c,w,avg in db.execute('SELECT kind,SUM(orders),COUNT(DISTINCT center),COUNT(*),AVG(orders) FROM center_week GROUP BY kind')}
        for kind in result['center_types']:
            assert types[kind['center_type']] == (kind['orders'],kind['centers'],kind['observed_center_weeks'],kind['orders_per_observed_center_week'])
    notebook = nbformat.read(ROOT / 'notebooks/analysis.ipynb', as_version=4)
    nbformat.validate(notebook)
    code = [cell for cell in notebook.cells if cell.cell_type == 'code']
    assert [cell.execution_count for cell in code] == list(range(1,len(code)+1))
    assert not [o for cell in code for o in cell.outputs if o.output_type == 'error']
    images = sum('image/png' in o.get('data',{}) for cell in code for o in cell.outputs)
    assert images >= 5  # Later authorized phases may append figures.
    profile = json.loads((out / 'enriched_profile.json').read_text())
    assert profile['analysis']['rows_scanned'] == count and not profile['analysis']['row_limit_reached']
    for name, expected in phase5['raw_sha256_after'].items():
        assert hashlib.sha256((ROOT / 'data/raw' / name).read_bytes()).hexdigest() == expected
    assert hashlib.sha256((ROOT / 'data/processed/train_prepared.csv').read_bytes()).hexdigest() == phase5['outputs']['train_prepared.csv']['sha256']
    validation = {'status': 'passed', 'independent_sqlite_aggregates': ['weekly','categories','meals','centers','center_types'],
                  'threshold_crossing_80pct': 'passed', 'center_week_denominators': 'passed',
                  'notebook_code_cells': len(code), 'notebook_error_outputs': 0, 'embedded_figures': images,
                  'skill_scan_rows': count, 'skill_row_truncation': False,
                  'raw_and_phase5_input_hashes': 'unchanged', 'final_report_figures': 'outside Phase 6 verification scope'}
    (ROOT / 'docs/phase6_validation.json').write_text(json.dumps(validation, indent=2) + '\n')
    print(json.dumps(validation, indent=2))


if __name__ == '__main__':
    main()
