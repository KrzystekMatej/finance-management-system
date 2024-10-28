from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
import random

from finance_app.models import (
    Category,
    CategoryPreference,
    Transaction,
    Budget,
)


def create_default_categories():
    categories_data = [
        {"name": "Jídlo"},
        {"name": "Doprava"},
        {"name": "Zábava"},
        {"name": "Nákupy"},
        {"name": "Bydlení"},
        {"name": "Zdraví"},
        {"name": "Výplata"},
    ]

    for category_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=category_data["name"], is_default=True
        )
        if created:
            category.save()


def create_users():
    users_data = [
        {
            "username": "jnovak",
            "email": "jnovak@example.com",
            "password": "heslo123",
            "first_name": "Jan",
            "last_name": "Novák",
        },
        {
            "username": "ppavel",
            "email": "ppavel@example.com",
            "password": "heslo123",
            "first_name": "Petr",
            "last_name": "Pavel",
        },
    ]

    for user_data in users_data:
        user = get_user_model().objects.create_user(
            username=user_data["username"],
            password=user_data["password"],
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
        )
        user.save()


def generate_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


def assign_colors_to_preferences_of_default_categories():
    for preference in CategoryPreference.objects.all():
        preference.color = generate_random_color()
        preference.save()


def create_user_defined_categories():
    user_defined_categories = [
        "Sport",
        "Cestování",
        "Elektronika",
        "Knihy",
        "Domácnost",
    ]

    user_categories = []
    for name in user_defined_categories:
        category, created = Category.objects.get_or_create(name=name, is_default=False)
        user_categories.append(category)

    for user in get_user_model().objects.all():
        assigned_categories = random.sample(
            user_categories, k=random.randint(1, len(user_categories))
        )

        for category in assigned_categories:
            CategoryPreference.objects.get_or_create(
                user=user,
                category=category,
                defaults={"color": generate_random_color()},
            )


def create_transactions_and_budgets_for_test_user():
    user = get_user_model().objects.get(username="jnovak")

    budget_1 = Budget.objects.create(
        name="Domácnost",
        owner=user,
        created_at=timezone.now(),
        limit=Decimal("2000.00"),
        period_start=date.today() - timedelta(days=30),
        period_end=date.today() + timedelta(days=30),
        description="Rozpočet na domácí výdaje",
    )

    budget_2 = Budget.objects.create(
        name="Volný čas",
        owner=user,
        created_at=timezone.now(),
        limit=Decimal("1000.00"),
        period_start=date.today() - timedelta(days=30),
        period_end=date.today() + timedelta(days=30),
        description="Rozpočet na volnočasové aktivity",
    )

    budget_1.categories.add(Category.objects.get(name="Jídlo"))
    budget_1.categories.add(Category.objects.get(name="Bydlení"))

    budget_2.categories.add(Category.objects.get(name="Zábava"))

    transactions = [
        (
            "Nákup potravin",
            Decimal("-450.00"),
            "Jídlo",
            "Týdenní nákup potravin v supermarketu",
            5,
        ),
        ("Měsíční nájem", Decimal("-1200.00"), "Bydlení", "Platba nájmu za měsíc", 2),
        (
            "Večeře s přáteli",
            Decimal("-300.00"),
            "Zábava",
            "Společná večeře v restauraci",
            7,
        ),
        ("Benzín", Decimal("-150.00"), "Doprava", "Tankování benzínu na cestu", 3),
        (
            "Údržba domácnosti",
            Decimal("-200.00"),
            "Bydlení",
            "Drobná údržba v bytě",
            10,
        ),
        ("Kino", Decimal("-100.00"), "Zábava", "Film v kině s rodinou", 9),
        ("Léky", Decimal("-75.00"), "Zdraví", "Lékárna", 15),
        ("Nákup oblečení", Decimal("-600.00"), "Nákupy", "Obnova šatníku", 20),
        ("Veřejná doprava", Decimal("-50.00"), "Doprava", "Jízdenky na MHD", 12),
        ("Sportovní aktivity", Decimal("-250.00"), "Zábava", "Fitcentrum", 8),
        ("Nákup elektroniky", Decimal("-1200.00"), "Nákupy", "Nový telefon", 18),
        ("Kadeřník", Decimal("-200.00"), "Nákupy", "Vlasy", 25),
        ("Víkendový pobyt", Decimal("-1500.00"), "Zábava", "Ubytování v hotelu", 30),
        ("Nákup knih", Decimal("-80.00"), "Nákupy", "Nová kniha na čtení", 11),
        ("Pojištění", Decimal("-400.00"), "Bydlení", "Pojištění domu", 28),
        ("Dárek pro přátele", Decimal("-350.00"), "Nákupy", "Dárek k narozeninám", 16),
        ("Restaurace", Decimal("-250.00"), "Jídlo", "Oběd v restauraci", 4),
        (
            "Úklidové prostředky",
            Decimal("-120.00"),
            "Domácnost",
            "Nákup čisticích prostředků",
            6,
        ),
        (
            "Výdaje za internet",
            Decimal("-500.00"),
            "Bydlení",
            "Měsíční poplatek za internet",
            13,
        ),
        ("Kavárna", Decimal("-80.00"), "Jídlo", "Káva s přáteli", 14),
        ("Fitness", Decimal("-300.00"), "Zábava", "Permanentka do fitness centra", 5),
        ("Cestování", Decimal("-600.00"), "Doprava", "Vlaková jízdenka", 9),
        ("Domácí spotřebiče", Decimal("-150.00"), "Domácnost", "Nákup spotřebičů", 10),
        ("Školní potřeby", Decimal("-100.00"), "Nákupy", "Školní pomůcky pro děti", 12),
        ("Nákup hraček", Decimal("-250.00"), "Nákupy", "Hračky pro děti", 20),
        ("Dovolená", Decimal("-2000.00"), "Zábava", "Výlet do zahraničí", 21),
        ("Obnova obuvi", Decimal("-500.00"), "Nákupy", "Nákup nových bot", 23),
        ("Hobby", Decimal("-150.00"), "Zábava", "Modelářské potřeby", 27),
        ("Večeře doma", Decimal("-150.00"), "Jídlo", "Nákup potravin na večeři", 22),
        ("Výplata za říjen", Decimal("20000.00"), "Výplata", "", 0),
        ("Výplata za září", Decimal("20000.00"), "Výplata", "", 30),
    ]

    for name, amount, category_name, description, days_ago in transactions:
        Transaction.objects.create(
            name=name,
            amount=amount,
            performed_at=timezone.now() - timedelta(days=days_ago),
            user=user,
            category=Category.objects.get(name=category_name),
            description=description,
        )


class Command(BaseCommand):
    help = "Populate the database with default values"

    def handle(self, *args, **kwargs):
        create_users()
        create_default_categories()
        assign_colors_to_preferences_of_default_categories()
        create_user_defined_categories()
        create_transactions_and_budgets_for_test_user()

        self.stdout.write(self.style.SUCCESS("Database populated with default values."))
