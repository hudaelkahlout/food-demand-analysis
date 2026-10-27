"""Read-only dashboard adapters reusing validated notebook outputs."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from src.analysis.demand import analyze_records
ROOT=Path(__file__).resolve().parents[1]
SECTIONS=['Overview','Demand','Centers','Promotions & Pricing','Inventory Risk','Forecasting']

def read_json(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def load_bundle():
    required=['data/processed/train_prepared.csv','data/processed/phase6/eda_results.json','data/processed/phase7/kpi_results.json','data/processed/phase8/promotion_results.json','data/processed/phase9/inventory_segments.json','data/processed/phase10/results.json','data/processed/phase10/test_predictions.csv','data/processed/phase10/holdout_predictions.csv']
    missing=[p for p in required if not (ROOT/p).is_file()]
    if missing: raise FileNotFoundError('Missing prepared dashboard inputs. See dashboard/README.md: '+', '.join(missing))
    expected=read_json('docs/phase5_audit.json')['raw_sha256_before']
    if {name:sha(ROOT/'data/raw'/name) for name in expected}!=expected: raise ValueError('Raw inputs differ from the validated inventory.')
    a=read_json('data/processed/phase6/eda_results.json');k=read_json('data/processed/phase7/kpi_results.json');p=read_json('data/processed/phase8/promotion_results.json');v=read_json('data/processed/phase9/inventory_segments.json');ml=read_json('data/processed/phase10/results.json')
    if sha(ROOT/'data/processed/train_prepared.csv')!=a['prepared_sha256'] or k['prepared_sha256']!=a['prepared_sha256'] or v['prepared_sha256']!=a['prepared_sha256']:raise ValueError('Prepared input provenance mismatch.')
    phase12=read_json('docs/phase12_validation.json')
    for name,entry in phase12['pngs'].items():
        if sha(ROOT/entry['path'])!=entry['sha256']:raise ValueError('Final chart provenance mismatch: '+name)
    if sha(ROOT/'data/processed/phase7/kpi_results.json')!=v['phase7_kpi_sha256']:raise ValueError('CV source mismatch.')
    frame=pd.read_csv(ROOT/'data/processed/train_prepared.csv')
    if len(frame)!=k['observation_count'] or int(frame.num_orders.sum())!=k['total_orders']:raise ValueError('Historical population mismatch.')
    future=pd.read_csv(ROOT/'data/raw/test.csv');pred=pd.read_csv(ROOT/'data/processed/phase10/test_predictions.csv')
    if future.id.tolist()!=pred.id.tolist() or not np.isfinite(pred.num_orders).all() or (pred.num_orders<0).any():raise ValueError('Forecast alignment or values invalid.')
    future['forecast_orders']=pred.num_orders.to_numpy()
    for key,columns in [('meal_id',['category','cuisine']),('center_id',['center_type'])]:
        lookup=frame[[key]+columns].drop_duplicates()
        if lookup[key].duplicated().any():raise ValueError('Conflicting lookup metadata.')
        for column in columns:
            future[column]=future[key].map(lookup.set_index(key)[column])
            if future[column].isna().any():raise ValueError('Unmatched forecast metadata.')
    if len(future)!=ml['test_summary']['rows'] or future.id.tolist()!=pred.id.tolist():raise ValueError('Forecast metadata expansion.')
    holdout=pd.read_csv(ROOT/'data/processed/phase10/holdout_predictions.csv')
    if len(holdout)!=ml['holdout_rows']:raise ValueError('Holdout population mismatch.')
    return {'history':frame,'demand':a,'kpis':k,'promotions':p,'inventory':v,'ml':ml,'future':future,'holdout':holdout,
            'forecast_alignment':{'rows_before':len(pred),'rows_after':len(future),'unique_ids_before':int(pred.id.nunique()),'unique_ids_after':int(future.id.nunique()),'unmatched_metadata':0,'duplicate_expansion':0,'row_order_preserved':True,'actual_order_total':'not applicable'}}

def filter_history(frame,weeks,categories=(),meals=(),centers=(),types=(),cuisines=(),promotion='All'):
    mask=frame.week.between(*weeks)
    for col,values in [('category',categories),('meal_id',meals),('center_id',centers),('center_type',types),('cuisine',cuisines)]:
        if values: mask &= frame[col].isin(values)
    if promotion=='Email present':mask &= frame.emailer_for_promotion.eq(1)
    elif promotion=='Homepage featured':mask &= frame.homepage_featured.eq(1)
    elif promotion=='Neither':mask &= frame.emailer_for_promotion.eq(0)&frame.homepage_featured.eq(0)
    elif promotion=='Both':mask &= frame.emailer_for_promotion.eq(1)&frame.homepage_featured.eq(1)
    selected=frame.loc[mask].copy()
    audit={'source_rows':len(frame),'selected_rows':len(selected),'outside_selection_rows':int((~mask).sum()),'source_orders':int(frame.num_orders.sum()),'selected_orders':int(selected.num_orders.sum()),'outside_selection_orders':int(frame.loc[~mask,'num_orders'].sum()),'source_rows_deleted':0}
    return selected,audit

def summarize_selection(frame,full_result):
    if frame.empty:return None
    if len(frame)==full_result['input_rows'] and int(frame.num_orders.sum())==full_result['input_orders']:return full_result
    # Call exactly the Phase 6 implementation, including observed-week denominators.
    return analyze_records(frame.to_dict(orient='records'))

def forecast_selection(frame,center='All',meal='All',weeks=(146,155)):
    mask=frame.week.between(*weeks)
    if center!='All': mask &= frame.center_id.eq(center)
    if meal!='All': mask &= frame.meal_id.eq(meal)
    selected=frame.loc[mask].copy()
    return selected,{'source_rows':len(frame),'selected_rows':len(selected),'outside_selection_rows':int((~mask).sum()),'source_forecast_orders':float(frame.forecast_orders.sum()),'selected_forecast_orders':float(selected.forecast_orders.sum()),'outside_selection_forecast_orders':float(frame.loc[~mask,'forecast_orders'].sum()),'actual_orders':'unavailable','source_rows_deleted':0}
