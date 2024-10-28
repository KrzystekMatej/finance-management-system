from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Category, CategoryPreference, Transaction, UserProfile
from decimal import Decimal


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


original_amount = None


@receiver(pre_save, sender=Transaction)
def store_original_amount(sender, instance, **kwargs):
    global original_amount
    try:
        original_amount = Transaction.objects.get(pk=instance.pk).amount
    except Transaction.DoesNotExist:
        original_amount = None


@receiver(post_save, sender=Transaction)
def update_balance_on_transaction_save(sender, instance, created, **kwargs):
    user_profile = UserProfile.objects.get(user=instance.user)
    global original_amount
    if created:
        user_profile.balance += Decimal(instance.amount)
    else:
        difference = instance.amount - original_amount
        user_profile.balance += Decimal(difference)
    user_profile.save()


@receiver(post_delete, sender=Transaction)
def update_balance_on_transaction_delete(sender, instance, **kwargs):
    user_profile = UserProfile.objects.get(user=instance.user)
    user_profile.balance -= Decimal(instance.amount)
    user_profile.save()


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
