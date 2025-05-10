import os
import shutil
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.conf import settings
import importlib

class Command(BaseCommand):
    help = 'Resets migrations for the given app'

    def add_arguments(self, parser):
        parser.add_argument('app_name', nargs='?', default='base', type=str, help='The app to reset migrations for')
        parser.add_argument('--no-backup', action='store_true', help='Do not create backup of migration files')

    def handle(self, *args, **options):
        app_name = options['app_name']
        no_backup = options['no_backup']
        
        migrations_dir = os.path.join(settings.BASE_DIR, app_name, 'migrations')
        
        if not os.path.exists(migrations_dir):
            raise CommandError(f'Migrations directory for {app_name} does not exist')
        
        # Create a backup of the migrations directory if requested
        if not no_backup:
            backup_dir = os.path.join(settings.BASE_DIR, f'{app_name}_migrations_backup')
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            shutil.copytree(migrations_dir, backup_dir)
            self.stdout.write(self.style.SUCCESS(f'Backup of migrations created in {backup_dir}'))
        
        # Delete all migration files except for __init__.py
        for file_name in os.listdir(migrations_dir):
            file_path = os.path.join(migrations_dir, file_name)
            if os.path.isfile(file_path) and file_name != '__init__.py' and file_name.endswith('.py'):
                os.remove(file_path)
        
        self.stdout.write(self.style.SUCCESS(f'Migrations for {app_name} have been reset!'))
        self.stdout.write(self.style.WARNING('Make sure to run "python manage.py makemigrations" to create new migration files.')) 