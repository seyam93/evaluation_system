from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Create an examinee user for testing'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the examinee')
        parser.add_argument('--password', type=str, default='examinee123', help='Password for the examinee')
        parser.add_argument('--first-name', type=str, default='Test', help='First name')
        parser.add_argument('--last-name', type=str, default='Examinee', help='Last name')
        parser.add_argument('--email', type=str, default='examinee@test.com', help='Email address')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        email = options['email']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists.')
            )
            return

        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Update the user profile to be an examinee
        profile = user.profile
        profile.user_type = 'examinee'
        profile.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created examinee user "{username}" with password "{password}"'
            )
        )
        self.stdout.write(
            f'Login URL: http://127.0.0.1:8000/'
        )
        self.stdout.write(
            f'Examinee Dashboard: http://127.0.0.1:8000/evaluation/examinee/'
        )