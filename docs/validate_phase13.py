"""Focused dashboard acceptance and data consistency checks; no model fitting."""
from pathlib import Path
import hashlib
import io
import json
import math
import urllib.request
import pandas as pd
import streamlit
from streamlit.testing.v1 import AppTest
from dashboard.data import load_bundle,filter_history,summarize_selection,forecast_selection,SECTIONS
ROOT=Path(__file__).resolve().parents[1]

def main():
    snapshot=ROOT/'data/processed/phase13/before.json'
    if not snapshot.exists():
        snapshot.parent.mkdir(parents=True,exist_ok=True)
        raw={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data/raw').glob('*.csv')}
        assert raw==json.loads((ROOT/'docs/phase5_audit.json').read_text())['raw_sha256_before']
        protected=list((ROOT/'src').rglob('*.py'))+list((ROOT/'tests').glob('*.py'))+list((ROOT/'notebooks').glob('*.ipynb'))+list((ROOT/'reports/figures').glob('*.png'))+list((ROOT/'data/processed/phase10').glob('*'))
        snapshot.write_text(json.dumps({'raw':raw,'protected':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected if p.is_file()}},indent=2))
    b=load_bundle();results=[]
    app=AppTest.from_file(str(ROOT/'dashboard/app.py'),default_timeout=120).run()
    def okay(case):
        assert not app.exception,[e.message for e in app.exception]
        results.append(case)
    okay('Overview renders')
    actual={m.label:m.value for m in app.metric};k=b['kpis']
    assert actual['Total orders']==f"{k['total_orders']:,}"
    assert actual['Average weekly demand']==f"{k['average_weekly_demand']:,.0f}"
    assert actual['Revenue proxy']==f"{float(k['revenue_proxy'])/1e9:.2f} billion"
    assert actual['Mean signed discount']==f"{k['discount_mean_rate']:.2%}"
    assert actual['Email promotion share']==f"{k['email_promotion_share']:.2%}"
    assert actual['Homepage feature share']==f"{k['homepage_feature_share']:.2%}"
    results.append('All six displayed KPIs match Phase 7')
    for section in SECTIONS[1:]:
        app.radio(key='section').set_value(section).run();okay(section+' renders')
        if section=='Inventory Risk':
            table=app.dataframe[0].value;assert len(table)==14
            indexed={row['meal_id']:row for row in b['inventory']['meals']}
            assert table['Meal ID'].tolist()==b['inventory']['priority_meal_ids']
            for row in table.to_dict('records'):
                source=indexed[row['Meal ID']];assert row['Observed orders']==source['orders'] and row['CV']==source['cv']
            results.append('All 14 priority rows, volume ordering and CVs match Phase 9')
        if section=='Forecasting':
            assert any('32.71%' in x.value and 'Random Forest' in x.value for x in app.success)
            comp=app.dataframe[0].value
            for row in comp.to_dict('records'):
                assert row['MAE (orders)']==b['ml']['metrics'][row['Model']]['mae']
            assert len(app.get('download_button'))==1
            results.append('Model MAEs, winner, 32.71% improvement and download widget match Phase 10')
    app.radio(key='section').set_value('Demand').run()
    app.multiselect(key='hist_categories').set_value(['Beverages']);app.multiselect(key='hist_centers').set_value([13]);app.slider(key='hist_weeks').set_value((1,10));app.run();okay('Demand filters change selected view')
    selected,audit=filter_history(b['history'],(1,10),categories=['Beverages'],centers=[13])
    source=b['history'];independent=source.loc[source.week.between(1,10)&source.category.eq('Beverages')&source.center_id.eq(13)]
    assert selected.id.tolist()==independent.id.tolist() and len(selected)>0
    demand=summarize_selection(selected,b['demand']);weekly=independent.groupby('week').num_orders.sum()
    assert {r['week']:r['orders'] for r in demand['weekly']}==weekly.to_dict()
    assert int(app.dataframe[0].value.Orders.sum())==int(independent.num_orders.sum())
    results.append('Filtered results reuse Phase 6 function and agree with independent source group totals')
    app.radio(key='section').set_value('Centers').run();okay('Historical filters persist to Centers')
    app.radio(key='center_measure').set_value('Orders per observed week').run();okay('Center ranking measure switches')
    app.button[0].click().run();assert app.slider(key='hist_weeks').value==(1,145) and not app.multiselect(key='hist_categories').value;okay('Reset restores full historical scope')
    # Exercise the other controls together, with a nonempty source-derived combination.
    example=source.loc[(source.emailer_for_promotion==1)&(source.homepage_featured==1)].iloc[0]
    app.multiselect(key='hist_meals').set_value([int(example.meal_id)]);app.multiselect(key='hist_types').set_value([example.center_type]);app.multiselect(key='hist_cuisines').set_value([example.cuisine]);app.selectbox(key='hist_promotion').set_value('Both');app.run();okay('Meal, center-type, cuisine and promotion filters operate together')
    choice,extra=filter_history(source,(1,145),meals=[int(example.meal_id)],types=[example.center_type],cuisines=[example.cuisine],promotion='Both')
    assert len(choice)>0 and (choice.emailer_for_promotion==1).all() and (choice.homepage_featured==1).all()
    app.button[0].click().run();app.multiselect(key='hist_centers').set_value([13]);app.multiselect(key='hist_types').set_value(['TYPE_A']);app.run();okay('Empty historical selection handled without exception')
    assert any('No recorded observations' in x.value for x in app.info)
    app.radio(key='section').set_value('Inventory Risk').run();okay('Historical filters do not alter fixed inventory cohort');assert len(app.dataframe[0].value)==14
    app.radio(key='section').set_value('Forecasting').run()
    app.selectbox(key='forecast_center').set_value(13);app.selectbox(key='forecast_meal').set_value(2290);app.slider(key='forecast_weeks').set_value((146,148));app.run();okay('Forecast center, meal and horizon controls operate independently')
    future,faudit=forecast_selection(b['future'],13,2290,(146,148));assert len(future)==3
    displayed=app.dataframe[-1].value;assert displayed['Week'].tolist()==future.week.tolist()
    assert displayed['Forecast orders'].tolist()==future.forecast_orders.tolist()
    output=future[['id','week','center_id','meal_id','category','forecast_orders']].to_csv(index=False)
    restored=pd.read_csv(io.StringIO(output));assert restored.id.tolist()==future.id.tolist()
    assert all(math.isfinite(x) and x>=0 for x in restored.forecast_orders)
    results.append('Filtered forecast preview/export preserves row order and saved prediction values')
    pairs=set(zip(b['future'].center_id,b['future'].meal_id));missing=next((c,m) for c in sorted(b['future'].center_id.unique()) for m in sorted(b['future'].meal_id.unique()) if (c,m) not in pairs)
    app.selectbox(key='forecast_center').set_value(int(missing[0]));app.selectbox(key='forecast_meal').set_value(int(missing[1]));app.slider(key='forecast_weeks').set_value((146,155));app.run();okay('Empty forecast selection handled without exception')
    assert any('No forecast rows' in x.value for x in app.info)
    for log in [audit,extra]:
        assert log['source_rows']==log['selected_rows']+log['outside_selection_rows']
        assert log['source_orders']==log['selected_orders']+log['outside_selection_orders']
    assert faudit['source_rows']==faudit['selected_rows']+faudit['outside_selection_rows']
    assert math.isclose(faudit['source_forecast_orders'],faudit['selected_forecast_orders']+faudit['outside_selection_forecast_orders'],rel_tol=1e-12)
    health={}
    for route in ['/_stcore/health','/']:
        with urllib.request.urlopen('http://127.0.0.1:8501'+route,timeout=10) as response:
            assert response.status==200;health[route]=response.status
    before=json.loads((ROOT/'data/processed/phase13/before.json').read_text())
    raw={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data/raw').glob('*.csv')};assert raw==before['raw']
    for name,value in before['protected'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value,name
    result={'status':'passed','streamlit_version':streamlit.__version__,'sections':SECTIONS,'acceptance_checks':results,'acceptance_check_count':len(results),
            'http':health,'historical_filter_example':audit,'forecast_filter_example':faudit,'forecast_metadata_alignment':b['forecast_alignment'],
            'raw_sha256_before':before['raw'],'raw_sha256_after':raw,'existing_source_tests_notebooks_figures_forecasts':'unchanged',
            'model_refitting':False,'expensive_statistical_analysis_rerun':False,'full_suite_rerun':False,'phase14':'not started'}
    (ROOT/'docs/phase13_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
