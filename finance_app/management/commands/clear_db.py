from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction, connection
from finance_app.signals import update_balance_on_transaction_delete
from django.db.models.signals import post_delete


class Command(BaseCommand):
    help = "Clear all data from all tables in the database"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        post_delete.disconnect(update_balance_on_transaction_delete)

        all_models = apps.get_models()
        for model in all_models:
            model.objects.all().delete()

            with connection.cursor() as cursor:
                table_name = model._meta.db_table
                cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name=%s", [table_name]
                )

        post_delete.connect(update_balance_on_transaction_delete)

        self.stdout.write(self.style.SUCCESS("Database cleared successfully."))
