# تدقيق التسليم النهائي — المرحلة 20

التاريخ: 2026-10-27. أُنجز التدقيق مع بندي قبول غير محسومين: التحقق من تاريخ Git والنشر، وتجربة التثبيت في بيئة نظيفة. لا يُعلن المشروع مكتمل القبول بالكامل.

نجحت الاختبارات الحالية **74/74** دون إخفاق أو خطأ أو تخطٍّ. طابقت جميع الإصدارات المثبتة requirements.txt، ونجح pip check. بقيت الملفات الخام الأربعة ومخرجات المرحلة 10 دون تغيير. لم يُعد تدريب النماذج أو تشغيل الدفاتر أو التحليلات.

الحالة «دليل سابق» تعني مراجعة نتيجة تنفيذ محفوظة، لا إعادة تنفيذ في المرحلة 20. لا يثبت فحص بنية ملف أو وجود مستند وحده صحة جميع نتائجه. تفاصيل الفحوص الحالية في [السجل الآلي](phase20_validation.json).

| المجال | بند الخطة | الحالة | الدليل والحدود |
| --- | --- | --- | --- |
| Repository | Correct repository structure. | دليل سابق وفحص الملفات | AGENTS.md; .github/instructions/project-rules.md; requirements.txt; current file/pin checks |
| Repository | `data/` ignored. | قاعدة موجودة؛ التتبع غير متحقق | .gitignore يحتوي /data/؛ تعذر git check-ignore لغياب المستودع. |
| Repository | No raw/private data committed. | غير قابل للتحقق | لا توجد .git؛ لم يُجرَ commit/push. لا CSV للمشروع خارج data/، ولا يثبت هذا تاريخ النشر. |
| Repository | `AGENTS.md` complete. | دليل سابق وفحص الملفات | AGENTS.md; .github/instructions/project-rules.md; requirements.txt; current file/pin checks |
| Repository | Rules complete. | دليل سابق وفحص الملفات | AGENTS.md; .github/instructions/project-rules.md; requirements.txt; current file/pin checks |
| Repository | Requirements reproducible. | دليل سابق وفحص الملفات | AGENTS.md; .github/instructions/project-rules.md; requirements.txt; current file/pin checks |
| Skills | Find Skills actually used. | دليل سابق وفحص الملفات | docs/find_skills.md; docs/skills_testing.md; current skill-file checks |
| Skills | Two appropriate existing skills selected and documented. | دليل سابق وفحص الملفات | docs/find_skills.md; docs/skills_testing.md; current skill-file checks |
| Skills | Two custom skills created. | دليل سابق وفحص الملفات | docs/find_skills.md; docs/skills_testing.md; current skill-file checks |
| Skills | Positive and negative tests documented for custom skills. | دليل سابق وفحص الملفات | docs/find_skills.md; docs/skills_testing.md; current skill-file checks |
| Skills | No false claims about skill usage. | دليل سابق وفحص الملفات | docs/find_skills.md; docs/skills_testing.md; current skill-file checks |
| Data | Three analytical tables joined correctly. | دليل سابق وفحص الملفات | docs/phase5_audit.json; docs/cleaning_decisions.md; current SHA-256 check |
| Data | Row counts validated. | دليل سابق وفحص الملفات | docs/phase5_audit.json; docs/cleaning_decisions.md; current SHA-256 check |
| Data | Total demand validated. | دليل سابق وفحص الملفات | docs/phase5_audit.json; docs/cleaning_decisions.md; current SHA-256 check |
| Data | Missing values checked. | دليل سابق وفحص الملفات | docs/phase5_audit.json; docs/cleaning_decisions.md; current SHA-256 check |
| Data | Duplicates checked. | دليل سابق وفحص الملفات | docs/phase5_audit.json; docs/cleaning_decisions.md; current SHA-256 check |
| Data | Pricing anomalies checked. | دليل سابق وفحص الملفات | docs/phase5_audit.json; docs/cleaning_decisions.md; current SHA-256 check |
| Data | Outliers investigated. | دليل سابق وفحص الملفات | docs/phase5_audit.json; docs/cleaning_decisions.md; current SHA-256 check |
| Data | Missing weeks investigated. | دليل سابق وفحص الملفات | docs/phase5_audit.json; docs/cleaning_decisions.md; current SHA-256 check |
| Data | Cleaning decisions documented. | دليل سابق وفحص الملفات | docs/phase5_audit.json; docs/cleaning_decisions.md; current SHA-256 check |
| Analysis | Weekly demand answered. | دليل سابق وفحص الملفات | Phase 6–9 saved outputs; notebooks/analysis.ipynb; 74 current tests |
| Analysis | 80% demand concentration answered. | دليل سابق وفحص الملفات | Phase 6–9 saved outputs; notebooks/analysis.ipynb; 74 current tests |
| Analysis | Center performance answered. | دليل سابق وفحص الملفات | Phase 6–9 saved outputs; notebooks/analysis.ipynb; 74 current tests |
| Analysis | Promotion effect answered. | دليل سابق وفحص الملفات | Phase 6–9 saved outputs; notebooks/analysis.ipynb; 74 current tests |
| Analysis | Homepage effect answered. | دليل سابق وفحص الملفات | Phase 6–9 saved outputs; notebooks/analysis.ipynb; 74 current tests |
| Analysis | Discount relationship answered. | دليل سابق وفحص الملفات | Phase 6–9 saved outputs; notebooks/analysis.ipynb; 74 current tests |
| Analysis | Volatility/inventory risk answered. | دليل سابق وفحص الملفات | Phase 6–9 saved outputs; notebooks/analysis.ipynb; 74 current tests |
| Statistics | Mann--Whitney implemented appropriately. | دليل سابق وفحص الملفات | docs/phase8_progress.md; docs/phase8_validation.json; tests/test_promotions.py |
| Statistics | Percentage differences reported. | دليل سابق وفحص الملفات | docs/phase8_progress.md; docs/phase8_validation.json; tests/test_promotions.py |
| Statistics | Spearman implemented. | دليل سابق وفحص الملفات | docs/phase8_progress.md; docs/phase8_validation.json; tests/test_promotions.py |
| Statistics | Promotion/discount overlap discussed. | دليل سابق وفحص الملفات | docs/phase8_progress.md; docs/phase8_validation.json; tests/test_promotions.py |
| Statistics | Statistical significance not confused with causation. | دليل سابق وفحص الملفات | docs/phase8_progress.md; docs/phase8_validation.json; tests/test_promotions.py |
| Machine Learning | Last 10 weeks used for chronological evaluation. | دليل سابق وفحص الملفات | docs/phase10_validation.json; docs/phase10_notebook_validation.json; saved predictions; current tests |
| Machine Learning | Previous-week baseline created. | دليل سابق وفحص الملفات | docs/phase10_validation.json; docs/phase10_notebook_validation.json; saved predictions; current tests |
| Machine Learning | Linear Regression evaluated. | دليل سابق وفحص الملفات | docs/phase10_validation.json; docs/phase10_notebook_validation.json; saved predictions; current tests |
| Machine Learning | Random Forest evaluated. | دليل سابق وفحص الملفات | docs/phase10_validation.json; docs/phase10_notebook_validation.json; saved predictions; current tests |
| Machine Learning | MAE calculated. | دليل سابق وفحص الملفات | docs/phase10_validation.json; docs/phase10_notebook_validation.json; saved predictions; current tests |
| Machine Learning | Leakage checked. | دليل سابق وفحص الملفات | docs/phase10_validation.json; docs/phase10_notebook_validation.json; saved predictions; current tests |
| Machine Learning | Best model selected honestly. | دليل سابق وفحص الملفات | docs/phase10_validation.json; docs/phase10_notebook_validation.json; saved predictions; current tests |
| Machine Learning | `test.csv` predictions generated. | دليل سابق وفحص الملفات | docs/phase10_validation.json; docs/phase10_notebook_validation.json; saved predictions; current tests |
| Machine Learning | Forecast business use explained. | دليل سابق وفحص الملفات | docs/phase10_validation.json; docs/phase10_notebook_validation.json; saved predictions; current tests |
| Testing | Data tests pass. | ناجح حاليًا | Phase 20 full suite: 74/74; docs/testing_report.md is historical |
| Testing | KPI tests pass. | ناجح حاليًا | Phase 20 full suite: 74/74; docs/testing_report.md is historical |
| Testing | Analysis-function tests pass. | ناجح حاليًا | Phase 20 full suite: 74/74; docs/testing_report.md is historical |
| Testing | ML tests pass. | ناجح حاليًا | Phase 20 full suite: 74/74; docs/testing_report.md is historical |
| Testing | Actual test results documented. | ناجح حاليًا | Phase 20 full suite: 74/74; docs/testing_report.md is historical |
| Visuals | At least 4 final figures. | دليل سابق وفحص الملفات | docs/phase12_validation.json; docs/phase19_validation.json; 7 PNG files |
| Visuals | Preferably 6--8 useful figures. | دليل سابق وفحص الملفات | docs/phase12_validation.json; docs/phase19_validation.json; 7 PNG files |
| Visuals | Conclusion-oriented titles. | دليل سابق وفحص الملفات | docs/phase12_validation.json; docs/phase19_validation.json; 7 PNG files |
| Visuals | Every chart has a concise interpretation. | دليل سابق وفحص الملفات | docs/phase12_validation.json; docs/phase19_validation.json; 7 PNG files |
| Visuals | PNG files saved under `reports/figures/`. | دليل سابق وفحص الملفات | docs/phase12_validation.json; docs/phase19_validation.json; 7 PNG files |
| Dashboard | Runs locally. | دليل سابق وفحص الملفات | docs/phase13_validation.json: 20 acceptance checks; current health status in JSON |
| Dashboard | Dynamic filters work. | دليل سابق وفحص الملفات | docs/phase13_validation.json: 20 acceptance checks; current health status in JSON |
| Dashboard | KPIs correct. | دليل سابق وفحص الملفات | docs/phase13_validation.json: 20 acceptance checks; current health status in JSON |
| Dashboard | Demand section works. | دليل سابق وفحص الملفات | docs/phase13_validation.json: 20 acceptance checks; current health status in JSON |
| Dashboard | Marketing section works. | دليل سابق وفحص الملفات | docs/phase13_validation.json: 20 acceptance checks; current health status in JSON |
| Dashboard | Inventory section works. | دليل سابق وفحص الملفات | docs/phase13_validation.json: 20 acceptance checks; current health status in JSON |
| Dashboard | ML section works. | دليل سابق وفحص الملفات | docs/phase13_validation.json: 20 acceptance checks; current health status in JSON |
| Reports | Client report uses non-technical language. | دليل سابق وفحص الملفات | docs/phase14_validation.json; docs/phase15_validation.json; Phase 19 independent checks |
| Reports | Executive summary starts with strongest result. | دليل سابق وفحص الملفات | docs/phase14_validation.json; docs/phase15_validation.json; Phase 19 independent checks |
| Reports | Every numerical claim is traceable. | دليل سابق وفحص الملفات | docs/phase14_validation.json; docs/phase15_validation.json; Phase 19 independent checks |
| Reports | At least 3 recommendations. | دليل سابق وفحص الملفات | docs/phase14_validation.json; docs/phase15_validation.json; Phase 19 independent checks |
| Reports | Every recommendation has evidence + KPI. | دليل سابق وفحص الملفات | docs/phase14_validation.json; docs/phase15_validation.json; Phase 19 independent checks |
| Reports | Limitations included. | دليل سابق وفحص الملفات | docs/phase14_validation.json; docs/phase15_validation.json; Phase 19 independent checks |
| Reports | Technical report documents methodology and tools. | دليل سابق وفحص الملفات | docs/phase14_validation.json; docs/phase15_validation.json; Phase 19 independent checks |
| README | Setup instructions tested. | جزئي | فُحصت البيئة الحالية والإصدارات وpip check؛ لم يُكرر تثبيت نظيف كامل أو تشغيل أوامر التدريب. |
| README | Top 3 findings added. | دليل سابق وفحص الملفات | README.md; pinned versions/pip check; documented historical validation |
| README | AI usage explained. | دليل سابق وفحص الملفات | README.md; pinned versions/pip check; documented historical validation |
| README | Dashboard instructions included. | دليل سابق وفحص الملفات | README.md; pinned versions/pip check; documented historical validation |
| README | ML results included. | دليل سابق وفحص الملفات | README.md; pinned versions/pip check; documented historical validation |
| README | Limitations included. | دليل سابق وفحص الملفات | README.md; pinned versions/pip check; documented historical validation |
| Presentation | Business problem included. | ناجح؛ استُكمل ملف التسليم | presentation/final_presentation.pptx; Phase 20 finalization receipt and 13-slide visual review |
| Presentation | Data quality included. | ناجح؛ استُكمل ملف التسليم | presentation/final_presentation.pptx; Phase 20 finalization receipt and 13-slide visual review |
| Presentation | Main findings included. | ناجح؛ استُكمل ملف التسليم | presentation/final_presentation.pptx; Phase 20 finalization receipt and 13-slide visual review |
| Presentation | Recommendations included. | ناجح؛ استُكمل ملف التسليم | presentation/final_presentation.pptx; Phase 20 finalization receipt and 13-slide visual review |
| Presentation | ML included. | ناجح؛ استُكمل ملف التسليم | presentation/final_presentation.pptx; Phase 20 finalization receipt and 13-slide visual review |
| Presentation | Limitations included. | ناجح؛ استُكمل ملف التسليم | presentation/final_presentation.pptx; Phase 20 finalization receipt and 13-slide visual review |
| Presentation | AI usage included. | ناجح؛ استُكمل ملف التسليم | presentation/final_presentation.pptx; Phase 20 finalization receipt and 13-slide visual review |
| Presentation | Uses final verified figures. | ناجح؛ استُكمل ملف التسليم | presentation/final_presentation.pptx; Phase 20 finalization receipt and 13-slide visual review |

