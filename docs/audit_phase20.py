from pathlib import Path
import json,hashlib,re,importlib.metadata as md,urllib.request
from zipfile import ZipFile
import xml.etree.ElementTree as ET
root=Path('.'); checks={}; issues=[]
base=json.loads(Path('data/processed/phase19/before.json').read_text(encoding='utf-8-sig'))
checks['protected_files_unchanged']=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in base.items())
assert checks['protected_files_unchanged']
checks['raw_files_match_inventory']=all(h in Path('docs/data_inventory.md').read_text(encoding='utf8') for p,h in base.items() if p.startswith('data/raw/'))
checks['git_metadata_present']=Path('.git').exists()
checks['ignore_data_rule_present']='/data/' in Path('.gitignore').read_text(encoding='utf-8-sig')
issues += ['Git tracking/history/publication could not be verified: no .git metadata in this workspace.', 'A clean environment installation was not repeated; installed pinned versions and pip check were verified.']
pins={}
for line in Path('requirements.txt').read_text(encoding='utf-8-sig').splitlines():
 if '==' in line and not line.startswith('#'):
  name,version=line.split('==');pins[name]={'required':version,'installed':md.version(name)}
assert all(x['required']==x['installed'] for x in pins.values())
checks['requirements_pins_match']=pins
checks['pip_check']='No broken requirements found.'
checks['tests']={'command':'.venv/Scripts/python.exe -m unittest discover -s tests -v','tests_run':74,'failures':0,'errors':0,'skipped':0,'suite_invocations':1,'runner_seconds':1.086,'evidence':'Executed during Phase 20; tool output retained in chat.'}
checks['notebooks']={}
for file in ['notebooks/analysis.ipynb','notebooks/machine_learning.ipynb']:
 nb=json.loads(Path(file).read_text(encoding='utf8')); cells=[c for c in nb['cells'] if c['cell_type']=='code']; errors=[o for c in cells for o in c.get('outputs',[]) if o.get('output_type')=='error']
 assert not errors and all(c.get('execution_count') is not None for c in cells)
 checks['notebooks'][file]={'code_cells':len(cells),'stored_errors':len(errors),'all_stored_executed':True,'rerun_in_phase20':False}
checks['historical_evidence']={}
for file in ['docs/phase10_notebook_validation.json','docs/phase9_notebook_validation.json','docs/phase12_validation.json','docs/phase13_validation.json','docs/phase14_validation.json','docs/phase15_validation.json','docs/phase19_validation.json']:
 obj=json.loads(Path(file).read_text(encoding='utf-8-sig'));assert obj['status'] in ['pass','passed'];checks['historical_evidence'][file]=obj['status']
try:
 with urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health',timeout=2) as response: checks['dashboard_health_current']=response.status
except Exception as e:checks['dashboard_health_current']='not running; historical Phase 13 AppTest 20/20 retained'
figures=list(Path('reports/figures').glob('*.png'));assert len(figures)>=4;checks['final_png_figures']=len(figures)
assert len(list(Path('.github/skills').glob('*/SKILL.md')))==2
checks['custom_skills_count']=2
checks['external_skills_available']=all(Path('.agents/skills',name,'SKILL.md').is_file() for name in ['exploratory-data-analysis','scikit-learn'])
receipt=json.loads(Path('data/processed/phase18/build/phase20b.final.validation.json').read_text(encoding='utf-8-sig'))
assert hashlib.sha256(Path('presentation/final_presentation.pptx').read_bytes()).hexdigest()==receipt['finalSha256']
assert receipt['packageIntegrity']['status']=='pass' and receipt['presentationLayout']['finding_count']==0 and receipt['firstPartyImport']['passed']
checks['presentation']={'path':'presentation/final_presentation.pptx','slides':13,'sha256':receipt['finalSha256'],'package_layout_font_import_and_native_chart_checks':'passed','visual_review':'all 13 final slides rendered by LibreOffice and inspected; Arabic direction and priority IDs readable','powerpoint_native_open_verified':False}
with ZipFile('presentation/final_presentation.pptx') as z:
 slides=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)];assert len(slides)==13
 alltext=' '.join(t.text or '' for n in slides for t in ET.fromstring(z.read(n)).iter() if t.tag.endswith('}t'))
 for value in ['119,557,485','116,101','4,296,545','32.71','2290','1754','1109','1971','1727']:assert value in alltext,value
 checks['presentation']['key_numbers_and_priority_ids_present']=True
unexpected=[]
for p in root.rglob('*.csv'):
 if not any(part in ['data','.venv','.agents','node_modules','.git'] for part in p.parts):unexpected.append(p.as_posix())
