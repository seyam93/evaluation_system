from django.core.management.base import BaseCommand
from examinations.models import CandidateTest, TestCategory
from students.models import Person


class Command(BaseCommand):
    help = 'Migrate existing test results to pass/fail format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--person-name',
            type=str,
            help='Name of the person to migrate tests for'
        )
        parser.add_argument(
            '--test-category',
            type=str,
            help='Name of the test category to migrate'
        )
        parser.add_argument(
            '--result',
            type=str,
            choices=['pass', 'fail'],
            help='The pass/fail result to set'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes'
        )

    def handle(self, *args, **options):
        person_name = options.get('person_name')
        test_category_name = options.get('test_category')
        result = options.get('result')
        dry_run = options.get('dry_run', False)

        if not all([person_name, test_category_name, result]):
            self.stdout.write(
                self.style.ERROR('Please provide --person-name, --test-category, and --result')
            )
            return

        try:
            # Find the person
            person = Person.objects.get(student_name__icontains=person_name)
            self.stdout.write(f"Found person: {person.student_name}")

            # Find the test category
            test_category = TestCategory.objects.get(name__icontains=test_category_name)
            self.stdout.write(f"Found test category: {test_category.name} (result_type: {test_category.result_type})")

            # Find the candidate test
            candidate_test = CandidateTest.objects.get(
                person=person,
                test_category=test_category
            )

            self.stdout.write(f"Found candidate test:")
            self.stdout.write(f"  Current score: {candidate_test.score}")
            self.stdout.write(f"  Current pass_fail_result: {candidate_test.pass_fail_result}")
            self.stdout.write(f"  Test category result_type: {candidate_test.test_category.result_type}")

            if dry_run:
                self.stdout.write(
                    self.style.WARNING('DRY RUN - Would make the following changes:')
                )
                self.stdout.write(f"  Set pass_fail_result to: {result}")
                self.stdout.write(f"  Set score to: None")
            else:
                # Update the candidate test
                candidate_test.pass_fail_result = result
                candidate_test.score = None
                candidate_test.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully updated test result for {person.student_name} - {test_category.name} to: {result}'
                    )
                )

        except Person.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Person with name containing "{person_name}" not found')
            )
        except TestCategory.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Test category with name containing "{test_category_name}" not found')
            )
        except CandidateTest.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'No test found for {person_name} in category {test_category_name}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )