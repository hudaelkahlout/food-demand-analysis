"""Bounded Phase 15 report audit against saved evidence and source text."""
from pathlib import Path
import ast
import hashlib
import json
import re
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    text=(ROOT/'reports/technical_report.md').read_text(encoding='utf-8')
    a=load('data/processed/phase6/eda_results.json');k=load('data/processed/phase7/kpi_results.json');p=load('data/processed/phase8/promotion_results.json');v=load('data/processed/phase9/inventory_segments.json');ml=load('data/processed/phase10/results.json');audit=load('docs/phase5_audit.json');tests=load('docs/phase11_validation.json');ui=load('docs/phase13_validation.json')
    clean=re.sub(r'```.*?```','',text,flags=re.S);clean=re.sub(r'`[^`]+`','',clean);clean=re.sub(r'\[([^]]+)\]\([^)]+\)',r'\1',clean)
    tokens=re.findall(r'(?<![\w])\d[\d,]*(?:\.\d+)?%?',clean)
    claims=[]
    def add(value,fmt,source):
        displayed=format(value,fmt)
        assert displayed in tokens,(source,displayed)
        claims.append({'source':source,'value':value,'display':displayed,'occurrences':tokens.count(displayed)})
    for name,row in audit['input_audits'].items():
        add(row['rows'],',',f'phase5/input_audits/{name}/rows');add(row['columns'],'d',f'phase5/input_audits/{name}/columns')
    for value,source in [(1,'phase6/weekly/first/week'),(145,'phase6/weekly/last/week'),(146,'phase10/test_summary/weeks/first'),(155,'phase10/test_summary/weeks/last')]:
        actual={'phase6/weekly/first/week':a['weekly'][0]['week'],'phase6/weekly/last/week':a['weekly'][-1]['week'],'phase10/test_summary/weeks/first':ml['test_summary']['weeks'][0],'phase10/test_summary/weeks/last':ml['test_summary']['weeks'][1]}[source]
        assert actual==value;add(actual,'d',source)
    add(k['total_orders'],',','phase7/total_orders');add(k['average_weekly_demand'],',.0f','phase7/average_weekly_demand');add(k['average_weekly_demand'],',.2f','phase7/average_weekly_demand');add(float(k['revenue_proxy']),',.2f','phase7/revenue_proxy')
    for field in ['discount_mean_rate','email_promotion_share','homepage_feature_share']:add(k[field],'.2%',f'phase7/{field}')
    add(audit['quality']['pricing']['checkout_above_base_rows'],',','phase5/quality/pricing/checkout_above_base_rows');add(audit['quality']['pricing']['positive_difference_distribution']['median'],'.2f','phase5/quality/pricing/difference/median')
    for field in ['global_iqr_outlier_rows','within_series_iqr_outlier_rows']:add(audit['quality']['orders'][field],',','phase5/quality/orders/'+field)
    add(audit['quality']['orders']['global_iqr_fences'][1],'.0f','phase5/quality/orders/upper_fence');add(audit['quality']['orders']['distribution']['max'],',','phase5/quality/orders/max')
    coverage=audit['quality']['weeks']['center_meal_level']
    for field in ['absent_slots_within_observed_groups','observed_groups','internal_absent_slots','never_observed_pairs_in_center_meal_cartesian_product']:add(coverage[field],',','phase5/quality/weeks/'+field)
    for key in ['peak','trough']:
        add(a['weekly_summary'][key]['week'],'d','phase6/weekly_summary/'+key+'/week');add(a['weekly_summary'][key]['orders'],',','phase6/weekly_summary/'+key+'/orders')
    for key in ['categories','meals']:add(a[key]['selected_share_pct']/100,'.2%','phase6/'+key+'/selected_share_pct')
    add(a['meals']['threshold_count'],'d','phase6/meals/threshold_count')
    assert a['categories']['threshold_count']==5
    lead=max(a['centers'],key=lambda r:r['orders']);add(int(lead['center_id']),'d','phase6/center_leader/id');add(lead['orders'],',','phase6/center_leader/orders')
    assert max(a['center_types'],key=lambda r:r['orders'])['center_type']=='TYPE_A'
    assert max(a['center_types'],key=lambda r:r['orders_per_observed_center_week'])['center_type']=='TYPE_B'
    assert p['design']['minimum_per_state']==5;add(p['design']['minimum_per_state'],'d','phase8/design/minimum_per_state')
    assert 'len(common)>=30' in (ROOT/'src/statistics/promotions.py').read_text();add(30,'d','src/statistics/promotions.py:common-context lower bound')
    for name,r in [('email',p['email']),('homepage',p['homepage'])]+list(p['combined']['contrasts'].items()):
        for field,fmt,value in [('contexts',',',r['coverage']['eligible_series']),('flagged_n',',',r['pooled_promoted']['n']),('reference_n',',',r['pooled_reference']['n']),('difference_orders','.2f',r['difference_orders']),('percentage_difference','.2%',r['percentage_difference']/100)]:add(value,fmt,'phase8/'+name+'/'+field)
    for flag in ['email','homepage']:
        add(p[flag]['mann_whitney_pooled_reference']['u'],',.1f','phase8/'+flag+'/U')
        for state in ['0','1']:add(p[flag]['overlap'][state]['discount']['mean'],'.2%','phase8/'+flag+'/overlap/'+state+'/discount/mean')
        primary=next(r for r in p[flag]['uncertainty']['sensitivity'] if r['block_weeks']==8)
        for i,value in enumerate(primary['difference_ci95']):add(value,'.2f','phase8/'+flag+'/8-week interval/'+str(i))
        assert all(part['family99_excludes_zero'] for part in p[flag]['uncertainty']['sensitivity'])
    assert all(part['family99_excludes_zero'] for r in p['combined']['contrasts'].values() for part in r['uncertainty']['sensitivity'])
    add(p['design']['bootstrap_repetitions'],',','phase8/design/bootstrap_repetitions')
    assert f"`{p['design']['bootstrap_seed']}`" in text
    for value in p['design']['block_lengths']:add(value,'d','phase8/design/block_lengths')
    add(p['design']['family_intervals'],'.0%','phase8/design/family_intervals')
    assert '[.025,.975]' in (ROOT/'src/statistics/promotions.py').read_text();add(0.95,'.0%','src/statistics/promotions.py:quantile interval')
    add(p['spearman']['rho'],'.8f','phase8/spearman/rho');add(p['spearman']['within_context']['eligible_contexts'],',','phase8/spearman/within_context/count');add(p['spearman']['within_context']['mean_rho_equal_context'],'.8f','phase8/spearman/within_context/mean')
    add(v['thresholds']['volume_orders'],',.0f','phase9/thresholds/volume_orders');add(v['thresholds']['cv'],'.8f','phase9/thresholds/cv')
    for segment in v['segment_summary']:add(segment['meals'],'d','phase9/segment_summary/'+segment['segment'])
    add(v['segment_summary'][0]['demand_share_pct']/100,'.2%','phase9/high-high/share')
    for field in ['fit_rows','holdout_rows']:add(ml[field],',','phase10/'+field)
    for value in ml['fit_weeks']+ml['holdout_weeks']:add(value,'d','phase10/fit_and_holdout_weeks')
    add(ml['fallback_fit_median'],'.0f','phase10/fallback_fit_median')
    for model,row in ml['metrics'].items():
        add(row['mae'],'.3f','phase10/metrics/'+model+'/mae')
        if model!='Previous-week baseline':add(row['improvement_pct_vs_baseline']/100,'.2%','phase10/metrics/'+model+'/improvement')
    add(ml['metrics']['Linear Regression']['negative_predictions_clipped'],',','phase10/metrics/linear/clipped')
    add(tests['tests_run'],'d','phase11/tests_run')
    for file,count in tests['test_counts_by_file'].items():add(count,'d','phase11/test_counts/'+file)
    assert tests['failures']==tests['errors']==tests['skipped']==0
    for phase in [9,10]:add(load(f'docs/phase{phase}_notebook_validation.json')['code_cells_executed'],'d',f'phase{phase}/executed_notebook_cells')
    add(ui['acceptance_check_count'],'d','phase13/acceptance_check_count')
    assert set(ui['http'].values())=={200}
    trigger=load('docs/phase4_trigger_observations.json');assert len(trigger['cases'])==4
    assert '4,096' in (ROOT/'docs/cleaning_decisions.md').read_text(encoding='utf-8');add(4096,',','docs/cleaning_decisions.md:EDA sensitivity sample')
    allowed={r['display'] for r in claims};assert not set(tokens)-allowed,set(tokens)-allowed
    headings=re.findall(r'^## (.+)$',text,re.M);assert len(headings)==15
    assert '<div' not in text and 'dir=' not in text
    for label,target in re.findall(r'\[([^]]+)\]\(([^)]+)\)',text):
        if '://' not in target:assert (ROOT/'reports'/target.split('#')[0]).exists(),target
    figures=re.findall(r'\]\((figures/[^)]+)\)',text);assert len(figures)==6
    expected=load('docs/phase12_validation.json')['pngs']
    for path in figures:assert sha(ROOT/'reports'/path)==next(r['sha256'] for r in expected.values() if r['path']=='reports/'+path)
    # Match concrete methodological claims to the actual source, without fitting or inference.
    code=(ROOT/'src/machine_learning/forecast.py').read_text();tree=ast.parse(code)
    cfg=next(node.value for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='RF_CONFIG' for target in node.targets))
    parsed={kw.arg:ast.literal_eval(kw.value) for kw in cfg.keywords};assert parsed==ml['random_forest_configuration']
    for name,value in parsed.items():assert f'{name}={value}' in text,(name,value)
    methods={
      'fixed_origin_recursion':"drop(columns=['num_orders'],errors='ignore')" in code and 'history[(week,c,m)] = float(y)' in code and 'لا تُستهلك أهداف الفترة المحجوبة' in text,
      'exact_prior_week_window':'for k in range(1,5)' in code and 'الأسابيع الأربعة السابقة' in text,
      'train_only_pipeline':"model.fit(x,fit.num_orders)" in code and "SimpleImputer(strategy='median',add_indicator=True)" in code and 'نافذة التعلم وحدها' in text,
      'unknown_category_handling':"OneHotEncoder(handle_unknown='ignore')" in code,
      'prediction_clipping':'np.maximum(values,0)' in code and 'قبل القياس أيضًا' in text,
      'model_discount_floating':"np.divide(base-rows.checkout_price" in code and 'حساب التخفيض للنموذج عائم' in text,
      'pooled_U_not_paired':'ليس اختبارًا مزدوجًا أو طبقيًا' in text,
      'reference_p_not_confirmatory':'لا دليل دلالة تأكيدي' in text,
      'first_order_week_blocks':'ليس سحبًا كاملًا' in text,
      'manual_skill_routing':'لا إثبات تنشيط تلقائي' in text,
      'previous_validation_not_rerun':'لم تُعد الاختبارات أو الدفاتر' in text}
    assert all(methods.values()),methods
    manifest=load('docs/phase3_skill_sources.json')
    for file in manifest['files']:
        if file['path'].startswith('skills/'):assert sha(ROOT/'.agents'/file['path'])==file['sha256']
    before=load('data/processed/phase15/before.json')
    for file,value in before.items():assert sha(ROOT/file)==value,file
    raw={f.name:sha(f) for f in (ROOT/'data/raw').glob('*.csv')};assert raw==audit['raw_sha256_before']
    result={'status':'passed','report':'reports/technical_report.md','report_sha256':sha(ROOT/'reports/technical_report.md'),
        'sections':headings,'source_claim_entries':len(claims),'numeric_occurrences_checked':len(tokens),'numeric_source_map':claims,
        'methodology_checks':methods,'random_forest_config_verified':parsed,'final_figures':figures,'skill_source_files':'unchanged',
        'raw_sha256':raw,'prior_code_tests_notebooks_dashboard_client_report_outputs':'unchanged','analysis_rerun':False,'full_suite_rerun':False,'phase16':'not started'}
    (ROOT/'docs/phase15_validation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['numeric_source_map','raw_sha256']},indent=2,ensure_ascii=False))
if __name__=='__main__':main()
