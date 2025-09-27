from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Update user names for better reporting'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to update')
        parser.add_argument('--first-name', type=str, help='First name (Arabic)')
        parser.add_argument('--last-name', type=str, help='Last name (Arabic)')
        parser.add_argument('--list', action='store_true', help='List all users and their names')

    def handle(self, *args, **options):
        if options['list']:
            self.list_users()
            return

        if not options['username']:
            self.stdout.write(
                self.style.ERROR('Please provide --username or use --list to see all users')
            )
            return

        username = options['username']
        first_name = options.get('first_name', '')
        last_name = options.get('last_name', '')

        if not first_name and not last_name:
            self.stdout.write(
                self.style.ERROR('Please provide at least --first-name or --last-name')
            )
            return

        try:
            user = User.objects.get(username=username)

            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name

            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated user "{username}": {user.get_full_name()}'
                )
            )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" not found')
            )

    def list_users(self):
        self.stdout.write(self.style.SUCCESS('Current users and their names:'))
        self.stdout.write('-' * 50)

        for user in User.objects.all():
            full_name = user.get_full_name() or 'No name set'
            user_type = 'Unknown'

            if hasattr(user, 'profile'):
                user_type = user.profile.get_user_type_display()

            self.stdout.write(f'Username: {user.username}')
            self.stdout.write(f'  Name: {full_name}')
            self.stdout.write(f'  Type: {user_type}')
            self.stdout.write(f'  Email: {user.email or "Not set"}')
            self.stdout.write('')