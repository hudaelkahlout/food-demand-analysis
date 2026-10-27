"""Independent integer-cents/SQLite KPI validation; no imports of KPI logic."""

import csv
import hashlib
import json
import math
from pathlib import Path
import sqlite3

import nbformat

ROOT = Path(__file__).resolve().parents[1]


def cents(value):
    """Independent price parser for this source's nonnegative two-decimal prices."""
    whole, _, fractional = value.partition('.')
    if not whole.isdigit() or len(fractional) > 2 or (fractional and not fractional.isdigit()):
        raise ValueError('Expected nonnegative price with at most two decimal places')
    return int(whole) * 100 + int(fractional.ljust(2, '0') or '0')


def main():
    out = ROOT / 'data/processed/phase7'
    result = json.loads((out / 'kpi_results.json').read_text())
    with sqlite3.connect(':memory:') as db:
        db.execute('CREATE TABLE demand (week INTEGER, meal TEXT, orders INTEGER, checkout INTEGER, base INTEGER, email INTEGER, homepage INTEGER)')
        with (ROOT / 'data/processed/train_prepared.csv').open(encoding='utf-8', newline='') as stream:
            db.executemany('INSERT INTO demand VALUES (?,?,?,?,?,?,?)',
                           ((int(r['week']),r['meal_id'],int(r['num_orders']),cents(r['checkout_price']),cents(r['base_price']),int(r['emailer_for_promotion']),int(r['homepage_featured'])) for r in csv.DictReader(stream)))
        count, total, weeks, amount, email, homepage = db.execute('SELECT COUNT(*), SUM(orders), COUNT(DISTINCT week), SUM(checkout*orders), SUM(email), SUM(homepage) FROM demand').fetchone()
        assert count == result['observation_count'] and total == result['total_orders']
        # Check the decimal string against exact independently parsed integer cents.
        assert cents(result['revenue_proxy']) == amount
        average_weekly = db.execute('SELECT AVG(n) FROM (SELECT SUM(orders) n FROM demand GROUP BY week)').fetchone()[0]
        assert average_weekly == result['average_weekly_demand'] == total / weeks
        assert email == result['email_promotion_rows'] and homepage == result['homepage_feature_rows']
        assert email / count == result['email_promotion_share']
        assert homepage / count == result['homepage_feature_share']
        discount, low, high, negative, invalid = db.execute('SELECT AVG(1.0*(base-checkout)/base), MIN(1.0*(base-checkout)/base), MAX(1.0*(base-checkout)/base), SUM(checkout>base), SUM(base<=0 OR checkout<0) FROM demand').fetchone()
        assert invalid == result['discount_invalid_rows'] == result['revenue_invalid_rows'] == 0
        for expected, actual in [(discount,result['discount_mean_rate']),(low,result['discount_min_rate']),(high,result['discount_max_rate'])]:
            assert math.isclose(expected,actual,rel_tol=1e-12,abs_tol=1e-12)
        assert negative == result['negative_discount_rows'] == 116101
        meals = {r['meal_id']:r for r in result['volatility']}
        checked=0
        for meal,n,total_meal,sum_squares in db.execute('SELECT meal,COUNT(*),SUM(orders),SUM(orders*orders) FROM demand GROUP BY meal'):
            mean=total_meal/n
            # Independent sample variance via sums of squares, not statistics.stdev.
            std=math.sqrt((sum_squares-total_meal*total_meal/n)/(n-1))
            row=meals[meal]
            assert n==row['observations']
            for expected,actual in [(mean,row['mean_orders']),(std,row['sample_std_orders']),(std/mean,row['cv'])]:
                assert math.isclose(expected,actual,rel_tol=1e-12,abs_tol=1e-12),(meal,expected,actual)
            checked+=1
        assert checked==len(meals)==51
    with (out/'meal_volatility.csv').open(newline='') as stream:
        assert len(list(csv.DictReader(stream)))==51
    with (out/'kpi_summary.csv').open(newline='') as stream:
        assert len(list(csv.DictReader(stream)))==6
    notebook=nbformat.read(ROOT/'notebooks/analysis.ipynb',as_version=4)
    nbformat.validate(notebook)
    code=[c for c in notebook.cells if c.cell_type=='code']
    assert [c.execution_count for c in code]==list(range(1,len(code)+1))
    assert not [o for c in code for o in c.outputs if o.output_type=='error']
    assert any('calculate_prepared_kpis' in c.source for c in code)
    saved=json.loads((ROOT/'docs/phase7_notebook_validation.json').read_text())
    # Later authorized phases may append cells; the current notebook itself is
    # validated above, while this record remains the historical Phase 7 run.
    assert saved['status']=='passed' and saved['code_cells_executed']<=len(code)
    phase5=json.loads((ROOT/'docs/phase5_audit.json').read_text())
    for name,expected in phase5['raw_sha256_after'].items():
        assert hashlib.sha256((ROOT/'data/raw'/name).read_bytes()).hexdigest()==expected
    assert hashlib.sha256((ROOT/'data/processed/train_prepared.csv').read_bytes()).hexdigest()==phase5['outputs']['train_prepared.csv']['sha256']
    validation={'status':'passed','independent_method':'SQLite sums, exact integer-cents revenue, floating rate averages, independent sample variance from sums of squares',
                'scalar_kpis_verified':6,'meal_cvs_verified':checked,'negative_discounts_preserved':negative,
                'revenue_exact_to_cent':True,'discount_tolerance':1e-12,'cv_relative_tolerance':1e-12,
                'notebook_code_cells':len(code),'notebook_errors':0,'raw_and_prepared_inputs':'unchanged','phase8_tests':'not run'}
    (ROOT/'docs/phase7_validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    print(json.dumps(validation,indent=2))


if __name__=='__main__':
    main()
