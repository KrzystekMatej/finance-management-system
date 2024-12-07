from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import random
from finance_app.models import (
    UserProfile,
    Category,
    CategoryPreference,
    Transaction,
    RecurringTransaction,
    Budget,
    SharedBudget,
    Notification,
    TimeInterval,
    NotificationMode,
    BudgetRole,
    BudgetPermission,
)
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import locale
from enum import Enum
from django.contrib.auth.hashers import make_password


def get_random_datetime(start, end):
    if start > end:
        raise ValueError("Start must be earlier than end.")

    delta = end - start
    delta_seconds = delta.total_seconds()
    random_seconds = random.uniform(0, delta_seconds)
    return start + timedelta(seconds=random_seconds)


email_domains = ["seznam.cz", "gmail.com", "outlook.com", "centrum.cz", "yahoo.com"]

first_names = [
    "James",
    "Mary",
    "John",
    "Patricia",
    "Robert",
    "Jennifer",
    "Michael",
    "Linda",
    "William",
    "Elizabeth",
    "David",
    "Barbara",
    "Richard",
    "Susan",
    "Joseph",
    "Jessica",
    "Thomas",
    "Sarah",
    "Charles",
    "Karen",
    "Christopher",
    "Nancy",
    "Daniel",
    "Lisa",
    "Matthew",
    "Betty",
    "Anthony",
    "Margaret",
    "Mark",
    "Sandra",
]

last_names = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
    "Taylor",
    "Moore",
    "Jackson",
    "Martin",
    "Lee",
    "Perez",
    "Thompson",
    "White",
    "Harris",
    "Sanchez",
    "Clark",
    "Ramirez",
    "Lewis",
    "Robinson",
]

default_category_names = [
    "Ostatní",
    "Jídlo",
    "Doprava",
    "Zábava",
    "Zdraví",
    "Domácnost",
    "Výplata",
]

user_category_names = [
    "Potraviny",
    "Ubytování",
    "Kultura",
    "Hudba",
    "Knížky",
    "Restaurace",
    "Kavárny",
    "Cestování",
    "Dárky",
    "Sport",
    "Hobby",
    "Oblečení",
    "Elektronika",
    "Pojištění",
    "Filmy",
    "Vzdělání",
    "Energie",
    "Internet",
    "Telekomunikace",
    "Hry",
    "Knihy",
    "Kosmetika",
    "Auta",
    "Domácí zvířata",
    "Půjčky",
    "Úspory",
    "Charita",
    "Nájem",
    "Údržba",
    "Zahrada",
]

user_colors = [
    "#FF8C33",  # Orange
    "#33FF57",  # Green
    "#5733FF",  # Blue
    "#FF33A1",  # Pink
    "#33FFF5",  # Cyan
    "#FFA533",  # Amber
    "#9D33FF",  # Purple
    "#FFD633",  # Yellow
    "#FF8C57",  # Coral
    "#8C33FF",  # Indigo
    "#33FFDD",  # Turquoise
    "#964B00",  # Brown
    "#338CFF",  # Ocean blue
]

typical_recurring_transactions = [
    {"name": "Netflix", "amount": -300, "category_id": 4},
    {"name": "Spotify", "amount": -170, "category_id": 4},
    {"name": "Posilovna", "amount": -500, "category_id": 5},
    {"name": "Elektřina", "amount": -1200, "category_id": 6},
    {"name": "Internet", "amount": -500, "category_id": 6},
    {"name": "Pojištění auta", "amount": -200, "category_id": 3},
    {"name": "Amazon Prime", "amount": -300, "category_id": 4},
    {"name": "Voda", "amount": -350, "category_id": 6},
]

current_time = datetime.now().replace(microsecond=0)

intervals = [interval.name for interval in TimeInterval]
notification_modes = [notification_mode.name for notification_mode in NotificationMode]
budget_roles = [role.name for role in BudgetRole]
budget_permissions = [budget_permission.name for budget_permission in BudgetPermission]


class Table:
    def __init__(self, name, is_child=False):
        self.name = name
        self.id_counter = 1
        self.records = {}
        self.is_child = is_child

    def add_record(self, record):
        record["id"] = self.id_counter
        self.records[self.id_counter] = record
        self.id_counter += 1

    def get_record(self, id):
        return self.records[id]

    def filter(self, condition):
        return [record for record in self.records.values() if condition(record)]

    def get_insert_script(self):
        if not self.records:
            return ""

        columns = [
            f"'{column}'"
            for column in self.get_record(1).keys()
            if column != "id" or not self.is_child
        ]

        rows = []
        for record in self.records.values():
            values = []
            for key, value in record.items():
                if key == "id" and self.is_child:
                    continue

                if isinstance(value, str):
                    values.append(f"'{value}'")
                elif isinstance(value, int):
                    values.append(str(value))
                elif isinstance(value, Enum):
                    values.append(f"'{value.name}'")
                elif isinstance(value, datetime):
                    values.append(f"'{value.strftime('%Y-%m-%d %H:%M:%S%z')}'")
                else:
                    values.append("NULL")

            rows.append(f"({', '.join(values)})")

        columns_str = ", ".join(columns)
        rows_str = ",\n".join(rows)
        sql_command = f"INSERT INTO {self.name} ({columns_str}) VALUES\n{rows_str};\n"

        return sql_command


user_table = Table(User._meta.db_table)
user_profile_table = Table(UserProfile._meta.db_table)
category_table = Table(Category._meta.db_table)
category_preference_table = Table(CategoryPreference._meta.db_table)
transaction_table = Table(Transaction._meta.db_table)
recurring_transaction_table = Table(RecurringTransaction._meta.db_table, True)
budget_table = Table(Budget._meta.db_table)
budget_categories_table = Table("budget_categories")
shared_budget_table = Table(SharedBudget._meta.db_table)
notification_table = Table(Notification._meta.db_table)

tables = [
    user_table,
    user_profile_table,
    category_table,
    category_preference_table,
    transaction_table,
    recurring_transaction_table,
    budget_table,
    shared_budget_table,
    notification_table,
]


def add_preferences_for_user(user, default_categories, user_categories):
    categories = default_categories + random.sample(
        user_categories, random.randint(0, 5)
    )
    colors = random.sample(user_colors, len(categories))

    for category, color in zip(categories, colors):
        preference = {
            "user_id": user["id"],
            "category_id": category["id"],
            "color": color,
        }
        category_preference_table.add_record(preference)

    return categories


def add_transactions_for_user(user, categories, price_range):
    start_date = (user["date_joined"] + relativedelta(months=1)).replace(day=1)

    user_transactions = []

    while start_date < current_time:
        month_count = random.randint(4, 15)
        next_date = start_date + relativedelta(months=1)

        for _ in range(month_count):
            category = random.choice(categories)
            transaction = {
                "user_id": user["id"],
                "category_id": category["id"],
                "amount": -random.randint(price_range[0], price_range[1]),
                "performed_at": get_random_datetime(start_date, next_date),
                "name": f'Nákup - {category["name"]}',
                "created_at": current_time,
                "description": "",
            }

            transaction_table.add_record(transaction)
            user_transactions.append(transaction)

        start_date = next_date

    return user_transactions


def add_income_transaction(user, income):
    income_day = random.randint(1, 10)
    income_date = (user["date_joined"] + relativedelta(months=1)).replace(
        day=income_day, hour=10, minute=0, second=0, microsecond=0
    )
    income_category = category_table.get_record(7)

    income_transaction = {
        "user_id": user["id"],
        "category_id": income_category["id"],
        "amount": income,
        "performed_at": income_date,
        "name": income_category["name"],
        "created_at": income_date,
        "description": "",
    }

    transaction_table.add_record(income_transaction)

    income_recurring = {
        "transaction_ptr_id": income_transaction["id"],
        "_interval": TimeInterval.MONTH,
        "next_performed_at": income_date,
    }

    recurring_transaction_table.add_record(income_recurring)
    return income_recurring


