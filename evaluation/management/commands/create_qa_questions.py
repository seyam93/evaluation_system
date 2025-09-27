from django.core.management.base import BaseCommand
from evaluation.models import EvaluationQuestion, EvaluationTemplate


class Command(BaseCommand):
    help = 'Create sample Q&A evaluation questions'

    def handle(self, *args, **options):
        # Sample Q&A questions
        qa_questions = [
            {
                'title': 'سؤال تقني - البرمجة',
                'description': 'اشرح الفرق بين البرمجة الإجرائية والبرمجة الكائنية مع إعطاء أمثلة عملية.',
                'question_type': 'qa',
                'max_score': 20,
                'weight': 2.0,
                'order': 1,
                'sample_answer': '''البرمجة الإجرائية:
- تعتمد على تسلسل الإجراءات والدوال
- البيانات والدوال منفصلة
- مثال: لغة C، Pascal

البرمجة الكائنية:
- تعتمد على الكائنات والفئات (Classes)
- البيانات والدوال مدمجة في كائن واحد
- تدعم المفاهيم: التغليف، الوراثة، تعدد الأشكال
- مثال: Java، C++, Python

مثال عملي:
- إجرائية: function calculateArea(length, width) { return length * width; }
- كائنية: class Rectangle { calculateArea() { return this.length * this.width; } }''',
                'answer_guidelines': '''معايير التقييم:
- فهم الفرق الأساسي (5 نقاط)
- ذكر المفاهيم الأساسية (5 نقاط)
- إعطاء أمثلة واضحة (5 نقاط)
- وضوح الشرح والتنظيم (5 نقاط)

تقييم ممتاز (18-20): شرح شامل ومفصل مع أمثلة متقدمة
تقييم جيد (14-17): شرح واضح مع أمثلة بسيطة
تقييم مقبول (10-13): فهم أساسي للمفاهيم
تقييم ضعيف (أقل من 10): فهم محدود أو خاطئ'''
            },
            {
                'title': 'سؤال إداري - إدارة المشاريع',
                'description': 'كيف تتعامل مع مشروع متأخر عن الجدول الزمني المحدد؟ اذكر الخطوات العملية.',
                'question_type': 'qa',
                'max_score': 15,
                'weight': 1.5,
                'order': 2,
                'sample_answer': '''خطوات التعامل مع تأخير المشروع:

1. تحليل أسباب التأخير:
- مراجعة المهام المكتملة والمتبقية
- تحديد العوائق والمشاكل
- تقييم الموارد المتاحة

2. إعادة تقييم الأولويات:
- تحديد المهام الأساسية vs الثانوية
- إمكانية التنفيذ المتوازي للمهام
- تقليل النطاق إذا لزم الأمر

3. وضع خطة تصحيحية:
- إعادة جدولة المهام
- تخصيص موارد إضافية
- تحديد معالم جديدة قابلة للتحقيق

4. التواصل مع أصحاب المصلحة:
- إبلاغهم بالوضع الحالي
- عرض الخيارات المتاحة
- الحصول على موافقة على الخطة الجديدة

5. المتابعة والمراقبة المكثفة:
- مراجعات يومية للتقدم
- حل العوائق فوراً
- تقييم مستمر للجدول الزمني''',
                'answer_guidelines': '''معايير التقييم:
- تحديد أسباب التأخير (3 نقاط)
- وضع خطة تصحيحية واضحة (4 نقاط)
- التواصل مع أصحاب المصلحة (3 نقاط)
- المتابعة والتحكم (3 نقاط)
- التطبيق العملي والواقعية (2 نقطة)

ممتاز (13-15): خطة شاملة ومتكاملة
جيد (10-12): خطة واضحة مع بعض التفاصيل
مقبول (7-9): فهم أساسي للمفاهيم
ضعيف (أقل من 7): إجابة غير مكتملة أو غير واضحة'''
            },
            {
                'title': 'سؤال تحليلي - حل المشاكل',
                'description': 'لديك قاعدة بيانات تحتوي على مليون سجل وتواجه مشكلة في بطء الاستعلامات. كيف تحلل وتحل هذه المشكلة؟',
                'question_type': 'qa',
                'max_score': 25,
                'weight': 2.5,
                'order': 3,
                'sample_answer': '''خطوات تحليل وحل مشكلة بطء قاعدة البيانات:

1. تشخيص المشكلة:
- مراقبة الاستعلامات البطيئة (Query Monitoring)
- فحص خطط التنفيذ (Execution Plans)
- تحليل استخدام الموارد (CPU, Memory, I/O)
- مراجعة logs قاعدة البيانات

2. تحليل الاستعلامات:
- تحديد الاستعلامات الأكثر استهلاكاً للوقت
- فحص WHERE clauses وJOINs
- تحليل ORDER BY وGROUP BY operations
- مراجعة subqueries والوظائف المستخدمة

3. تحسين البنية:
- إضافة أو تحسين الفهارس (Indexes)
- تحسين تصميم الجداول (Table Design)
- تطبيق التطبيع أو إلغاء التطبيع حسب الحاجة
- تقسيم الجداول الكبيرة (Partitioning)

4. تحسين الاستعلامات:
- إعادة كتابة الاستعلامات المعقدة
- استخدام EXISTS بدلاً من IN
- تجنب SELECT * واستخدام الحقول المطلوبة فقط
- استخدام LIMIT للنتائج الكبيرة

5. تحسين الأداء العام:
- زيادة ذاكرة التخزين المؤقت (Buffer Pool)
- تحسين إعدادات قاعدة البيانات
- استخدام Connection Pooling
- تطبيق التخزين المؤقت للنتائج (Result Caching)

6. الحلول المتقدمة:
- تطبيق Read Replicas للاستعلامات
- استخدام Database Sharding
- تنفيذ Data Warehousing للتقارير
- استخدام NoSQL للبيانات غير المنظمة''',
                'answer_guidelines': '''معايير التقييم:
- تشخيص المشكلة بطريقة منهجية (5 نقاط)
- تحليل الاستعلامات والفهارس (5 نقاط)
- اقتراح حلول تحسين مناسبة (5 نقاط)
- فهم تحسين الأداء العام (5 نقاط)
- معرفة الحلول المتقدمة (3 نقاط)
- التطبيق العملي والواقعية (2 نقطة)

ممتاز (22-25): حلول شاملة ومتقدمة مع فهم عميق
جيد جداً (18-21): حلول جيدة مع فهم واضح للمفاهيم
جيد (14-17): حلول أساسية مع بعض التفاصيل
مقبول (10-13): فهم محدود مع حلول بسيطة
ضعيف (أقل من 10): فهم غير كافٍ للمشكلة'''
            },
            {
                'title': 'سؤال سلوكي - العمل الجماعي',
                'description': 'أعط مثالاً عن موقف واجهت فيه تحدياً في العمل مع فريق متنوع الخلفيات. كيف تعاملت معه؟',
                'question_type': 'qa',
                'max_score': 15,
                'weight': 1.5,
                'order': 4,
                'sample_answer': '''مثال على التعامل مع فريق متنوع:

الموقف:
كنت أعمل في مشروع تطوير تطبيق مع فريق مكون من:
- مطورين من خلفيات تقنية مختلفة (Frontend, Backend, Mobile)
- مصمم UI/UX
- محلل أعمال
- فريق ضمان الجودة

التحدي:
- اختلاف في أساليب العمل والتواصل
- تباين في مستويات الخبرة التقنية
- اختلاف في فهم متطلبات المشروع
- صعوبة في التنسيق بين المهام

الحلول المطبقة:

1. وضع معايير تواصل موحدة:
- اجتماعات يومية قصيرة (Daily Stand-ups)
- استخدام أدوات تواصل مشتركة (Slack, Teams)
- توثيق واضح للقرارات والتغييرات

2. بناء الفهم المشترك:
- ورش عمل لشرح المفاهيم التقنية للفريق
- مشاركة المعرفة بين أعضاء الفريق
- وضع مسرد للمصطلحات التقنية

3. تحديد الأدوار والمسؤوليات:
- تعريف واضح لدور كل فرد
- تحديد نقاط التواصل لكل تخصص
- وضع مصفوفة المسؤوليات (RACI Matrix)

4. تشجيع التعاون:
- جلسات عصف ذهني مشتركة
- مراجعة الكود الجماعية (Code Reviews)
- تقديم المساعدة المتبادلة بين الأعضاء

النتيجة:
- تحسن كبير في التواصل والتعاون
- تسليم المشروع في الوقت المحدد
- رضا عالي من جميع أعضاء الفريق
- بناء علاقات مهنية قوية''',
                'answer_guidelines': '''معايير التقييم:
- وضوح وصف الموقف والتحدي (3 نقاط)
- الحلول المطبقة والاستراتيجيات (5 نقاط)
- مهارات التواصل والقيادة (3 نقاط)
- النتائج المحققة (2 نقطة)
- التعلم والتطوير الشخصي (2 نقطة)

ممتاز (13-15): مثال واضح مع حلول متقدمة ونتائج قابلة للقياس
جيد (10-12): مثال جيد مع حلول عملية
مقبول (7-9): مثال بسيط مع بعض الحلول
ضعيف (أقل من 7): مثال غير واضح أو حلول غير مناسبة'''
            },
        ]

        created_questions = []
        for question_data in qa_questions:
            question, created = EvaluationQuestion.objects.get_or_create(
                title=question_data['title'],
                defaults=question_data
            )
            if created:
                created_questions.append(question)
                self.stdout.write(
                    self.style.SUCCESS(f'Created Q&A question: {question.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Q&A question already exists: {question.title}')
                )

        # Create or update Q&A template
        template_name = 'قالب أسئلة السؤال والجواب'
        template, template_created = EvaluationTemplate.objects.get_or_create(
            name=template_name,
            defaults={
                'description': 'قالب يحتوي على أسئلة السؤال والجواب للتقييم التفاعلي'
            }
        )

        if template_created or not template.questions.filter(question_type='qa').exists():
            # Add all Q&A questions to the template
            qa_questions_qs = EvaluationQuestion.objects.filter(
                question_type='qa',
                title__in=[q['title'] for q in qa_questions]
            )
            template.questions.add(*qa_questions_qs)

            self.stdout.write(
                self.style.SUCCESS(f'Updated template: {template.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Template already has Q&A questions: {template.name}')
            )

        # Summary
        created_count = len(created_questions)
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully created {created_count} new Q&A questions!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nAll Q&A questions already exist.')
            )

        total_qa_questions = EvaluationQuestion.objects.filter(question_type='qa').count()
        self.stdout.write(
            self.style.SUCCESS(f'Total Q&A questions in system: {total_qa_questions}')
        )