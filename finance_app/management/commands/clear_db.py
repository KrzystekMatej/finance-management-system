from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction


class Command(BaseCommand):
    help = "Clear all data from all tables in the database"

    @transaction.atomic  # Ensures the operation is wrapped in a transaction
    def handle(self, *args, **kwargs):
        # Get all models in the project
        all_models = apps.get_models()

        # Optionally disable foreign key checks (e.g., for MySQL or SQLite)
        from django.db import connection

        if connection.vendor == "mysql":
            self.stdout.write(
                self.style.WARNING("Disabling foreign key checks for MySQL...")
            )
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        self.stdout.write(self.style.WARNING("Deleting all records from all tables..."))

        # Loop through all models and delete all records
        for model in all_models:
            model_name = model.__name__
            model.objects.all().delete()  # This deletes all records for the model
            self.stdout.write(
                self.style.SUCCESS(f"Cleared all records from {model_name}")
            )

        # Optionally re-enable foreign key checks (if previously disabled)
        if connection.vendor == "mysql":
            self.stdout.write(self.style.WARNING("Re-enabling foreign key checks..."))
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        self.stdout.write(
            self.style.SUCCESS("All data has been cleared from the database!")
        )
