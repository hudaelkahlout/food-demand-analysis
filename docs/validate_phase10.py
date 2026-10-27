"""Independent Phase 10 checks using CSV/SQLite and scalar MAE arithmetic."""
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import math
import subprocess
import tempfile
import numpy as np
import pandas as pd
from src.machine_learning.forecast import features,history_of
ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'data/processed/phase10'; r=json.loads((out/'results.json').read_text())
    connection=sqlite3.connect(':memory:')
    connection.execute('create table source(id integer, week integer, center integer, meal integer, orders real)')
    with (ROOT/'data/raw/train.csv').open(newline='') as f:
        source=list(csv.DictReader(f))
    connection.executemany('insert into source values(?,?,?,?,?)',[(int(x['id']),int(x['week']),int(x['center_id']),int(x['meal_id']),float(x['num_orders'])) for x in source])
    fit_count,fit_orders=connection.execute('select count(*),sum(orders) from source where week<=135').fetchone()
    hold_count,hold_orders=connection.execute('select count(*),sum(orders) from source where week>=136').fetchone()
    assert (fit_count,hold_count,fit_orders,hold_orders)==(r['fit_rows'],r['holdout_rows'],r['fit_orders'],r['holdout_orders'])
    observed={int(x['id']):float(x['num_orders']) for x in source if int(x['week'])>=136}
    with (out/'holdout_predictions.csv').open(newline='') as f: hold=list(csv.DictReader(f))
    assert len(hold)==hold_count and {int(x['id']) for x in hold}==set(observed)
    independent={}
    for name,metric in r['metrics'].items():
        mae=math.fsum(abs(observed[int(x['id'])]-float(x[name])) for x in hold)/hold_count
        assert math.isclose(mae,metric['mae'],rel_tol=1e-12)
        independent[name]=mae
    history={(int(x['week']),int(x['center_id']),int(x['meal_id'])):float(x['num_orders']) for x in source if int(x['week'])<=135}
    fallback=float(np.median([float(x['num_orders']) for x in source if int(x['week'])<=135]))
    # Independently reconstruct baseline in chronological batches without holdout actuals.
    absent=0
    for week in range(136,146):
        for x in [x for x in hold if int(x['week'])==week]:
            key=(week-1,int(x['center_id']),int(x['meal_id']))
            absent+=key not in history
            expected=history.get(key,fallback)
            assert float(x['Previous-week baseline'])==expected
            history[(week,int(x['center_id']),int(x['meal_id']))]=expected
    assert absent==r['metrics']['Previous-week baseline']['missing_previous_week']
    assert r['winner']==min(independent,key=independent.get)
    for m in r['metrics'].values():
        assert math.isclose(m['improvement_pct_vs_baseline'],100*(independent['Previous-week baseline']-m['mae'])/independent['Previous-week baseline'],abs_tol=1e-10)
    with (ROOT/'data/raw/test.csv').open(newline='') as f: test=list(csv.DictReader(f))
    with (out/'test_predictions.csv').open(newline='') as f: pred=list(csv.DictReader(f))
    assert [x['id'] for x in test]==[x['id'] for x in pred]
    values=[float(x['num_orders']) for x in pred]
    assert len(values)==32573 and all(math.isfinite(v) and v>=0 for v in values)
    train=pd.read_csv(ROOT/'data/processed/train_prepared.csv')
    sample=train.loc[train.week.between(136,137)].copy()
    h=history_of(train.loc[train.week<=135])
    # Poison all current/future labels: exact feature equality must hold.
    poisoned=history_of(train.loc[train.week<=135])
    for w,c,m in sample[['week','center_id','meal_id']].itertuples(index=False,name=None):
        poisoned[(w,c,m)]=1e12
    first=sample.loc[sample.week==136]
    pd.testing.assert_frame_equal(features(first,h),features(first,poisoned))
    for name,expected in r['raw_hashes'].items():
        assert hashlib.sha256((ROOT/'data/raw'/name).read_bytes()).hexdigest()==expected
    assert hashlib.sha256((ROOT/'data/processed/train_prepared.csv').read_bytes()).hexdigest()=='52467bcad7b7c863276d1844bfe8a677cbfd4d6d08256d704e8da1e4a79cf137'
    probes=['data/raw/train.csv','data/raw/test.csv','data/processed/phase10/test_predictions.csv','data/processed/phase10/results.json']
    with tempfile.TemporaryDirectory(prefix='food-phase10-ignore-') as folder:
        subprocess.run(['git','init','--bare','--quiet',folder],check=True)
        for probe in probes:
            check=subprocess.run(['git',f'--git-dir={folder}',f'--work-tree={ROOT}','check-ignore','--no-index','-v','--',probe],capture_output=True,text=True,check=True)
            assert '/data/' in check.stdout
    result=dict(status='passed',git_ignore_probes=len(probes),independent_mae=independent,fit_rows=fit_count,holdout_rows=hold_count,
        baseline_recursion='independently reconstructed',test_ids_and_order='exact match',test_predictions=len(values),
        finite_nonnegative=True,current_future_label_poisoning='identical features',raw_and_prepared_hashes='unchanged',
        evaluation_coverage='all holdout rows; none excluded')
    (ROOT/'docs/phase10_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()

