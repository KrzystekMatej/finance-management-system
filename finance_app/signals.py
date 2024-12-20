from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Category, CategoryPreference, UserProfile


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Category)
def link_new_default_category_to_existing_users(sender, instance, created, **kwargs):
    if instance.is_default:
        users = get_user_model().objects.all()

        for user in users:
            CategoryPreference.objects.get_or_create(user=user, category=instance)


@receiver(post_save, sender=get_user_model())
def link_new_user_to_existing_default_categories(sender, instance, created, **kwargs):
    if created:
        default_categories = Category.objects.filter(is_default=True)
        for category in default_categories:
            CategoryPreference.objects.create(user=instance, category=category)