تمت مراجعة بنود القائمة **79** كلٌ على حدة.

## إصلاح فجوة العرض

كان presentation/ يخلو من PowerPoint نهائي بعد المقاطعة. اعتُمدت المسودة العربية المحفوظة من المرحلة 18 دون إعادة إنشاء التحليل؛ اجتازت فحوص الحزمة والهندسة والخط والاستيراد والرسم القابل للتحرير. رُندرت الشرائح الـ13 عبر LibreOffice، وفُحصت بصريًا؛ عولجت مشكلة ترتيب العربية وقائمة المعرّفات في المسودة السابقة. بقيت الرسوم المعتمدة بلغتها الأصلية مع تفسير عربي. يذكر العرض نتيجة الاختبارات التاريخية 66؛ العدد الحالي 74 موثق هنا، فلا تُقرأ الأولى كحصيلة حديثة. فحص LibreOffice ليس ادعاء بفتح PowerPoint الأصلي. تحسين المرحلة 19 محفوظ في ملحقه المستقل.

## البنود المفتوحة

1. لا يوجد مستودع .git محلي: لا يمكن إثبات عدم وجود بيانات منشورة أو ملتزم بها تاريخيًا. لم يُنشأ مستودع أو يُنفذ commit/push ضمن التدقيق.
2. لم تُختبر عملية تثبيت نظيف من الصفر حفاظًا على نطاق التدقيق السريع؛ نجحت مطابقة جميع الإصدارات المثبتة وفحص ترابط التبعيات.

