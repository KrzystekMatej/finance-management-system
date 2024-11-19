from django.test import TestCase
from django.urls import reverse
from finance_app.forms import RegistrationForm
from django.contrib.auth import get_user_model, get_user
from django.utils import timezone
from finance_app.models import Transaction, Category, CategoryPreference


class RegisterPageTest(TestCase):
    def test_register_page_renders_correct_template(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertIsInstance(response.context["form"], RegistrationForm)

    def test_register_page_successful_registration(self):
        self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password1": "complexpassword123",
                "password2": "complexpassword123",
            },
        )
        self.assertRedirects(response, reverse("register-success"))
        self.assertTrue(get_user_model().objects.filter(username="newuser").exists())

    def test_register_page_registration_invalid_data(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "first_name": "John",
                "last_name": "Doe",
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


class CreateTransactionViewTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )
        self.client.login(username="testuser", password="password123")

        self.category = Category.objects.create(name="Test Kategorie", is_default=True)

    def test_create_transaction_success(self):
        url = reverse("create-transaction")
        response = self.client.post(
            url,
            {
                "name": "Testovací transakce",
                "amount": "100.00",
                "performed_at": timezone.now().date(),
                "category": self.category.id,
                "description": "Popis transakce",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
        self.assertEqual(Transaction.objects.count(), 1)

    def test_create_transaction_missing_fields(self):
        url = reverse("create-transaction")
        response = self.client.post(
            url,
            {
                "name": "",
                "amount": "100.00",
                "performed_at": timezone.now().date(),
                "category": self.category.id,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json().get("success"))
        self.assertEqual(Transaction.objects.count(), 0)

    def test_create_transaction_invalid_amount(self):
        url = reverse("create-transaction")
        response = self.client.post(
            url,
            {
                "name": "Neplatná částka",
                "amount": "neplatná částka",
                "performed_at": timezone.now().date(),
                "category": self.category.id,
                "description": "Popis transakce",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json().get("success"))
        self.assertEqual(Transaction.objects.count(), 0)

    def test_create_transaction_future_date(self):
        url = reverse("create-transaction")
        future_date = (timezone.now() + timezone.timedelta(days=1)).date()
        response = self.client.post(
            url,
            {
                "name": "Budoucí transakce",
                "amount": "100.00",
                "performed_at": future_date,
                "category": self.category.id,
                "description": "Popis transakce",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json().get("success"))
        self.assertEqual(Transaction.objects.count(), 0)


class CreateCategoryViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.login(username="testuser", password="testpass")
        self.url = reverse("create-category")

    def test_create_category_success(self):
        data = {
            "name": "Nová kategorie",
            "color": "#FF5733",
        }

        response = self.client.post(
            self.url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(Category.objects.filter(name="Nová kategorie").count(), 1)

        category = Category.objects.get(name="Nová kategorie")
        category_preference = CategoryPreference.objects.get(
            user=self.user, category=category
        )
        self.assertEqual(category_preference.color, "#FF5733")

    def test_create_category_failure_existing_category(self):
        category = Category.objects.create(name="Existující kategorie")
        CategoryPreference.objects.create(
            user=self.user, category=category, color="#00FF00"
        )

        data = {
            "name": "Existující kategorie",
            "color": "#FF5733",
        }

        response = self.client.post(
            self.url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        # self.assertIn("Tuto kategorii už máte vytvořenou.", response.json()["errors"])

    def test_create_category_failure_invalid_color_format(self):
        data = {
            "name": "Nová kategorie s chybou",
            "color": "incorrect-color",
        }

        response = self.client.post(
            self.url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        # self.assertIn("Neplatný formát barvy.", response.json()["errors"])

    def test_create_category_failure_missing_color(self):
        data = {
            "name": "Kategorie bez barvy",
        }

        response = self.client.post(
            self.url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        # self.assertIn("Tento údaj je povinný.", response.json()["errors"]["color"])

    def test_create_category_failure_missing_name(self):
        data = {
            "color": "#FF5733",
        }

        response = self.client.post(
            self.url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        # self.assertIn("Tento údaj je povinný.", response.json()["errors"]["name"])

    def test_create_category_failure_empty_name(self):
        data = {
            "name": "",
        }

        response = self.client.post(
            self.url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        # self.assertIn("Tento údaj je povinný.", response.json()["errors"]["name"])
