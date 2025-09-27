from django.core.management.base import BaseCommand
from evaluation.models import EvaluationQuestion


class Command(BaseCommand):
    help = 'Create sample questions for all 3 types (MCQ, True/False, Q&A)'

    def handle(self, *args, **options):
        # Sample questions for each type
        questions_data = [
            # MCQ Questions
            {
                'question_text': 'ما هي أفضل طريقة لتحسين أداء قاعدة البيانات؟',
                'question_type': 'mcq',
                'option_a': 'إضافة فهارس للجداول',
                'option_b': 'زيادة حجم الذاكرة',
                'option_c': 'تقسيم الجداول الكبيرة',
                'option_d': 'جميع ما سبق',
                'correct_answer': 'D'
            },
            {
                'question_text': 'أي من هذه اللغات تُستخدم في تطوير المواقع؟',
                'question_type': 'mcq',
                'option_a': 'Python',
                'option_b': 'JavaScript',
                'option_c': 'PHP',
                'option_d': 'جميع ما سبق',
                'correct_answer': 'D'
            },
            {
                'question_text': 'ما هو المفهوم الأساسي في البرمجة الكائنية؟',
                'question_type': 'mcq',
                'option_a': 'الوراثة',
                'option_b': 'التغليف',
                'option_c': 'تعدد الأشكال',
                'option_d': 'جميع ما سبق',
                'correct_answer': 'D'
            },

            # True/False Questions
            {
                'question_text': 'لغة Python تُعتبر لغة برمجة مفسرة (Interpreted Language)',
                'question_type': 'true_false',
                'correct_answer': 'True'
            },
            {
                'question_text': 'قواعد البيانات العلائقية تدعم فقط العمليات البسيطة مثل الإدراج والحذف',
                'question_type': 'true_false',
                'correct_answer': 'False'
            },
            {
                'question_text': 'HTML هي لغة برمجة كاملة مثل Java أو Python',
                'question_type': 'true_false',
                'correct_answer': 'False'
            },
            {
                'question_text': 'يمكن استخدام Git في إدارة وتتبع التغييرات في المشاريع البرمجية',
                'question_type': 'true_false',
                'correct_answer': 'True'
            },

            # Q&A Questions
            {
                'question_text': 'اشرح الفرق بين HTTP و HTTPS وأهمية كل منهما في تطوير المواقع',
                'question_type': 'qa',
                'answer': '''HTTP (HyperText Transfer Protocol):
- بروتوكول نقل النصوص التشعبية
- لا يوفر تشفير للبيانات
- البيانات تُرسل بصورة واضحة
- يستخدم المنفذ 80 افتراضياً

HTTPS (HTTP Secure):
- نسخة آمنة من HTTP
- يستخدم SSL/TLS للتشفير
- يحمي البيانات من التنصت والتلاعب
- يستخدم المنفذ 443 افتراضياً
- ضروري للمواقع التي تتعامل مع بيانات حساسة

الأهمية:
- HTTPS ضروري لحماية كلمات المرور والبيانات المصرفية
- يحسن ترتيب الموقع في محركات البحث
- يزيد ثقة المستخدمين في الموقع'''
            },
            {
                'question_text': 'ما هي أهم مبادئ الأمان في تطوير التطبيقات الويب؟',
                'question_type': 'qa',
                'answer': '''مبادئ الأمان الأساسية:

1. التحقق من صحة البيانات (Input Validation):
- فحص جميع البيانات الواردة من المستخدم
- منع هجمات SQL Injection و XSS

2. التشفير (Encryption):
- تشفير كلمات المرور باستخدام Hash functions
- استخدام HTTPS لتشفير البيانات المنقولة

3. إدارة الجلسات (Session Management):
- انتهاء صلاحية الجلسات تلقائياً
- إعادة توليد معرف الجلسة عند تسجيل الدخول

4. التحكم في الوصول (Access Control):
- تطبيق مبدأ الأذونات الأدنى
- التحقق من صلاحيات المستخدم لكل عملية

5. تسجيل العمليات (Logging):
- تسجيل جميع العمليات الحساسة
- مراقبة المحاولات المشبوهة

6. التحديث المستمر:
- تحديث المكتبات والإطارات البرمجية
- تطبيق التصحيحات الأمنية'''
            },
            {
                'question_text': 'صف عملية تطوير المشاريع باستخدام منهجية Agile',
                'question_type': 'qa',
                'answer': '''منهجية Agile:

المبادئ الأساسية:
- التعاون مع العملاء أهم من التفاوض على العقود
- الأفراد والتفاعل أهم من العمليات والأدوات
- البرمجيات العاملة أهم من التوثيق الشامل
- الاستجابة للتغيير أهم من اتباع خطة محددة

العملية:
1. تقسيم المشروع إلى دورات قصيرة (Sprints)
2. اجتماعات يومية قصيرة (Daily Standups)
3. مراجعة نهاية كل دورة (Sprint Review)
4. تحسين مستمر للعملية (Retrospective)

الفوائد:
- مرونة في التعامل مع التغييرات
- تقليل المخاطر من خلال التطوير التدريجي
- تحسين جودة المنتج من خلال الاختبار المستمر
- رضا أكبر للعملاء من خلال التسليم المبكر'''
            }
        ]

        created_count = 0
        for question_data in questions_data:
            question, created = EvaluationQuestion.objects.get_or_create(
                question_text=question_data['question_text'],
                defaults=question_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created {question.get_question_type_display()}: {question.question_text[:50]}...')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Question already exists: {question.question_text[:50]}...')
                )

        # Summary
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully created {created_count} new questions!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nAll sample questions already exist.')
            )

        # Show counts by type
        mcq_count = EvaluationQuestion.objects.filter(question_type='mcq').count()
        tf_count = EvaluationQuestion.objects.filter(question_type='true_false').count()
        qa_count = EvaluationQuestion.objects.filter(question_type='qa').count()

        self.stdout.write(
            self.style.SUCCESS(f'\nQuestion counts:')
        )
        self.stdout.write(f'- اختيار من متعدد: {mcq_count}')
        self.stdout.write(f'- صح أم خطأ: {tf_count}')
        self.stdout.write(f'- سؤال وجواب: {qa_count}')
        self.stdout.write(f'- إجمالي: {mcq_count + tf_count + qa_count}')