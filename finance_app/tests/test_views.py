from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, get_user
from django.utils import timezone
from finance_app.models import Transaction, Category, CategoryPreference, Budget
from decimal import Decimal


class RegisterPageTest(TestCase):
    def test_register_page_renders_correct_template(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_register_page_successful_registration(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password1": "complexpassword123",
                "password2": "complexpassword123",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("redirect_url", response.json())
        self.assertEqual(response.json()["redirect_url"], reverse("register-success"))
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
        self.assertEqual(response.status_code, 400)


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

    def test_create_category_failure_missing_color(self):
        data = {
            "name": "Kategorie bez barvy",
        }

        response = self.client.post(
            self.url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_create_category_failure_missing_name(self):
        data = {
            "color": "#FF5733",
        }

        response = self.client.post(
            self.url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_create_category_failure_empty_name(self):
        data = {
            "name": "",
        }

        response = self.client.post(
            self.url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])


class CreateBudgetViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )
        self.client.login(username="testuser", password="password123")
        self.category = Category.objects.create(name="Utilities")
        self.url = reverse("create-budget")

    def test_create_budget_success(self):
        data = {
            "name": "Monthly Budget",
            "limit": "500.00",
            "period_start": timezone.now().isoformat(),
            "period_end": (timezone.now() + timezone.timedelta(days=30)).isoformat(),
            "categories": [self.category.id],
            "description": "Budget for monthly expenses.",
        }
        response = self.client.post(
            self.url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(Budget.objects.count(), 1)

    def test_create_budget_failure_invalid_limit(self):
        data = {
            "name": "Negative Limit Budget",
            "limit": "-100.00",
            "period_start": timezone.now().isoformat(),
            "period_end": (timezone.now() + timezone.timedelta(days=30)).isoformat(),
            "categories": [self.category.id],
            "description": "Budget with negative limit.",
        }
        response = self.client.post(
            self.url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_create_budget_failure_unauthorized(self):
        self.client.logout()
        response = self.client.post(
            self.url, {}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 302)


class EditCategoryViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )
        self.client.login(username="testuser", password="password123")
        self.category = Category.objects.create(name="Travel")
        self.category_preference = CategoryPreference.objects.create(
            user=self.user, category=self.category, color="#FF5733"
        )
        self.url = reverse("edit-category", args=[self.category_preference.id])

    def test_edit_category_invalid_data(self):
        response = self.client.post(
            self.url,
            {
                "name": "",
                "color": "invalid-color",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])


class DeleteCategoryViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )
        self.client.login(username="testuser", password="password123")
        self.category = Category.objects.create(name="Entertainment")
        self.category_preference = CategoryPreference.objects.create(
            user=self.user, category=self.category, color="#FF5733"
        )
        self.url = reverse("delete-category", args=[self.category_preference.id])

    def test_delete_category_success(self):
        response = self.client.post(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertFalse(
            CategoryPreference.objects.filter(id=self.category_preference.id).exists()
        )

    def test_delete_category_failure_unauthorized(self):
        self.client.logout()
        response = self.client.post(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 302)  # Redirect to login


class DeleteTransactionViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )
        self.client.login(username="testuser", password="password123")
        self.transaction = Transaction.objects.create(
            name="Test Transaction",
            amount=Decimal("100.00"),
            performed_at=timezone.now(),
            user=self.user,
            category=None,
            description="Test description",
        )
        self.url = reverse("delete-transaction", args=[self.transaction.id])

    def test_delete_transaction_success(self):
        response = self.client.post(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertFalse(Transaction.objects.filter(id=self.transaction.id).exists())

    def test_delete_transaction_failure_unauthorized(self):
        self.client.logout()
        response = self.client.post(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 302)
