from django.test import TestCase
from django.contrib.auth import get_user_model
from finance_app.forms import (
    RegistrationForm,
    LoginForm,
    TransactionForm,
    CategoryForm,
    BudgetForm,
    RecurringTransactionForm,
)
from finance_app.models import Category, Transaction, CategoryPreference
from django.utils import timezone
from decimal import Decimal


class RegistrationFormTest(TestCase):
    def test_registration_form_valid_data(self):
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_missing_first_name(self):
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "last_name": "Doe",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)

    def test_registration_form_missing_last_name(self):
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "John",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("last_name", form.errors)

    def test_registration_form_invalid_email(self):
        get_user_model().objects.create(
            username="existinguser", email="test@example.com"
        )
        form_data = {
            "username": "newuser",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_registration_form_password_mismatch(self):
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "complexpassword123",
            "password2": "differentpassword",
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class LoginFormTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )

    def test_login_form_valid_data(self):
        form_data = {"username": "testuser", "password": "password123"}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_form_invalid_credentials(self):
        form_data = {"username": "testuser", "password": "wrongpassword"}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)


class CreateTransactionFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password"
        )
        self.category = Category.objects.create(name="Food", is_default=True)

    def test_create_transaction_valid_data(self):
        form_data = {
            "name": "Grocery Shopping",
            "amount": Decimal("150.00"),
            "performed_at": timezone.now().date(),
            "category": self.category.id,
            "description": "Weekly groceries",
        }
        form = TransactionForm(data=form_data)
        self.assertTrue(form.is_valid(), "Form should be valid with correct data")

    def test_create_transaction_missing_name(self):
        form_data = {
            "amount": Decimal("150.00"),
            "performed_at": timezone.now().date(),
            "category": self.category.id,
            "description": "Weekly groceries",
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid if 'name' is missing")
        self.assertIn("name", form.errors)

    def test_create_transaction_empty_name(self):
        form_data = {
            "name": "",
            "amount": Decimal("150.00"),
            "performed_at": timezone.now().date(),
            "category": self.category.id,
            "description": "Empty name test",
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(
            form.is_valid(), "Form should be invalid if 'name' is an empty string"
        )
        self.assertIn("name", form.errors)

    def test_create_transaction_missing_category(self):
        form_data = {
            "name": "Miscellaneous",
            "amount": Decimal("30.00"),
            "performed_at": timezone.now().date(),
            "description": "Random expense",
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(
            form.is_valid(), "Form should be invalid if 'category' is missing"
        )
        self.assertIn("category", form.errors)

    def test_create_transaction_with_empty_category(self):
        form_data = {
            "name": "Nákup v supermarketu",
            "amount": Decimal("250.00"),
            "performed_at": "2024-10-29",
            "category": "",
            "description": "Test nákupu",
        }

        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)

    def test_create_transaction_future_date(self):
        future_date = timezone.now().date() + timezone.timedelta(days=30)
        form_data = {
            "name": "Future Purchase",
            "amount": Decimal("70.00"),
            "performed_at": future_date,
            "category": self.category.id,
            "description": "Future planned expense",
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(
            form.is_valid(), "Form should be invalid if 'performed_at' is in the future"
        )
        self.assertIn("performed_at", form.errors)


class CreateCategoryFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )

    def test_valid_data(self):
        form_data = {"name": "Test Category", "color": "#ff5733"}
        form = CategoryForm(data=form_data)
        self.assertTrue(
            form.is_valid(), "Form should be valid with a proper name and color."
        )

    def test_missing_name(self):
        form_data = {"color": "#ff5733"}
        form = CategoryForm(data=form_data)
        self.assertFalse(
            form.is_valid(), "Form should be invalid if the name field is missing."
        )
        self.assertIn(
            "name", form.errors, "Form should have 'name' in errors when it's missing."
        )

    def test_empty_name(self):
        form_data = {"name": "", "color": "#ff5733"}
        form = CategoryForm(data=form_data)
        self.assertFalse(
            form.is_valid(), "Form should be invalid if the name is an empty string."
        )
        self.assertIn(
            "name",
            form.errors,
            "Form should have 'name' in errors when it's an empty string.",
        )

    def test_missing_color(self):
        form_data = {"name": "Test Category"}
        form = CategoryForm(data=form_data)
        self.assertFalse(
            form.is_valid(), "Form should be invalid if the color field is missing."
        )
        self.assertIn(
            "color",
            form.errors,
            "Form should have 'color' in errors when it's missing.",
        )

    def test_invalid_color_format(self):
        form_data = {"name": "Test Category", "color": "invalid"}
        form = CategoryForm(data=form_data)
        self.assertFalse(
            form.is_valid(),
            "Form should be invalid if the color code is improperly formatted.",
        )
        self.assertIn(
            "color",
            form.errors,
            "Form should have 'color' in errors for invalid color format.",
        )


class EditTransactionFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )
        self.category = Category.objects.create(name="Food", is_default=True)
        self.transaction = Transaction.objects.create(
            name="Old Transaction",
            amount=Decimal("100.00"),
            performed_at=timezone.now(),
            user=self.user,
            category=self.category,
            description="Old description",
        )

    def test_edit_transaction_valid_data(self):
        form_data = {
            "name": "Updated Transaction",
            "amount": Decimal("150.00"),
            "performed_at": timezone.now(),
            "category": self.category.id,
            "description": "Updated description",
        }
        form = TransactionForm(
            data=form_data, instance=self.transaction, user=self.user
        )
        self.assertTrue(form.is_valid())
        updated_transaction = form.save()
        self.assertEqual(updated_transaction.name, "Updated Transaction")
        self.assertEqual(updated_transaction.amount, Decimal("150.00"))

    def test_edit_transaction_invalid_amount(self):
        form_data = {
            "name": "Invalid Transaction",
            "amount": "invalid",
            "performed_at": timezone.now(),
            "category": self.category.id,
            "description": "Invalid amount",
        }
        form = TransactionForm(
            data=form_data, instance=self.transaction, user=self.user
        )
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)


class EditCategoryFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )
        self.category = Category.objects.create(name="Travel")
        self.category_preference = CategoryPreference.objects.create(
            user=self.user, category=self.category, color="#FF5733"
        )

    def test_edit_category_valid_data(self):
        form_data = {
            "name": "Updated Travel",
            "color": "#00FF00",
        }
        form = CategoryForm(
            data=form_data, user=self.user, existing_instance=self.category_preference
        )
        self.assertTrue(form.is_valid())
        updated_preference = form.save()
        self.assertEqual(updated_preference.color, "#00FF00")
        self.assertEqual(updated_preference.category.name, "Updated Travel")

    def test_edit_category_invalid_color(self):
        form_data = {
            "name": "Travel",
            "color": "invalid-color",
        }
        form = CategoryForm(
            data=form_data, user=self.user, existing_instance=self.category_preference
        )
        self.assertFalse(form.is_valid())
        self.assertIn("color", form.errors)


class BudgetFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )
        self.category = Category.objects.create(name="Groceries")

    def test_budget_form_valid_data(self):
        data = {
            "name": "Weekly Budget",
            "limit": Decimal("300.00"),
            "period_start": timezone.now(),
            "period_end": timezone.now() + timezone.timedelta(days=7),
            "categories": [self.category],
            "description": "Groceries for the week.",
        }
        form = BudgetForm(data=data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_budget_form_negative_limit(self):
        data = {
            "name": "Invalid Budget",
            "limit": Decimal("-50.00"),
            "period_start": timezone.now(),
            "period_end": timezone.now() + timezone.timedelta(days=7),
            "categories": [self.category],
            "description": "Invalid limit.",
        }
        form = BudgetForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("limit", form.errors)

    def test_budget_form_invalid_dates(self):
        data = {
            "name": "Date Error Budget",
            "limit": Decimal("150.00"),
            "period_start": timezone.now(),
            "period_end": timezone.now() - timezone.timedelta(days=7),
            "categories": [self.category],
            "description": "End date before start date.",
        }
        form = BudgetForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("period_end", form.errors)

    def test_budget_form_missing_categories(self):
        data = {
            "name": "No Categories Budget",
            "limit": Decimal("200.00"),
            "period_start": timezone.now(),
            "period_end": timezone.now() + timezone.timedelta(days=15),
            "categories": [],
            "description": "No categories selected.",
        }
        form = BudgetForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("categories", form.errors)


class RecurringTransactionFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )
        self.category = Category.objects.create(name="Utilities")

    def test_recurring_transaction_form_valid_data(self):
        form_data = {
            "name": "Monthly Rent",
            "amount": Decimal("1200.00"),
            "performed_at": timezone.now(),
            "next_performed_at": timezone.now() + timezone.timedelta(days=30),
            "interval": "MONTH",
            "category": self.category.id,
            "description": "Monthly rent payment",
        }
        form = RecurringTransactionForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_recurring_transaction_form_invalid_interval(self):
        form_data = {
            "name": "Weekly Grocery",
            "amount": Decimal("200.00"),
            "performed_at": timezone.now(),
            "next_performed_at": timezone.now() + timezone.timedelta(days=7),
            "interval": "INVALID",
            "category": self.category.id,
            "description": "Invalid interval",
        }
        form = RecurringTransactionForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("interval", form.errors)
