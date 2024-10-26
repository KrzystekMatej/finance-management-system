from django.test import TestCase
from django.contrib.auth import get_user_model
from finance_app.forms import RegistrationForm, LoginForm


class RegistrationFormTest(TestCase):
    def test_registration_form_valid_data(self):
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_invalid_email(self):
        get_user_model().objects.create(
            username="existinguser", email="test@example.com"
        )
        form_data = {
            "username": "newuser",
            "email": "test@example.com",  # Tento email je již používán
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