معايير القبول النهائية: التحليل والدفاتر واللوحة مدعومة بأدلة تنفيذ سابقة، الاختبارات الحالية ناجحة، مصادر الأرقام والحدود وتقسيم التنبؤ وخط الأساس موثقة، والتقارير والعرض جاهزة محليًا. معيار استبعاد الخام من النشر والتحقق الكامل من إعداد بيئة جديدة ما زالا غير محسومين. أُجري تدقيق كل بند دون ادعاء قبول نهائي كامل.


## معايير القبول الاثنا عشر

| المعيار | نتيجة التدقيق |
| --- | --- |
| 1. قابلية إعادة إنتاج التحليل | الشيفرة والمخرجات والتبعيات موجودة؛ تثبيت نظيف غير معاد. |
| 2. تنفيذ الدفاتر بلا أخطاء | دليل تشغيل سابق ناجح مع فحص المخرجات الحالية؛ لم تُعد في هذا التدقيق. |
| 3. الاختبارات الآلية | 74/74 ناجحة حاليًا. |
| 4. تتبع الأرقام إلى الشيفرة | أدلة المراحل 6–15 و19 وملاحظات مصادر العرض محفوظة؛ لم تُعد كل الحسابات. |
| 5. عدم نشر الخام | غير قابل للإثبات من نسخة بلا .git؛ بند مفتوح. |
| 6. صياغة الإحصاء | الارتباط والسببية وحدود المقارنة موضحة في التقارير. |
| 7. تحقق زمني وخط أساس | الأسابيع 136–145 وخط الأسبوع السابق وMAE موثقة؛ اختبارات التسرب ناجحة. |
| 8. عمل اللوحة | دليل 20 اختبار قبول سابق؛ فحص صحة الخادم الحالي 200. |
| 9. تقرير عميل مفهوم | تقرير عربي مع خلاصة وتوصيات وحدود ودليل تحقق المرحلة 14. |
| 10. تقرير تقني مفصل | المنهج والأدوات والمهارات والاختبارات والذكاء الاصطناعي وML موثقة؛ إضافة المرحلة 19 مستقلة التحقق. |
| 11. جاهزية العرض | PowerPoint من 13 شريحة مع تحقق بنيوي ومعاينة بصرية؛ لا ادعاء فتح PowerPoint الأصلي. |
| 12. تدقيق المتطلبات فرديًا | 79 بند قائمة مع حالة ودليل لكل بند، وهذه المعايير الاثنا عشر. |
