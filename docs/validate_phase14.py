"""Phase 14 numerical/editorial validation using saved results only."""
from pathlib import Path
import hashlib
import json
import re
ROOT=Path(__file__).resolve().parents[1]

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    a=load('data/processed/phase6/eda_results.json');k=load('data/processed/phase7/kpi_results.json');p=load('data/processed/phase8/promotion_results.json');v=load('data/processed/phase9/inventory_segments.json');ml=load('data/processed/phase10/results.json')
    text=(ROOT/'reports/client_report.md').read_text(encoding='utf-8')
    claims=[]
    def claim(description,value,token,source):
        assert token in text,(description,token)
        claims.append({'claim':description,'source':source,'source_value':value,'display':token,'occurrences':text.count(token)})
    claim('Total observed orders',k['total_orders'],f"{k['total_orders']:,}",'phase7/kpi_results.json:total_orders')
    claim('Rounded average weekly demand',k['average_weekly_demand'],f"{k['average_weekly_demand']:,.0f}",'phase7/kpi_results.json:average_weekly_demand')
    for label,row in [('Peak',a['weekly_summary']['peak']),('Trough',a['weekly_summary']['trough'])]:
        claim(label+' orders',row['orders'],f"{row['orders']:,}",'phase6/eda_results.json:weekly_summary/'+label.lower() if label=='Peak' else 'phase6/eda_results.json:weekly_summary/trough')
        claim(label+' week',row['week'],str(row['week']),'phase6/eda_results.json:weekly_summary/'+('peak' if label=='Peak' else 'trough')+'/week')
    claim('Observed first week',a['weekly'][0]['week'],str(a['weekly'][0]['week']),'phase6/eda_results.json:weekly/first/week')
    claim('Observed last week',a['weekly'][-1]['week'],str(a['weekly'][-1]['week']),'phase6/eda_results.json:weekly/last/week')
    for key,label in [('categories','Category'),('meals','Meal')]:
        if key=='meals':claim(label+' threshold count',a[key]['threshold_count'],str(a[key]['threshold_count']),f'phase6/eda_results.json:{key}/threshold_count')
        claim(label+' demand share',a[key]['selected_share_pct'],f"{a[key]['selected_share_pct']:.2f}%",f'phase6/eda_results.json:{key}/selected_share_pct')
    category_map={'Beverages':'المشروبات','Rice Bowl':'أطباق الأرز','Sandwich':'الشطائر','Salad':'السلطات','Pizza':'البيتزا'}
    assert a['categories']['threshold_count']==5 and set(category_map)==set(a['categories']['selected_keys'])
    assert all(value in text for value in category_map.values())
    leader=max(a['centers'],key=lambda x:x['orders']);assert leader['center_id']=='13'
    claim('Leading center ID',leader['center_id'],leader['center_id'],'phase6/eda_results.json:centers/volume_leader/center_id')
    claim('Leading center orders',leader['orders'],f"{leader['orders']:,}",'phase6/eda_results.json:centers/volume_leader/orders')
    assert max(a['center_types'],key=lambda x:x['orders'])['center_type']=='TYPE_A'
    assert max(a['center_types'],key=lambda x:x['orders_per_observed_center_week'])['center_type']=='TYPE_B'
    assert 'فئة المراكز **«أ»** إجمالي' in text and 'الفئة **«ب»** متوسط الطلب' in text
    for flag in ['email','homepage']:
        claim(flag+' observed contrast',p[flag]['percentage_difference'],f"{p[flag]['percentage_difference']:.2f}%",f'phase8/promotion_results.json:{flag}/percentage_difference')
        claim(flag+' eligible contexts',p[flag]['coverage']['eligible_series'],f"{p[flag]['coverage']['eligible_series']:,}",f'phase8/promotion_results.json:{flag}/coverage/eligible_series')
    combined=p['combined']['contrasts']['both']
    claim('Both flags vs neither common-context contrast',combined['percentage_difference'],f"{combined['percentage_difference']:.2f}%",'phase8/promotion_results.json:combined/contrasts/both/percentage_difference')
    claim('Common four-state contexts',p['combined']['common_four_state_contexts'],f"{p['combined']['common_four_state_contexts']:,}",'phase8/promotion_results.json:combined/common_four_state_contexts')
    for state in ['0','1']:
        value=p['email']['overlap'][state]['discount']['mean']*100
        claim('Email flag '+state+' global mean signed discount percent',value,f'{value:.2f}%',f'phase8/promotion_results.json:email/overlap/{state}/discount/mean × 100')
    assert 0<p['spearman']['rho']<.2 and '**ضعيفة وموجبة**' in text
    high=v['segment_summary'][0];assert high['segment']=='high volume / high volatility'
    claim('Priority meals',len(v['priority_meal_ids']),str(len(v['priority_meal_ids'])),'phase9/inventory_segments.json:priority_meal_ids/length')
    claim('Priority demand share',high['demand_share_pct'],f"{high['demand_share_pct']:.2f}%",'phase9/inventory_segments.json:segment_summary/high-high/demand_share_pct')
    indexed={x['meal_id']:x for x in v['meals']}
    top=v['priority_meal_ids'][:5]
    table=re.findall(r'^\|\s*(\d{4})\s*\|\s*([\d,]+)\s*\|$',text,re.M)
    assert [meal for meal,orders in table]==top
    for meal,orders in table:
        assert int(orders.replace(',',''))==indexed[meal]['orders']
        claim('Priority meal ID',meal,meal,'phase9/inventory_segments.json:priority_meal_ids/top-five')
        claim('Priority meal '+meal+' orders',indexed[meal]['orders'],orders,'phase9/inventory_segments.json:meals/'+meal+'/orders')
    assert ml['winner']=='Random Forest'
    baseline=ml['metrics']['Previous-week baseline'];win=ml['metrics'][ml['winner']]
    claim('Baseline mean absolute forecast error',baseline['mae'],f"{baseline['mae']:.2f}",'phase10/results.json:metrics/Previous-week baseline/mae')
    claim('Selected model mean absolute forecast error',win['mae'],f"{win['mae']:.2f}",'phase10/results.json:metrics/Random Forest/mae')
    claim('Selected model MAE improvement percent',win['improvement_pct_vs_baseline'],f"{win['improvement_pct_vs_baseline']:.2f}%",'phase10/results.json:metrics/Random Forest/improvement_pct_vs_baseline')
    claim('Holdout start week',ml['holdout_weeks'][0],str(ml['holdout_weeks'][0]),'phase10/results.json:holdout_weeks/first')
    # Exhaustive displayed numeral check, including repeated occurrences.
    tokens=re.findall(r'(?<![\w])\d[\d,]*(?:\.\d+)?%?',text)
    allowed={row['display'] for row in claims}
    assert not set(tokens)-allowed,(set(tokens)-allowed)
    for row in claims:row['occurrences']=tokens.count(row['display'])
    headings=re.findall(r'^## (.+)$',text,re.M)
    expected=['الملخص التنفيذي','المشكلة التجارية','نظرة عامة على الطلب','أين يتركّز الطلب؟','مراكز التوزيع','الترويج والتسعير','مخاطر تخطيط المخزون','التنبؤ بالطلب','التوصيات','حدود النتائج','الخلاصة الإدارية']
    assert headings==expected
    executive=text.split('## الملخص التنفيذي\n',1)[1].split('\n## ',1)[0]
    assert len([line for line in executive.splitlines() if line.startswith('- ')])==4
    recommendation=text.split('## التوصيات\n',1)[1].split('\n## ',1)[0]
    assert len(re.findall(r'^\| \*\*',recommendation,re.M))==4
    assert all(word in recommendation for word in ['القرار والإجراء','الدليل الداعم','السبب التجاري','مؤشر المتابعة'])
    links=re.findall(r'(?<!!)\[([^]]+)\]\(([^)]+)\)',text)
    final=load('docs/phase12_validation.json');registered={entry['path']:entry['sha256'] for entry in final['pngs'].values()}
    assert len(links)==6 and text.count('**ما ينبغي للإدارة ملاحظته:**')==6
    figures=[]
    for label,target in links:
        path=ROOT/'reports'/target;relative=str(path.relative_to(ROOT)).replace('\\','/')
        assert relative in registered and sha(path)==registered[relative]
        figures.append(relative)
    visible=re.sub(r'\[([^]]+)\]\([^)]+\)',r'\1',text)
    assert not re.search(r'[A-Za-z]',visible),'Visible English text in Arabic report'
    assert '```' not in text
    for phrase in ['العملة غير محددة','مؤشر تقريبي للإيرادات','لا تقابل تواريخ تقويمية','لا تثبت','مهل توريد','لم يُفترض','عدم يقين','كميات الهدر']:
        assert phrase in text,phrase
    for phase in [6,7,8,9,10]:assert load(f'docs/phase{phase}_validation.json')['status']=='passed'
    snapshot=ROOT/'data/processed/phase14/before.json'
    if snapshot.exists():
        before=load('data/processed/phase14/before.json')
        for path,value in before.items():assert sha(ROOT/path)==value,path
    raw={path.name:sha(path) for path in (ROOT/'data/raw').glob('*.csv')};assert raw==load('docs/phase5_audit.json')['raw_sha256_before']
    assert not (ROOT/'reports/technical_report.md').exists()
    result={'status':'passed','report':'reports/client_report.md','report_sha256':sha(ROOT/'reports/client_report.md'),
        'sections':headings,'executive_statements':4,'recommendations':4,'chart_references':figures,
        'validated_source_claims':len(claims),'numeric_occurrences_checked':len(tokens),'numerical_claim_map':claims,
        'arabic_category_labels':category_map,'center_type_translation':{'TYPE_A':'أ','TYPE_B':'ب'},
        'visible_language':'Arabic only; image targets use existing filenames and charts are linked rather than embedded',
        'weak_positive_discount_relationship':'matches saved Phase 8 rho without adding statistical jargon to report',
        'winning_model':'Random Forest; expressed as selected best forecast in client prose',
        'raw_sha256_after':raw,'existing_data_code_tests_notebooks_forecasts_figures':'unchanged',
        'expensive_analysis_rerun':False,'full_suite_rerun':False,'technical_report_created':False,'phase15':'not started'}
    (ROOT/'docs/phase14_validation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in result.items() if key not in ['numerical_claim_map','arabic_category_labels','raw_sha256_after']},indent=2,ensure_ascii=False))
if __name__=='__main__':main()