checks['csv_outside_data']=unexpected;assert not unexpected
Path('docs/phase20_validation.json').write_text(json.dumps({'phase':20,'audit_status':'executed_with_open_acceptance_items','fully_complete':False,'checks':checks,'open_items':issues},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Each Phase 20 checkbox is recorded separately, preserving the actual rubric wording.
plan=Path('FOOD_DEMAND_ANALYSIS_IMPLEMENTATION_PLAN.md').read_text(encoding='utf8').split('# Phase 20 --- Final QA and Submission Audit')[1].split('# Final Acceptance Criteria')[0]
evidence={'Repository':'AGENTS.md; .github/instructions/project-rules.md; requirements.txt; current file/pin checks', 'Skills':'docs/find_skills.md; docs/skills_testing.md; current skill-file checks', 'Data':'docs/phase5_audit.json; docs/cleaning_decisions.md; current SHA-256 check', 'Analysis':'Phase 6–9 saved outputs; notebooks/analysis.ipynb; 74 current tests', 'Statistics':'docs/phase8_progress.md; docs/phase8_validation.json; tests/test_promotions.py', 'Machine Learning':'docs/phase10_validation.json; docs/phase10_notebook_validation.json; saved predictions; current tests', 'Testing':'Phase 20 full suite: 74/74; docs/testing_report.md is historical', 'Visuals':'docs/phase12_validation.json; docs/phase19_validation.json; 7 PNG files', 'Dashboard':'docs/phase13_validation.json: 20 acceptance checks; current health status in JSON', 'Reports':'docs/phase14_validation.json; docs/phase15_validation.json; Phase 19 independent checks', 'README':'README.md; pinned versions/pip check; documented historical validation', 'Presentation':'presentation/final_presentation.pptx; Phase 20 finalization receipt and 13-slide visual review'}
text=['# تدقيق التسليم النهائي — المرحلة 20','', 'التاريخ: 2026-10-27. أُنجز التدقيق مع بندي قبول غير محسومين: التحقق من تاريخ Git والنشر، وتجربة التثبيت في بيئة نظيفة. لا يُعلن المشروع مكتمل القبول بالكامل.','', 'نجحت الاختبارات الحالية **74/74** دون إخفاق أو خطأ أو تخطٍّ. طابقت جميع الإصدارات المثبتة requirements.txt، ونجح pip check. بقيت الملفات الخام الأربعة ومخرجات المرحلة 10 دون تغيير. لم يُعد تدريب النماذج أو تشغيل الدفاتر أو التحليلات.','', 'الحالة «دليل سابق» تعني مراجعة نتيجة تنفيذ محفوظة، لا إعادة تنفيذ في المرحلة 20. لا يثبت فحص بنية ملف أو وجود مستند وحده صحة جميع نتائجه. تفاصيل الفحوص الحالية في [السجل الآلي](phase20_validation.json).','', '| المجال | بند الخطة | الحالة | الدليل والحدود |','| --- | --- | --- | --- |']
category='';count=0
for line in plan.splitlines():
 if line.startswith('## '):category=line[3:]
 if '[ ]' in line:
  item=line.split('[ ]',1)[1].strip(); status='دليل سابق وفحص الملفات';ev=evidence[category]
  if category=='Testing':status='ناجح حاليًا'
  if category=='Presentation':status='ناجح؛ استُكمل ملف التسليم'
  if item=='No raw/private data committed.':status='غير قابل للتحقق';ev='لا توجد .git؛ لم يُجرَ commit/push. لا CSV للمشروع خارج data/، ولا يثبت هذا تاريخ النشر.'
  if item=='`data/` ignored.':status='قاعدة موجودة؛ التتبع غير متحقق';ev='.gitignore يحتوي /data/؛ تعذر git check-ignore لغياب المستودع.'
  if item=='Setup instructions tested.':status='جزئي';ev='فُحصت البيئة الحالية والإصدارات وpip check؛ لم يُكرر تثبيت نظيف كامل أو تشغيل أوامر التدريب.'
  text.append(f'| {category} | {item} | {status} | {ev} |');count+=1
text += ['',f'تمت مراجعة بنود القائمة **{count}** كلٌ على حدة.','', '## إصلاح فجوة العرض','', 'كان presentation/ يخلو من PowerPoint نهائي بعد المقاطعة. اعتُمدت المسودة العربية المحفوظة من المرحلة 18 دون إعادة إنشاء التحليل؛ اجتازت فحوص الحزمة والهندسة والخط والاستيراد والرسم القابل للتحرير. رُندرت الشرائح الـ13 عبر LibreOffice، وفُحصت بصريًا؛ عولجت مشكلة ترتيب العربية وقائمة المعرّفات في المسودة السابقة. بقيت الرسوم المعتمدة بلغتها الأصلية مع تفسير عربي. يذكر العرض نتيجة الاختبارات التاريخية 66؛ العدد الحالي 74 موثق هنا، فلا تُقرأ الأولى كحصيلة حديثة. فحص LibreOffice ليس ادعاء بفتح PowerPoint الأصلي. تحسين المرحلة 19 محفوظ في ملحقه المستقل.','', '## البنود المفتوحة','', '1. لا يوجد مستودع .git محلي: لا يمكن إثبات عدم وجود بيانات منشورة أو ملتزم بها تاريخيًا. لم يُنشأ مستودع أو يُنفذ commit/push ضمن التدقيق.','2. لم تُختبر عملية تثبيت نظيف من الصفر حفاظًا على نطاق التدقيق السريع؛ نجحت مطابقة جميع الإصدارات المثبتة وفحص ترابط التبعيات.','', 'معايير القبول النهائية: التحليل والدفاتر واللوحة مدعومة بأدلة تنفيذ سابقة، الاختبارات الحالية ناجحة، مصادر الأرقام والحدود وتقسيم التنبؤ وخط الأساس موثقة، والتقارير والعرض جاهزة محليًا. معيار استبعاد الخام من النشر والتحقق الكامل من إعداد بيئة جديدة ما زالا غير محسومين. أُجري تدقيق كل بند دون ادعاء قبول نهائي كامل.']
Path('docs/final_audit.md').write_text('\n'.join(text)+'\n',encoding='utf8')
print('Audit checklist items:',count,'; current tests: 74 PASS; open acceptance items: 2; dashboard:',checks['dashboard_health_current'])


