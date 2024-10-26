from django.test import TestCase
from finance_app.models import (
    UserProfile,
    NotificationMode,
    Category,
    CategoryPreference,
    Transaction,
    Budget,
    SharedBudget,
    BudgetRole,
    BudgetPermission,
)
from django.contrib.auth import get_user_model


class UserProfileTests(TestCase):
    def test_create_user_profile(self):
        user = get_user_model().objects.create_user(
            username="john",
            password="password123",
            email="johnsmith@gmail.com",
            first_name="john",
            last_name="smith",
            is_superuser=False,
        )
        user.save()

        user_profile = UserProfile.objects.create(user=user)
        user_profile.balance = 100
        user_profile.global_notification_mode = NotificationMode.APP_EMAIL
        user_profile.save()

        user_profile_db = UserProfile.objects.get(id=user_profile.id)
        self.assertEqual(user_profile_db.user.username, "john")
        self.assertEqual(user_profile_db.user.check_password("password123"), True)
        self.assertEqual(user_profile_db.user.email, "johnsmith@gmail.com")
        self.assertEqual(user_profile_db.user.first_name, "john")
        self.assertEqual(user_profile_db.user.last_name, "smith")
        self.assertEqual(user_profile_db.balance, 100)
        self.assertEqual(user_profile_db.user.is_superuser, False)
        self.assertEqual(
            user_profile_db.global_notification_mode, NotificationMode.APP_EMAIL
        )


class CategoryTests(TestCase):
    pass


class CategoryPreferenceTests(TestCase):
    def test_create_category_preference(self):
        user = get_user_model().objects.create_user(
            username="john",
            password="password123",
        )
        user_profile = UserProfile.objects.create(user=user)

        category = Category.objects.create(name="Groceries")
        category_preference = CategoryPreference.objects.create(
            color="#FF5733", user=user_profile, category=category
        )

        category_preference_db = CategoryPreference.objects.get(
            id=category_preference.id
        )
        self.assertEqual(category_preference_db.user, user_profile)
        self.assertEqual(category_preference_db.category, category)
        self.assertEqual(category_preference_db.color, "#FF5733")
        self.assertEqual(category_preference_db.category.name, "Groceries")


class TransactionTests(TestCase):
    def test_create_transaction(self):
        user = get_user_model().objects.create_user(
            username="john",
            password="password123",
        )
        user_profile = UserProfile.objects.create(user=user)

        category = Category.objects.create(name="Groceries")

        transaction = Transaction.objects.create(
            name="Grocery Shopping",
            amount=50.00,
            performed_at="2024-10-25T14:30:00Z",
            category=category,
            description="Weekly grocery shopping",
            user=user_profile,
        )

        transaction_db = Transaction.objects.get(id=transaction.id)

        self.assertEqual(transaction_db.name, "Grocery Shopping")
        self.assertEqual(transaction_db.amount, 50.00)
        self.assertEqual(transaction_db.category, category)
        self.assertEqual(transaction_db.description, "Weekly grocery shopping")
        self.assertEqual(transaction_db.user, user_profile)
        self.assertIsNotNone(transaction_db.created_at)
        self.assertEqual(
            transaction_db.performed_at.isoformat(), "2024-10-25T14:30:00+00:00"
        )


class RecurringTransactionTests(TestCase):
    pass


class BudgetTests(TestCase):
    pass


class SharedBudgetTests(TestCase):
    def test_create_shared_budget(self):
        user1 = get_user_model().objects.create_user(
            username="john",
            password="password123",
        )
        user_profile1 = UserProfile.objects.create(user=user1)

        user2 = get_user_model().objects.create_user(
            username="jane",
            password="password456",
        )
        user_profile2 = UserProfile.objects.create(user=user2)

        category1 = Category.objects.create(name="Groceries")
        category2 = Category.objects.create(name="Utilities")

        budget = Budget.objects.create(
            name="Monthly Budget",
            owner=user_profile1,
            limit=500.00,
            period_start="2024-10-01",
            period_end="2024-10-31",
            description="October expenses",
        )
        budget.categories.add(category1, category2)

        shared_budget1 = SharedBudget.objects.create(
            budget=budget,
            shared_with=user_profile1,
            _permission=BudgetPermission.EDIT.value,
            _role=BudgetRole.PARTICIPANT.value,
            on_exceeded=True,
            on_limit_change=True,
            on_transaction=True,
            _notification_mode=NotificationMode.APP_EMAIL.value,
        )

        shared_budget2 = SharedBudget.objects.create(
            budget=budget,
            shared_with=user_profile2,
            _permission=BudgetPermission.VIEW.value,
            _role=BudgetRole.OBSERVER.value,
            on_exceeded=False,
            on_limit_change=False,
            on_transaction=False,
            _notification_mode=NotificationMode.NONE.value,
        )

        shared_budget1_db = SharedBudget.objects.get(id=shared_budget1.id)
        shared_budget2_db = SharedBudget.objects.get(id=shared_budget2.id)

        self.assertEqual(shared_budget1_db.budget, budget)
        self.assertEqual(shared_budget1_db.shared_with, user_profile1)
        self.assertEqual(shared_budget1_db.permission, BudgetPermission.EDIT)
        self.assertEqual(shared_budget1_db.role, BudgetRole.PARTICIPANT)
        self.assertEqual(
            shared_budget1_db.notification_mode, NotificationMode.APP_EMAIL
        )
        self.assertTrue(shared_budget1_db.on_exceeded)
        self.assertTrue(shared_budget1_db.on_limit_change)
        self.assertTrue(shared_budget1_db.on_transaction)

        self.assertEqual(shared_budget2_db.budget, budget)
        self.assertEqual(shared_budget2_db.shared_with, user_profile2)
        self.assertEqual(shared_budget2_db.permission, BudgetPermission.VIEW)
        self.assertEqual(shared_budget2_db.role, BudgetRole.OBSERVER)
        self.assertEqual(shared_budget2_db.notification_mode, NotificationMode.NONE)
        self.assertFalse(shared_budget2_db.on_exceeded)
        self.assertFalse(shared_budget2_db.on_limit_change)
        self.assertFalse(shared_budget2_db.on_transaction)

        categories = list(budget.categories.all())
        self.assertIn(category1, categories)
        self.assertIn(category2, categories)
        self.assertEqual(len(categories), 2)


class NotificationTests(TestCase):
    pass