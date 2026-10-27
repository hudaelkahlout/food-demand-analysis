"""Targeted Phase 12 plot-data checks, without a full suite or model rerun."""
from pathlib import Path
import hashlib
import json
import math
import struct
from decimal import Decimal
import numpy as np
import pandas as pd
from scipy.stats import rankdata
ROOT=Path(__file__).resolve().parents[1]
def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def close(a,b):assert math.isclose(float(a),float(b),rel_tol=1e-11,abs_tol=1e-9),(a,b)

def main():
    manifest=load('data/processed/phase12/export_manifest.json'); before=load('data/processed/phase12/before.json')
    a=load('data/processed/phase6/eda_results.json'); p=load('data/processed/phase8/promotion_results.json'); v=load('data/processed/phase9/inventory_segments.json')
    frame=pd.read_csv(ROOT/'data/processed/train_prepared.csv')
    assert len(frame)==a['input_rows']==p['rows']==v['input_rows']==456548
    assert int(frame.num_orders.sum())==a['input_orders']==p['total_orders']==v['total_orders']==119557485
    assert sha(ROOT/'data/processed/train_prepared.csv')==a['prepared_sha256']==v['prepared_sha256']
    for file,value in manifest['source_result_hashes'].items():assert sha(ROOT/file)==value
    plots=manifest['figures']; axes=lambda name:plots[name]['render_evidence']['axes']
    weekly=frame.groupby('week',sort=True).num_orders.sum()
    assert weekly.to_dict()=={r['week']:r['orders'] for r in a['weekly']}
    np.testing.assert_allclose(axes('weekly')[0]['lines'][0]['y'],weekly.to_numpy()/1e6,rtol=0,atol=1e-15)
    changes=[100*(weekly.loc[w]-weekly.loc[w-1])/weekly.loc[w-1] for w in weekly.index if w-1 in weekly.index]
    np.testing.assert_allclose([r['height'] for r in axes('weekly')[1]['bars']],changes,rtol=1e-12,atol=1e-12)
    peak_week=int(weekly.idxmax()); trough_week=int(weekly.idxmin())
    assert f"week {peak_week} at {weekly.max():,} orders" in axes('weekly')[0]['titles'][1]
    assert f"Week {trough_week}: {weekly.min():,}" in axes('weekly')[0]['texts']
    assert axes('weekly')[0]['ylim'][0]==0
    category=frame.groupby('category').num_orders.sum().sort_values(ascending=False)
    assert list(category.index)==[r['key'] for r in a['categories']['ranking']]
    np.testing.assert_array_equal(category.to_numpy(),[r['orders'] for r in a['categories']['ranking']])
    np.testing.assert_allclose([r['height'] for r in axes('category')[0]['bars']],category.to_numpy()/1e6,rtol=0,atol=1e-14)
    cumulative=category.cumsum()/category.sum()*100
    np.testing.assert_allclose(axes('category')[1]['lines'][0]['y'],cumulative.to_numpy(),rtol=1e-12)
    n=int((cumulative<80).sum()+1); share=float(cumulative.iloc[n-1]); assert n==a['categories']['threshold_count']==5
    close(share,a['categories']['selected_share_pct']); assert f'{share:.2f}%' in axes('category')[0]['titles'][1]
    cw=frame.groupby(['center_id','week']).num_orders.sum(); totals=cw.groupby('center_id').sum(); avg=cw.groupby('center_id').mean()
    selected=a['centers'][:10]
    for row in selected:
        close(totals.loc[int(row['center_id'])],row['orders']);close(avg.loc[int(row['center_id'])],row['average_observed_week_orders'])
    np.testing.assert_allclose([r['width'] for r in axes('centers')[0]['bars']],[r['average_observed_week_orders'] for r in selected][::-1],rtol=1e-12)
    assert int(totals.idxmax())==int(selected[0]['center_id'])==13
    assert f"Center 13: {avg.loc[13]:,.0f} orders\nper observed week" in axes('centers')[0]['texts']
    checks={}
    for index,(flag,column) in enumerate([('email','emailer_for_promotion'),('homepage','homepage_featured')]):
        saved=p[flag]; g=frame.groupby(['center_id','meal_id',column]).num_orders.agg(['size','mean','sum'])
        count=g['size'].unstack(column,fill_value=0); eligible=count.index[(count[0]>=5)&(count[1]>=5)]
        filtered=g.loc[g.index.droplevel(-1).isin(eligible)]
        means=filtered['mean'].unstack(column).mean(); ns=filtered['size'].unstack(column).sum()
        close(means[0],saved['reference_context_mean']); close(means[1],saved['promoted_context_mean'])
        close(100*(means[1]-means[0])/means[0],saved['percentage_difference'])
        assert len(eligible)==saved['coverage']['eligible_series']
        assert int(ns[0])==saved['pooled_reference']['n'] and int(ns[1])==saved['pooled_promoted']['n']
        np.testing.assert_allclose([r['height'] for r in axes('promotion')[index]['bars']],[means[0],means[1]],rtol=1e-12)
        text='\n'.join(axes('promotion')[index]['texts'])
        for value in [f"{means[0]:.1f}",f"{means[1]:.1f}",f"{ns[0]:,}",f"{ns[1]:,}",f"{saved['percentage_difference']:+.1f}%",f"{len(eligible):,}"]:assert value in text,value
        outside_rows=len(frame)-int(ns.sum());outside_orders=int(frame.num_orders.sum()-filtered['sum'].sum())
        assert outside_rows==saved['coverage']['rows_outside_comparison'];assert outside_orders==saved['coverage']['orders_outside_comparison']
        checks[flag]={'contexts':len(eligible),'reference_n':int(ns[0]),'flagged_n':int(ns[1]),'reference_mean':float(means[0]),'flagged_mean':float(means[1]),'outside_comparison_rows':outside_rows,'outside_comparison_orders':outside_orders}
    discount=pd.Series([float((Decimal(str(base))-Decimal(str(checkout)))/Decimal(str(base))) for base,checkout in zip(frame.base_price,frame.checkout_price)],index=frame.index)
    rho=float(np.corrcoef(rankdata(discount),rankdata(frame.num_orders))[0,1]); close(rho,p['spearman']['rho'])
    assert f"{rho:.3f}" in axes('discount')[0]['texts'][0]
    assert int((discount<0).sum())==p['negative_discounts']==116101
    assert axes('discount')[0]['yscale']=='log' and axes('discount')[0]['xscale']=='linear'
    assert axes('discount')[0]['xlim'][0]<=discount.min()*100 and axes('discount')[0]['xlim'][1]>=discount.max()*100
    assert axes('discount')[0]['ylim'][0]<=frame.num_orders.min() and axes('discount')[0]['ylim'][1]>=frame.num_orders.max()
    assert manifest['density_observations']==len(frame)
    meals=frame.groupby('meal_id').num_orders.agg(['sum','mean','std']);cvs=meals['std']/meals['mean']
    cut_volume=float(meals['sum'].median());cut_cv=float(cvs.median());close(cut_volume,v['thresholds']['volume_orders']);close(cut_cv,v['thresholds']['cv'])
    for row in v['meals']:
        close(meals.loc[int(row['meal_id']),'sum'],row['orders']);close(cvs.loc[int(row['meal_id'])],row['cv'])
    assert int(((meals['sum']>=cut_volume)&(cvs>=cut_cv)).sum())==14
    for summary in v['segment_summary']:
        count=sum(r['segment']==summary['segment'] for r in v['meals']);assert count==summary['meals']
    pngs={}
    assert len(plots)==6
    for name,entry in plots.items():
        path=ROOT/entry['file'];b=path.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n'
        width,height=struct.unpack('>II',b[16:24]);assert width>=1800 and height>=1000
        assert sha(path)==entry['sha256'];pngs[name]={'path':entry['file'],'width':width,'height':height,'sha256':entry['sha256']}
        if 'render_evidence' in entry:
            e=entry['render_evidence'];assert e['figure_texts'] and all('Source:' in t or name=='promotion' for t in e['figure_texts'])
            assert any(ax['texts'] for ax in e['axes'])
    assert sha(ROOT/plots['inventory']['file'])==before['volume_figure_before']
    assert {q.name:sha(q) for q in (ROOT/'data/raw').glob('*.csv')}==before['raw_before']
    for file,value in before['protected_before'].items(): assert sha(ROOT/file)==value,file
    result={'status':'passed','method':'Independent pandas source aggregations, raw rank-correlation arithmetic and rendered Matplotlib artist values compared with validated Phase 6–9 outputs',
        'weekly_points':len(weekly),'weekly_change_bars':len(changes),'categories':len(category),'category_80pct_count':n,'category_80pct_share':share,'center_bars':len(selected),
        'promotion':checks,'spearman_rho':rho,'discount_density_rows':manifest['density_observations'],'negative_discounts_preserved':116101,
        'inventory_meals_checked':len(meals),'inventory_png':'unchanged','pngs':pngs,'raw_data':'all four hashes unchanged',
        'tests_source_notebooks_dependencies':'unchanged','full_suite_rerun':False,'phase13':'not started'}
    (ROOT/'docs/phase12_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['pngs','promotion']},indent=2))
if __name__=='__main__': main()
