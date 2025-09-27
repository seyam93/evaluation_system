from django.core.management.base import BaseCommand
from examinations.models import PreviousTestTemplate


class Command(BaseCommand):
    help = 'Create default previous test templates'

    def handle(self, *args, **options):
        # Default test templates
        default_tests = [
            {
                'name': 'English',
                'name_arabic': 'اللغة الإنجليزية',
                'max_score': 100,
                'order': 1
            },
            {
                'name': 'IT Skills',
                'name_arabic': 'الحاسب الآلي',
                'max_score': 100,
                'order': 2
            },
            {
                'name': 'General Information',
                'name_arabic': 'المعلومات العامة',
                'max_score': 100,
                'order': 3
            },
            {
                'name': 'Psychology',
                'name_arabic': 'الاختبار النفسي',
                'max_score': 100,
                'order': 4
            },
            {
                'name': 'Security',
                'name_arabic': 'الأمن',
                'max_score': 100,
                'order': 5
            }
        ]

        created_count = 0
        for test_data in default_tests:
            template, created = PreviousTestTemplate.objects.get_or_create(
                name=test_data['name'],
                defaults=test_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created test template: {template.name_arabic} ({template.name})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Test template already exists: {template.name_arabic} ({template.name})')
                )

        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully created {created_count} new test templates!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nAll default test templates already exist.')
            )