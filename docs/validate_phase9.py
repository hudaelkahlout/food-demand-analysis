"""Independent raw-observation aggregates/variance and median quadrant checks."""

from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import sqlite3

import nbformat

ROOT=Path(__file__).resolve().parents[1]


def main():
    result=json.loads((ROOT/'data/processed/phase9/inventory_segments.json').read_text())
    phase7=json.loads((ROOT/'data/processed/phase7/kpi_results.json').read_text())
    previous={r['meal_id']:r for r in phase7['volatility']}
    with sqlite3.connect(':memory:') as db:
        db.execute('CREATE TABLE demand (meal TEXT,orders INTEGER,category TEXT,cuisine TEXT,center TEXT,week INTEGER)')
        with (ROOT/'data/processed/train_prepared.csv').open(newline='',encoding='utf-8') as stream:
            db.executemany('INSERT INTO demand VALUES (?,?,?,?,?,?)',((r['meal_id'],int(r['num_orders']),r['category'],r['cuisine'],r['center_id'],int(r['week'])) for r in csv.DictReader(stream)))
        independent={}
        for meal,n,total,squares,category,cuisine,centers,weeks in db.execute('SELECT meal,COUNT(*),SUM(orders),SUM(orders*orders),MIN(category),MIN(cuisine),COUNT(DISTINCT center),COUNT(DISTINCT week) FROM demand GROUP BY meal'):
            mean=total/n; std=math.sqrt((squares-total*total/n)/(n-1)); cv=std/mean
            independent[meal]=dict(orders=total,observations=n,cv=cv,category=category,cuisine=cuisine,observed_centers=centers,observed_weeks=weeks)
        source_rows,total_orders=db.execute('SELECT COUNT(*),SUM(orders) FROM demand').fetchone()
    assert len(independent)==len(previous)==result['total_meals']==51
    assert source_rows==result['input_rows']==456548 and total_orders==result['total_orders']==119557485
    # Odd-sized 51-meal medians are independently selected by order statistic.
    volume_cut=sorted(r['orders'] for r in independent.values())[25]
    cv_cut=sorted(r['cv'] for r in independent.values())[25]
    assert volume_cut==result['thresholds']['volume_orders']
    assert math.isclose(cv_cut,result['thresholds']['cv'],rel_tol=1e-12,abs_tol=1e-12)
    observed={r['meal_id']:r for r in result['meals']}
    assert set(observed)==set(independent)
    counts=Counter(); totals=Counter(); observations=Counter(); priority=[]
    for meal,expected in independent.items():
        actual=observed[meal]
        for key in ['orders','observations','category','cuisine','observed_centers','observed_weeks']:
            assert actual[key]==expected[key],(meal,key)
        assert actual['cv']==previous[meal]['cv'],'Phase 7 CV must be reused unchanged'
        assert math.isclose(actual['cv'],expected['cv'],rel_tol=1e-12,abs_tol=1e-12)
        segment=('high' if expected['orders']>=volume_cut else 'low')+' volume / '+('high' if expected['cv']>=cv_cut else 'low')+' volatility'
        assert actual['segment']==segment
        assert actual['priority_review']==(segment=='high volume / high volatility')
        assert actual['meal_name']=='Not supplied' and actual['interpretation']
        counts[segment]+=1;totals[segment]+=expected['orders'];observations[segment]+=expected['observations']
        if actual['priority_review']:priority.append(actual)
    for segment in result['segment_summary']:
        name=segment['segment']
        assert counts[name]==segment['meals'] and totals[name]==segment['orders'] and observations[name]==segment['observations']
        assert math.isclose(100*totals[name]/total_orders,segment['demand_share_pct'],abs_tol=1e-12)
    priority.sort(key=lambda r:(-r['orders'],-r['cv'],int(r['meal_id'])))
    assert [r['meal_id'] for r in priority]==result['priority_meal_ids']
    assert sum(counts.values())==51 and sum(totals.values())==total_orders and sum(observations.values())==source_rows
    with (ROOT/'data/processed/phase9/meal_inventory_segments.csv').open(newline='') as stream:
        assert len(list(csv.DictReader(stream)))==51
    notebook=nbformat.read(ROOT/'notebooks/analysis.ipynb',as_version=4);nbformat.validate(notebook)
    code=[c for c in notebook.cells if c.cell_type=='code']
    assert [c.execution_count for c in code]==list(range(1,len(code)+1))
    assert not [o for c in code for o in c.outputs if o.output_type=='error']
    images=sum('image/png' in o.get('data',{}) for c in code for o in c.outputs)
    assert images==6
    figure=ROOT/'reports/figures/demand_volume_volatility.png'
    assert figure.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    phase5=json.loads((ROOT/'docs/phase5_audit.json').read_text())
    for name,digest in phase5['raw_sha256_after'].items():assert hashlib.sha256((ROOT/'data/raw'/name).read_bytes()).hexdigest()==digest
    assert hashlib.sha256((ROOT/'data/processed/train_prepared.csv').read_bytes()).hexdigest()==phase5['outputs']['train_prepared.csv']['sha256']
    assert hashlib.sha256((ROOT/'data/processed/phase7/kpi_results.json').read_bytes()).hexdigest()==result['phase7_kpi_sha256']
    assert not (ROOT/'notebooks/machine_learning.ipynb').exists()
    report={'status':'passed','independent_method':'SQLite meal sums/counts, sample variance from sum of squares, 26th-order-statistic medians, independently assigned quadrants',
            'meals_verified':51,'phase7_cvs_reused_exactly':True,'source_rows_conserved':source_rows,'orders_conserved':total_orders,
            'segment_counts':dict(counts),'priority_order_verified':True,'notebook_cells':len(code),'notebook_errors':0,'embedded_images':images,
            'volume_volatility_png':'verified','raw_and_phase5_input_hashes':'unchanged','phase10_notebook':'absent'}
    (ROOT/'docs/phase9_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
