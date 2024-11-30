import os
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Reset the database, delete migrations, apply migrations, and populate test data."

    def handle(self, *args, **kwargs):
        db_path = settings.DATABASES["default"]["NAME"]

        if os.path.exists(db_path):
            self.stdout.write(f"Deleting database at {db_path}...")
            os.remove(db_path)

        self.stdout.write("Deleting migration files for user-defined apps...")
        for app_config in apps.get_app_configs():
            if "venv" in app_config.path:
                continue
            if app_config.path.startswith(str(settings.BASE_DIR)):
                migrations_path = os.path.join(app_config.path, "migrations")
                if os.path.exists(migrations_path):
                    self.stdout.write(f"Deleting migration files in: {migrations_path}")
                    migrations = [
                        f
                        for f in os.listdir(migrations_path)
                        if os.path.isfile(os.path.join(migrations_path, f))
                    ]
                    for file in migrations:
                        if file != "__init__.py":
                            os.remove(os.path.join(migrations_path, file))

        self.stdout.write("Creating migrations...")
        call_command("makemigrations", interactive=False)

        self.stdout.write("Applying migrations...")
        call_command("migrate", interactive=False)

        self.stdout.write("Populating database with test values...")
        sql_script = "populate_script.sql"
        call_command("generate_populate_script", sql_script)
        call_command("execute_sql", sql_script)

        self.stdout.write(
            self.style.SUCCESS("Database reset and populated successfully!")
        )