def add_recurring_transactions_for_user(user, income):
    recurring_transactions = [add_income_transaction(user, income)]

    chosen_transactions = random.sample(
        typical_recurring_transactions, random.randint(0, 3)
    )

    for chosen in chosen_transactions:
        performed_at = get_random_datetime(
            user["date_joined"], current_time - relativedelta(months=1)
        )
        transaction = {
            "user_id": user["id"],
            "category_id": chosen["category_id"],
            "amount": chosen["amount"],
            "performed_at": performed_at,
            "name": chosen["name"],
            "created_at": performed_at,
            "description": "",
        }

        transaction_table.add_record(transaction)

        recurring = {
            "transaction_ptr_id": transaction["id"],
            "_interval": TimeInterval.MONTH,
            "next_performed_at": transaction["performed_at"],
        }

        recurring_transaction_table.add_record(recurring)
        recurring_transactions.append(recurring)

    transactions = []

    for recurring_data in recurring_transactions:
        transaction_data = transaction_table.get_record(
            recurring_data["transaction_ptr_id"]
        )

        while recurring_data["next_performed_at"] < current_time:
            transaction = {
                "user_id": user["id"],
                "category_id": transaction_data["category_id"],
                "amount": transaction_data["amount"],
                "performed_at": recurring_data["next_performed_at"],
                "name": transaction_data["name"],
                "created_at": recurring_data["next_performed_at"],
                "description": "",
            }

            transaction_table.add_record(transaction)
            recurring_data["next_performed_at"] = RecurringTransaction.get_next_date(
                recurring_data["next_performed_at"], recurring_data["_interval"]
            )

            transactions.append(transaction)

    return transactions


def add_budgets_for_user(user, categories):
    budgets = []
    num_budgets = random.randint(1, 3)
    relative_date = current_time - relativedelta(months=4)

    for _ in range(num_budgets):
        start_date = relative_date + relativedelta(months=random.randint(0, 3))
        end_date = start_date + relativedelta(months=random.randint(1, 6))
        limit = random.randint(5000, 50000)
        chosen_categories = random.sample(categories, random.randint(1, 3))

        categories_tmp = ", ".join([category["name"] for category in chosen_categories])

        budget = {
            "name": f"Rozpočet pro {categories_tmp}",
            "owner_id": user["id"],
            "created_at": start_date,
            "exceeded_at": None,
            "limit": limit,
            "period_start": start_date,
            "period_end": end_date,
            "description": f'A budget for managing expenses in {random.choice(categories)["name"]}',
        }

        budget_table.add_record(budget)

        for category in chosen_categories:
            budget_category = {
                "budget_id": budget["id"],
                "category_id": category["id"],
            }

            budget_categories_table.add_record(budget_category)

        budgets.append(budget)

    return budgets


def add_users():
    default_categories = category_table.filter(lambda category: category["is_default"])
    user_categories = category_table.filter(lambda category: not category["is_default"])

    for first_name, last_name in zip(first_names, last_names):
        user = {
            "username": f"{first_name}.{last_name}",
            "password": make_password("1234"),
            "email": f"{first_name}.{last_name}@{random.choice(email_domains)}",
            "first_name": first_name,
            "last_name": last_name,
            "date_joined": get_random_datetime(
                datetime(2023, 1, 1), current_time - relativedelta(months=2)
            ),
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
        }
        user_table.add_record(user)

        categories = add_preferences_for_user(user, default_categories, user_categories)
        categories = list(filter(lambda c: c["name"] != "Výplata", categories))

        transactions = add_transactions_for_user(
            user, categories, (100, 2000)
        ) + add_recurring_transactions_for_user(user, random.randint(30000, 60000))

        balance = sum(transaction["amount"] for transaction in transactions)
        user_profile = {
            "user_id": user["id"],
            "balance": balance,
            "_global_notification_mode": random.choice(notification_modes),
        }
        user_profile_table.add_record(user_profile)

        add_budgets_for_user(user, categories)


def add_categories():
    for category_name in default_category_names:
        category = {"name": category_name, "is_default": True}
        category_table.add_record(category)

    for category_name in user_category_names:
        category = {"name": category_name, "is_default": False}
        category_table.add_record(category)


class Command(BaseCommand):
    help = "Generate sql script to populate database with test values"

    def add_arguments(self, parser):
        parser.add_argument("output_file", type=str, help="Name of the output file")

    def handle(self, *args, **kwargs):
        script_path = kwargs["output_file"]

        random.seed(42)
        locale.setlocale(locale.LC_TIME, "cs_CZ.UTF-8")
        add_categories()
        add_users()

        with open(script_path, "w", encoding="utf-8") as file:
            for table in tables:
                table_script = table.get_insert_script()
                file.write(table_script)
                file.write("\n\n")
