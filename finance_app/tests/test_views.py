from django.test import TestCase
from django.urls import reverse
from finance_app.forms import RegistrationForm
from django.contrib.auth import get_user_model, get_user


class RegisterPageTest(TestCase):
    def test_register_page_renders_correct_template(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertIsInstance(response.context["form"], RegistrationForm)

    def test_register_page_successful_registration(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "complexpassword123",
                "password2": "complexpassword123",
            },
        )
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(get_user_model().objects.filter(username="newuser").exists())

    def test_register_page_registration_invalid_data(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "complexpassword123",
                "password2": "differentpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "password2", "Hesla se neshodují.")


class LoginPageTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )

    def test_login_page_renders_correct_template(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_page_successful_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "password123",
            },
        )
        self.assertRedirects(response, reverse("main_page"))

    def test_login_page_invalid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, "form", None, "Nesprávné uživatelské jméno nebo heslo."
        )

    def test_authenticated_user_redirected_from_login(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("main_page"))


class LogoutPageTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )

    def test_logout_redirects_anonymous_user(self):
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('logout')}")

    def test_logout_logs_out_authenticated_user(self):
        self.client.login(username="testuser", password="password123")

        self.assertTrue(get_user(self.client).is_authenticated)

        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "logout.html")

        self.assertFalse(get_user(self.client).is_authenticated)
