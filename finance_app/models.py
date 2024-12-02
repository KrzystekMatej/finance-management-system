from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.conf import settings
from enum import Enum
from calendar import monthrange
from django.db.models import Q


class NotificationMode(Enum):
    NONE = "NONE"
    APP = "APP"
    EMAIL = "EMAIL"
    APP_EMAIL = "APP_EMAIL"


class BudgetRole(Enum):
    PARTICIPANT = "PARTICIPANT"
    OBSERVER = "OBSERVER"


class BudgetPermission(Enum):
    VIEW = "VIEW"
    EDIT = "EDIT"


class TimeInterval(Enum):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    _global_notification_mode = models.CharField(
        max_length=10,
        choices=[(mode.value, mode.name.capitalize()) for mode in NotificationMode],
        default=NotificationMode.APP.value,
    )

    @property
    def global_notification_mode(self):
        return NotificationMode(self._global_notification_mode)

    @global_notification_mode.setter
    def global_notification_mode(self, enum_value):
        self._global_notification_mode = enum_value.value


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    is_default = models.BooleanField(default=False)


class CategoryPreference(models.Model):
    color = models.CharField(max_length=7)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Transaction(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    performed_at = models.DateTimeField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-performed_at"]

    @staticmethod
    def get_non_recurring_transactions(user):
        non_recurring_transactions = Transaction.objects.filter(
            Q(user=user) & ~Q(recurringtransaction__isnull=False)
        )
        return non_recurring_transactions

    @staticmethod
    def get_recurring_transactions(user):
        recurring_transactions = Transaction.objects.filter(
            Q(user=user) & ~Q(recurringtransaction__isnull=True)
        )
        return recurring_transactions


class RecurringTransaction(Transaction):
    _interval = models.CharField(
        max_length=10,
        choices=[
            (interval.value, interval.name.capitalize()) for interval in TimeInterval
        ],
        default=TimeInterval.MONTH.value,
    )
    next_performed_at = models.DateTimeField()

    @property
    def interval(self):
        return TimeInterval(self._interval)

    @interval.setter
    def interval(self, enum_value):
        self._interval = enum_value.value

    @staticmethod
    def get_next_date(base_date, interval):
        match interval:
            case TimeInterval.DAY:
                return base_date + timedelta(days=1)
            case TimeInterval.WEEK:
                return base_date + timedelta(weeks=1)
            case TimeInterval.MONTH:
                next_month = (base_date.month % 12) + 1
                year = base_date.year + (1 if next_month == 1 else 0)
                last_day_of_next_month = monthrange(year, next_month)[1]

                day = min(base_date.day, last_day_of_next_month)

                return base_date.replace(year=year, month=next_month, day=day)
            case TimeInterval.YEAR:
                try:
                    return base_date.replace(year=base_date.year + 1)
                except ValueError:
                    return base_date.replace(year=base_date.year + 1, day=28)

    def process(self):
        current_time = timezone.now()

        generated_transactions = []
        # generated_recurrent_transactions = []

        while self.next_performed_at < current_time:
            generated_transactions.append(
                Transaction(
                    name=self.name,
                    amount=self.amount,
                    performed_at=self.next_performed_at,
                    user=self.user,
                    category=self.category,
                    # recurringtransaction=self
                )
            )

            # generated_recurrent_transactions.append(
            #    RecurringTransaction(
            #        _interval=self._interval,
            #        performed_at=self.next_performed_at,
            #    )
            # )

            self.next_performed_at = self.get_next_date(
                self.next_performed_at, self.interval
            )

        if generated_transactions:
            Transaction.objects.bulk_create(generated_transactions)
        # RecurringTransaction.objects.bulk_create(generated_recurrent_transactions)

        self.save()


class Budget(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    exceeded_at = models.DateTimeField(null=True, blank=True)
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, blank=True)


class SharedBudget(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    _permission = models.CharField(
        max_length=10,
        choices=[
            (permission.value, permission.name.capitalize())
            for permission in BudgetPermission
        ],
        default=BudgetPermission.VIEW.value,
    )

    _role = models.CharField(
        max_length=20,
        choices=[(role.value, role.name.capitalize()) for role in BudgetRole],
        default=BudgetRole.PARTICIPANT.value,
    )

    on_exceeded = models.BooleanField(default=True)
    on_limit_change = models.BooleanField(default=True)
    on_transaction = models.BooleanField(default=True)
    _notification_mode = models.CharField(
        max_length=10,
        choices=[(mode.value, mode.name.capitalize()) for mode in NotificationMode],
        default=NotificationMode.APP.value,
    )

    @property
    def permission(self):
        return BudgetPermission(self._permission)

    @permission.setter
    def permission(self, enum_value):
        self._permission = enum_value.value

    @property
    def role(self):
        return BudgetRole(self._role)

    @role.setter
    def role(self, enum_value):
        self._role = enum_value.value

    @property
    def notification_mode(self):
        return NotificationMode(self._notification_mode)

    @notification_mode.setter
    def notification_mode(self, enum_value):
        self._notification_mode = enum_value.value


class Notification(models.Model):
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    message = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
