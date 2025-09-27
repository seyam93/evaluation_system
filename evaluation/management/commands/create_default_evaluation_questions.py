from django.core.management.base import BaseCommand
from evaluation.models import EvaluationQuestion, EvaluationTemplate


class Command(BaseCommand):
    help = 'Create default evaluation questions and templates'

    def handle(self, *args, **options):
        # Default evaluation questions
        default_questions = [
            {
                'title': 'المظهر العام والانطباع الأول',
                'description': 'تقييم المظهر العام والانطباع الأول للمرشح',
                'question_type': 'rating',
                'max_score': 10,
                'weight': 1.0,
                'order': 1
            },
            {
                'title': 'مهارات التواصل والتعبير',
                'description': 'قدرة المرشح على التواصل والتعبير بوضوح',
                'question_type': 'rating',
                'max_score': 15,
                'weight': 1.5,
                'order': 2
            },
            {
                'title': 'الخبرة العملية ذات الصلة',
                'description': 'تقييم الخبرة العملية السابقة للمرشح في المجال',
                'question_type': 'rating',
                'max_score': 20,
                'weight': 2.0,
                'order': 3
            },
            {
                'title': 'المهارات التقنية والتخصصية',
                'description': 'تقييم المهارات التقنية والمعرفة التخصصية',
                'question_type': 'rating',
                'max_score': 25,
                'weight': 2.5,
                'order': 4
            },
            {
                'title': 'القدرة على حل المشاكل',
                'description': 'تقييم قدرة المرشح على التفكير النقدي وحل المشاكل',
                'question_type': 'rating',
                'max_score': 20,
                'weight': 2.0,
                'order': 5
            },
            {
                'title': 'العمل ضمن فريق',
                'description': 'تقييم قدرة المرشح على العمل الجماعي والتعاون',
                'question_type': 'rating',
                'max_score': 15,
                'weight': 1.5,
                'order': 6
            },
            {
                'title': 'الدافعية والاهتمام بالوظيفة',
                'description': 'تقييم مستوى الحماس والدافعية للوظيفة',
                'question_type': 'rating',
                'max_score': 15,
                'weight': 1.5,
                'order': 7
            },
            {
                'title': 'القدرة على التطوير والتعلم',
                'description': 'تقييم استعداد المرشح للتطوير المهني والتعلم المستمر',
                'question_type': 'rating',
                'max_score': 10,
                'weight': 1.0,
                'order': 8
            },
            {
                'title': 'ملاحظات إضافية',
                'description': 'أي ملاحظات أو تعليقات إضافية حول المرشح',
                'question_type': 'text',
                'max_score': 0,
                'weight': 0.0,
                'is_required': False,
                'order': 9
            },
            {
                'title': 'نقاط القوة الرئيسية',
                'description': 'اذكر أهم نقاط القوة التي لاحظتها في المرشح',
                'question_type': 'text',
                'max_score': 0,
                'weight': 0.0,
                'is_required': False,
                'order': 10
            },
            {
                'title': 'نقاط التحسين المطلوبة',
                'description': 'اذكر المجالات التي تحتاج إلى تطوير أو تحسين',
                'question_type': 'text',
                'max_score': 0,
                'weight': 0.0,
                'is_required': False,
                'order': 11
            }
        ]

        created_questions = []
        for question_data in default_questions:
            question, created = EvaluationQuestion.objects.get_or_create(
                title=question_data['title'],
                defaults=question_data
            )
            if created:
                created_questions.append(question)
                self.stdout.write(
                    self.style.SUCCESS(f'Created question: {question.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Question already exists: {question.title}')
                )

        # Create default template
        template_name = 'قالب التقييم الأساسي'
        template, template_created = EvaluationTemplate.objects.get_or_create(
            name=template_name,
            defaults={
                'description': 'القالب الأساسي لتقييم المرشحين يحتوي على الأسئلة الأساسية المطلوبة'
            }
        )

        if template_created or not template.questions.exists():
            # Add all questions to the template
            all_questions = EvaluationQuestion.objects.filter(
                title__in=[q['title'] for q in default_questions]
            )
            template.questions.set(all_questions)

            self.stdout.write(
                self.style.SUCCESS(f'Created/Updated template: {template.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Template already exists: {template.name}')
            )

        # Summary
        created_count = len(created_questions)
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully created {created_count} new evaluation questions!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nAll default evaluation questions already exist.')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Template "{template_name}" is ready with {template.questions.count()} questions.')
        )