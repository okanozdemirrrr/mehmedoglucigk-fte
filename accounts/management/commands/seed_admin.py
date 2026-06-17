from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Deprecated: seed_users komutunu çağırır.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('seed_admin yerine seed_users kullanılıyor...'))
        call_command('seed_users', *args, **options)
