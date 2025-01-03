from django.test import TestCase
from django.contrib.auth import get_user_model
from finance_app.models import Category, CategoryPreference, UserProfile


class UserProfileSignalTests(TestCase):
    def test_user_profile_creation_on_user_creation(self):
        user = get_user_model().objects.create_user(
            username="testuser", password="password123", email="testuser@example.com"
        )

        user_profile = UserProfile.objects.get(user=user)

        self.assertEqual(user_profile.user, user)
        self.assertEqual(user_profile.balance, 0)


class LinkNewUserToExistingDefaultCategoriesSignalTests(TestCase):
    def setUp(self):
        self.default_category_1 = Category.objects.create(name="Food", is_default=True)
        self.default_category_2 = Category.objects.create(
            name="Transport", is_default=True
        )
        self.default_category_3 = Category.objects.create(
            name="Health", is_default=True
        )

    def test_default_categories_added_on_user_creation(self):
        user = get_user_model().objects.create_user(
            username="test_user", password="password123"
        )

        user_categories = CategoryPreference.objects.filter(user=user)

        self.assertEqual(user_categories.count(), 3)

        assigned_categories = [pref.category for pref in user_categories]
        self.assertIn(self.default_category_1, assigned_categories)
        self.assertIn(self.default_category_2, assigned_categories)
        self.assertIn(self.default_category_3, assigned_categories)


class LinkNewDefaultCategoryToExistingUsersSignalTests(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            username="user1", password="password"
        )
        self.user2 = get_user_model().objects.create_user(
            username="user2", password="password"
        )

        CategoryPreference.objects.all().delete()

    def test_add_new_default_category_to_all_users(self):
        default_category = Category.objects.create(name="Zdraví", is_default=True)

        user1_preferences = CategoryPreference.objects.filter(
            user=self.user1, category=default_category
        )
        user2_preferences = CategoryPreference.objects.filter(
            user=self.user2, category=default_category
        )

        self.assertEqual(user1_preferences.count(), 1)
        self.assertEqual(user2_preferences.count(), 1)
