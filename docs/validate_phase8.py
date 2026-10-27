"""Independent counts/ranks/SQLite means and scalar week-block replication."""

from collections import Counter, defaultdict
import csv
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import sqlite3

import nbformat
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def independent_u(x,y):
    a,b=Counter(x),Counter(y); below=0; u=0
    for value in sorted(a.keys()|b.keys()):
        u+=a[value]*(below+.5*b[value]); below+=b[value]
    n,m=len(x),len(y); size=n+m; ties=a+b
    variance=n*m/12*(size+1-sum(t**3-t for t in ties.values())/(size*(size-1)))
    p=min(1.,math.erfc((abs(u-n*m/2)-.5)/math.sqrt(2*variance))) if variance else 1.
    return u,p


def ranks(values):
    counts=Counter(values); previous=0; mapping={}
    for value in sorted(counts):
        mapping[value]=previous+(counts[value]+1)/2; previous+=counts[value]
    return np.array([mapping[value] for value in values])


def main():
    result=json.loads((ROOT/'data/processed/phase8/promotion_results.json').read_text())
    groups=defaultdict(list); discounts=[]; demands=[]; negatives=0
    db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE demand (context TEXT,week INTEGER,orders INTEGER,discount REAL,email INTEGER,homepage INTEGER,state TEXT)')
    with (ROOT/'data/processed/train_prepared.csv').open(newline='',encoding='utf-8') as stream:
        for r in csv.DictReader(stream):
            e,h=int(r['emailer_for_promotion']),int(r['homepage_featured'])
            state=('both' if e and h else 'email_only' if e else 'homepage_only' if h else 'neither')
            d=float((Decimal(r['base_price'])-Decimal(r['checkout_price']))/Decimal(r['base_price']))
            n=int(r['num_orders']); week=int(r['week']); context=r['center_id']+'/'+r['meal_id']
            groups[context].append((week,n,d,e,h,state)); discounts.append(d);demands.append(n);negatives+=d<0
            db.execute('INSERT INTO demand VALUES (?,?,?,?,?,?,?)',(context,week,n,d,e,h,state))
    assert len(demands)==result['rows']==456548 and sum(demands)==result['total_orders']==119557485
    assert negatives==result['negative_discounts']==116101
    common=set(row[0] for row in db.execute('SELECT context FROM (SELECT context,state,COUNT(*) n FROM demand GROUP BY context,state) GROUP BY context HAVING COUNT(*)=4 AND MIN(n)>=5'))
    assert len(common)==result['combined']['common_four_state_contexts']==490
    cases=[('email',3,1,0,result['email'],None),('homepage',4,1,0,result['homepage'],None)]
    cases += [(name,5,name,'neither',value,common) for name,value in result['combined']['contrasts'].items()]
    for name,index,one,zero,observed,restrict in cases:
        selected={key:([r for r in rows if r[index]==one],[r for r in rows if r[index]==zero]) for key,rows in groups.items()
                  if (restrict is None or key in restrict) and sum(r[index]==one for r in rows)>=5 and sum(r[index]==zero for r in rows)>=5}
        x=[r[1] for a,b in selected.values() for r in a];y=[r[1] for a,b in selected.values() for r in b]
        mean1=sum(sum(r[1] for r in a)/len(a) for a,b in selected.values())/len(selected)
        mean0=sum(sum(r[1] for r in b)/len(b) for a,b in selected.values())/len(selected)
        assert len(selected)==observed['coverage']['eligible_series']
        assert len(x)==observed['pooled_promoted']['n'] and len(y)==observed['pooled_reference']['n']
        assert math.isclose(mean1,observed['promoted_context_mean'],abs_tol=1e-9)
        assert math.isclose(mean0,observed['reference_context_mean'],abs_tol=1e-9)
        assert math.isclose(100*(mean1-mean0)/mean0,observed['percentage_difference'],abs_tol=1e-9)
        u,p=independent_u(x,y)
        assert u==observed['mann_whitney_pooled_reference']['u']
        assert math.isclose(p,observed['mann_whitney_pooled_reference']['iid_reference_p'],abs_tol=1e-12)
        # Independently form the linearized weekly scores, then scalar block draws.
        score=[0.]*145
        for a,b in selected.values():
            for rows,sign in [(a,1),(b,-1)]:
                average=sum(r[1] for r in rows)/len(rows)
                for r in rows: score[r[0]-1]+=sign*(r[1]-average)/len(rows)/len(selected)
        assert abs(sum(score))<1e-9
        for interval in observed['uncertainty']['sensitivity']:
            length=interval['block_weeks']; rng=np.random.default_rng(20261027); draws=[]
            for _ in range(2000):
                starts=rng.integers(0,145,size=math.ceil(145/length))
                sampled=[score[(int(start)+j)%145] for start in starts for j in range(length)][:145]
                draws.append(mean1-mean0+sum(sampled))
            expected=np.percentile(draws,[2.5,97.5,.5,99.5])
            assert np.allclose(expected,list(interval['difference_ci95'])+list(interval['difference_ci99_family5']),atol=1e-8,rtol=1e-10)
    rho=float(np.corrcoef(ranks(discounts),ranks(demands))[0,1])
    assert math.isclose(rho,result['spearman']['rho'],abs_tol=1e-12)
    within=[]; within_rows=within_orders=0
    for rows in groups.values():
        if len(rows)>=10 and len({r[2] for r in rows})>1 and len({r[1] for r in rows})>1:
            within.append(float(np.corrcoef(ranks([r[2] for r in rows]),ranks([r[1] for r in rows]))[0,1]))
            within_rows+=len(rows);within_orders+=sum(r[1] for r in rows)
    assert len(within)==result['spearman']['within_context']['eligible_contexts']
    assert math.isclose(float(np.mean(within)),result['spearman']['within_context']['mean_rho_equal_context'],abs_tol=1e-12)
    assert within_rows==result['spearman']['within_context']['eligible_rows']
    assert within_orders==result['spearman']['within_context']['eligible_orders']
    assert within_rows+result['spearman']['within_context']['excluded_rows']==len(demands)
    assert within_orders+result['spearman']['within_context']['excluded_orders']==sum(demands)
    for flag in ['email','homepage']:
        for value in [0,1]:
            n,d=db.execute(f'SELECT COUNT(*),AVG(discount) FROM demand WHERE {flag}=?',(value,)).fetchone()
            assert n==result[flag]['overlap'][str(value)]['rows']
            assert math.isclose(d,result[flag]['overlap'][str(value)]['discount']['mean'],abs_tol=1e-12)
    for state,observed in result['combined']['global_states'].items():
        n,mean=db.execute('SELECT COUNT(*),AVG(orders) FROM demand WHERE state=?',(state,)).fetchone()
        assert n==observed['demand']['n'] and math.isclose(mean,observed['demand']['mean'],abs_tol=1e-12)
    db.close()
    nb=nbformat.read(ROOT/'notebooks/analysis.ipynb',as_version=4);nbformat.validate(nb)
    code=[c for c in nb.cells if c.cell_type=='code']
    assert [c.execution_count for c in code]==list(range(1,len(code)+1))
    assert not [o for c in code for o in c.outputs if o.output_type=='error']
    phase5=json.loads((ROOT/'docs/phase5_audit.json').read_text())
    for name,value in phase5['raw_sha256_after'].items(): assert hashlib.sha256((ROOT/'data/raw'/name).read_bytes()).hexdigest()==value
    assert hashlib.sha256((ROOT/'data/processed/train_prepared.csv').read_bytes()).hexdigest()==phase5['outputs']['train_prepared.csv']['sha256']
    report={'status':'passed','context_comparisons_verified':len(cases),'mann_whitney':'independent frequency-count U and tie-corrected normal reference p',
            'bootstrap':'all five contrasts, 4/8/12-week blocks independently replicated with scalar draws',
            'spearman':'global and within-context midranks independently correlated','discount_overlap':'SQLite counts/averages match',
            'negative_discounts_unchanged':negatives,'notebook_cells':len(code),'notebook_errors':0,'raw_and_prepared_inputs':'unchanged'}
    (ROOT/'docs/phase8_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
