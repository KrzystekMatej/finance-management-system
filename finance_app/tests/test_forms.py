from django.test import TestCase
from django.contrib.auth import get_user_model
from finance_app.forms import (
    RegistrationForm,
    LoginForm,
    TransactionForm,
    CategoryForm,
)
from finance_app.models import Category
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
            "name": "",  # Empty string
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
