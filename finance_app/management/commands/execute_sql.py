import os
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Execute an SQL script from the provided file path'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the SQL script to execute')

    def handle(self, *args, **kwargs):
        script_path = kwargs['file_path']

        if not os.path.isfile(script_path):
            self.stderr.write(f"Error: The file at {script_path} does not exist.")
            return

        with open(script_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()

        sql_statements = sql_script.split(';')

        try:
            with connection.cursor() as cursor:
                for statement in sql_statements:
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
                self.stdout.write(f"Successfully executed the SQL script: {script_path}")
        except Exception as e:
            self.stderr.write(f"Error executing the SQL script: {e}")