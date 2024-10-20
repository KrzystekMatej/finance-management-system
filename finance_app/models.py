from django.db import models
from django.conf import settings


class UserProfileModel(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    global_notification_mode = models.CharField(
        max_length=10,
        choices=[
            ("NONE", "None"),
            ("APP", "App"),
            ("EMAIL", "Email"),
            ("APP_EMAIL", "App and Email"),
        ],
        default="APP",
    )


class CategoryModel(models.Model):
    # user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(UserProfileModel, blank=True)


class CategoryPreferenceModel(models.Model):
    color = models.CharField(max_length=7)
    user = models.ForeignKey(UserProfileModel, on_delete=models.CASCADE)
    category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE)


class TransactionModel(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    performed_at = models.DateTimeField()
    category = models.ForeignKey(CategoryModel, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(UserProfileModel, on_delete=models.CASCADE)


class RecurringTransactionModel(TransactionModel):
    interval_seconds = models.PositiveIntegerField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)


class BudgetModel(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(UserProfileModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    exceeded_at = models.DateTimeField(null=True, blank=True)
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()
    description = models.TextField(blank=True)

    # category_names = JSONField(default=list, blank=True)
    categories = models.ManyToManyField(CategoryModel, blank=True)


class SharedBudgetModel(models.Model):
    budget = models.ForeignKey(BudgetModel, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(UserProfileModel, on_delete=models.CASCADE)
    permission = models.CharField(
        max_length=10, choices=[("VIEW", "View"), ("EDIT", "Edit")], default="VIEW"
    )
    role = models.CharField(
        max_length=12,
        choices=[("PARTICIPANT", "Participant"), ("OBSERVER", "Observer")],
        default="PARTICIPANT",
    )
    on_exceeded = models.BooleanField(default=True)
    on_limit_change = models.BooleanField(default=True)
    on_transaction = models.BooleanField(default=True)
    notification_mode = models.CharField(
        max_length=10,
        choices=[
            ("NONE", "None"),
            ("APP", "App"),
            ("EMAIL", "Email"),
            ("APP_EMAIL", "App and Email"),
        ],
        default="APP",
    )


class NotificationModel(models.Model):
    receiver = models.ForeignKey(UserProfileModel, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    message = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
