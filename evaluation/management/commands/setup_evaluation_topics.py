from django.core.management.base import BaseCommand
from evaluation.models import EvaluationTopic, EvaluationCriteria


class Command(BaseCommand):
    help = 'Setup default evaluation topics with scoring criteria'

    def handle(self, *args, **options):
        # Create Personal Appearance topic
        personal_appearance, created = EvaluationTopic.objects.get_or_create(
            name='المظهر الشخصي',
            defaults={
                'description': 'تقييم المظهر العام والهندام والنظافة الشخصية للمرشح',
                'weight': 1.0,
                'order': 1,
                'is_active': True
            }
        )

        if created:
            self.stdout.write(f'Created topic: {personal_appearance.name}')

            # Create criteria for Personal Appearance
            criteria_data = [
                ('ضعيف', 25.0, 1, '#dc3545', 'مظهر غير مقبول، غير مناسب للعمل'),
                ('جيد', 25.0, 2, '#ffc107', 'مظهر مقبول مع بعض التحسينات المطلوبة'),
                ('جيد جداً', 25.0, 3, '#28a745', 'مظهر جيد ومناسب للعمل'),
                ('ممتاز', 25.0, 4, '#007bff', 'مظهر متميز ومثالي للعمل'),
            ]

            for name, percentage, order, color, description in criteria_data:
                criteria, created = EvaluationCriteria.objects.get_or_create(
                    topic=personal_appearance,
                    name=name,
                    defaults={
                        'score_percentage': percentage,
                        'order': order,
                        'color': color,
                        'description': description
                    }
                )
                if created:
                    self.stdout.write(f'  Created criteria: {criteria.name} ({percentage}%)')

        # Create Communication Skills topic
        communication, created = EvaluationTopic.objects.get_or_create(
            name='مهارات التواصل',
            defaults={
                'description': 'تقييم قدرة المرشح على التواصل والتعبير بوضوح',
                'weight': 1.5,
                'order': 2,
                'is_active': True
            }
        )

        if created:
            self.stdout.write(f'Created topic: {communication.name}')

            # Create criteria for Communication Skills
            criteria_data = [
                ('ضعيف', 25.0, 1, '#dc3545', 'صعوبة في التعبير والتواصل'),
                ('جيد', 25.0, 2, '#ffc107', 'تواصل مقبول مع بعض التحسينات'),
                ('جيد جداً', 25.0, 3, '#28a745', 'تواصل واضح وفعال'),
                ('ممتاز', 25.0, 4, '#007bff', 'تواصل متميز وإقناعي'),
            ]

            for name, percentage, order, color, description in criteria_data:
                criteria, created = EvaluationCriteria.objects.get_or_create(
                    topic=communication,
                    name=name,
                    defaults={
                        'score_percentage': percentage,
                        'order': order,
                        'color': color,
                        'description': description
                    }
                )
                if created:
                    self.stdout.write(f'  Created criteria: {criteria.name} ({percentage}%)')

        # Create Technical Knowledge topic
        technical, created = EvaluationTopic.objects.get_or_create(
            name='المعرفة التخصصية',
            defaults={
                'description': 'تقييم المعرفة والمهارات التخصصية للمرشح',
                'weight': 2.0,
                'order': 3,
                'is_active': True
            }
        )

        if created:
            self.stdout.write(f'Created topic: {technical.name}')

            # Create criteria for Technical Knowledge
            criteria_data = [
                ('ضعيف', 25.0, 1, '#dc3545', 'معرفة محدودة جداً بالمجال'),
                ('جيد', 25.0, 2, '#ffc107', 'معرفة أساسية بالمجال'),
                ('جيد جداً', 25.0, 3, '#28a745', 'معرفة جيدة ومتقدمة'),
                ('ممتاز', 25.0, 4, '#007bff', 'معرفة متخصصة ومتميزة'),
            ]

            for name, percentage, order, color, description in criteria_data:
                criteria, created = EvaluationCriteria.objects.get_or_create(
                    topic=technical,
                    name=name,
                    defaults={
                        'score_percentage': percentage,
                        'order': order,
                        'color': color,
                        'description': description
                    }
                )
                if created:
                    self.stdout.write(f'  Created criteria: {criteria.name} ({percentage}%)')

        self.stdout.write(
            self.style.SUCCESS('Successfully setup evaluation topics and criteria!')
        )