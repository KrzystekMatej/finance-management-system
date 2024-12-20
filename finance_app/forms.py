from django import forms
from django.contrib.auth import get_user_model

from finance_app.logging import logger
from finance_app.models import (
    Transaction,
    Category,
    CategoryPreference,
    Budget,
    RecurringTransaction,
    TimeInterval,
    SharedBudget,
    UserProfile,
)
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy
from django.utils import timezone
import re
from django.db import transaction as db_transaction
from django.core.exceptions import ObjectDoesNotExist


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("Tento email je již používaný.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": gettext_lazy("Nesprávné uživatelské jméno nebo heslo."),
        "inactive": gettext_lazy("Tento účet je neaktivní."),
    }


class FilterByDateForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=False,
        label="Start Date",
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=False,
        label="End Date",
    )
    min_amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        required=False,
        label="Minimum Amount",
    )
    max_amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        required=False,
        label="Maximum Amount",
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Categories",
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categories = CategoryPreference.objects.filter(user=user).values_list(
            "category", flat=True
        )
        self.fields["categories"].queryset = Category.objects.filter(
            id__in=categories
        ).order_by("name")


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount", "performed_at", "category", "name", "description"]

    def __init__(self, *args, user=None, existing_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.existing_instance = existing_instance

    def clean_performed_at(self):
        performed_at = self.cleaned_data.get("performed_at")
        if performed_at:
            performed_at = (
                timezone.make_aware(performed_at)
                if timezone.is_naive(performed_at)
                else performed_at
            )
            if performed_at > timezone.now():
                raise ValidationError("Datum nemůže být v budoucnosti.")
        return performed_at

    def save(self, commit=True):
        with db_transaction.atomic():
            instance = super().save(commit=False)

            if isinstance(instance, RecurringTransaction):
                if commit:
                    instance.save()
                return instance

            user_profile = UserProfile.objects.select_for_update().get(user=self.user)

            if instance.pk is None:
                instance.user = self.user
                user_profile.balance += instance.amount
            else:
                original_amount = Transaction.objects.get(pk=instance.pk).amount
                difference = instance.amount - original_amount
                user_profile.balance += difference

            if commit:
                user_profile.save()
                instance.save()

            self.balance = user_profile.balance
            return instance


class RecurringTransactionForm(TransactionForm):
    INTERVAL_CHOICES = [
        (TimeInterval.DAY.value, gettext_lazy("Den")),  # Day
        (TimeInterval.WEEK.value, gettext_lazy("Týden")),  # Week
        (TimeInterval.MONTH.value, gettext_lazy("Měsíc")),  # Month
        (TimeInterval.YEAR.value, gettext_lazy("Rok")),  # Year
    ]

    interval = forms.ChoiceField(
        choices=[
            (interval.value, interval.name.capitalize()) for interval in TimeInterval
        ],
        required=True,
    )

    class Meta(TransactionForm.Meta):
        model = RecurringTransaction

    def save(self, commit=True):
        with db_transaction.atomic():
            instance = super().save(commit=False)

            instance.user = self.user
            instance._interval = self.cleaned_data["interval"]

            if not instance.next_performed_at:
                instance.next_performed_at = instance.performed_at

            user_profile = UserProfile.objects.select_for_update().get(user=self.user)

            if commit:
                instance.save()
                instance.process(user_profile)

            self.balance = user_profile.balance
            return instance


class CategoryForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    color = forms.CharField(max_length=7, required=True)

    def __init__(self, *args, user=None, existing_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.category = None
        self.existing_preference_instance = existing_instance

    def clean_color(self):
        color = self.cleaned_data.get("color")
        if not re.match(r"^#[0-9A-Fa-f]{6}$", color):
            raise ValidationError(
                "Barva musí být ve formátu hexadecimálního kódu, např. #RRGGBB."
            )
        return color

    def clean(self):
        cleaned_data = super().clean()
        category_name = cleaned_data.get("name")

        if (
            self.existing_preference_instance is not None
            and self.existing_preference_instance.category.is_default
        ):
            self.category = self.existing_preference_instance.category

            if self.category.name != category_name:
                raise ValidationError("Názvy výchozích kategorií nelze změnit.")
        else:
            # ToDo: Can be written with one database query - join
            self.category = Category.objects.filter(name=category_name).first()

            if (
                self.existing_preference_instance is None
                and self.category
                and CategoryPreference.objects.filter(
                    user=self.user, category=self.category
                ).exists()
            ):
                raise ValidationError("Tuto kategorii už máte vytvořenou.")

        return cleaned_data

    def save(self, commit=True):
        if not self.category:
            self.category = Category.objects.create(name=self.cleaned_data["name"])

        preference = CategoryPreference(
            color=self.cleaned_data["color"], user=self.user, category=self.category
        )

        if self.existing_preference_instance is not None:
            transactions = Transaction.objects.filter(
                user=self.user, category=self.existing_preference_instance.category
            )
            transactions.update(category=self.category)
            preference.id = self.existing_preference_instance.id

        if commit:
            preference.save()

        return preference


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = [
            "name",
            "limit",
            "period_start",
            "period_end",
            "description",
            "categories",
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_limit(self):
        limit = self.cleaned_data.get("limit")
        if limit < 0:
            raise ValidationError("Limit nemůže být záporný.")
        return limit

    def clean_period_end(self):
        period_start = self.cleaned_data.get("period_start")
        period_end = self.cleaned_data.get("period_end")
        if period_end and period_start and period_end <= period_start:
            raise ValidationError("Konec období musí být po začátku období.")
        return period_end

    def clean_categories(self):
        categories = self.cleaned_data.get("categories")
        if not categories:
            raise ValidationError("Musíte vybrat alespoň jednu kategorii.")
        return categories

    def save(self, commit=True):
        with db_transaction.atomic():
            budget = super().save(commit=False)
            budget.owner = self.user
            if commit:
                is_new = budget.pk is None
                budget.save()
                self.save_m2m()
                if is_new:
                    SharedBudget.objects.create(
                        user=budget.owner, budget=budget, _permission="EDIT"
                    )
        return budget


class SharedBudgetForm(forms.ModelForm):
    username = forms.CharField(max_length=30, required=True)

    class Meta:
        model = SharedBudget
        fields = ["_permission", "_role", "_notification_mode"]

    def __init__(self, *args, budget=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.budget = budget

    def clean_username(self):
        username = self.cleaned_data.get("username")
        try:
            self.user = get_user_model().objects.get(username=username)
        except ObjectDoesNotExist:
            raise ValidationError("Uživatel s tímto jménem neexistuje.")
        user_shared_budget = SharedBudget.objects.filter(
            user=self.user, budget=self.budget
        )
        if user_shared_budget:
            raise ValidationError("Uživatel již je členem tohoto sdíleného rozpočtu.")

    def save(self, commit=True):
        with db_transaction.atomic():
            instance = super().save(commit=False)
            instance.user = self.user
            instance.budget = self.budget

            budget_categories = self.budget.categories.all()
            user_categories = CategoryPreference.objects.filter(
                user=self.user
            ).values_list("category", flat=True)

            new_preferences = []
            for category in budget_categories:
                if category.id not in user_categories:
                    new_preferences.append(
                        CategoryPreference(user=self.user, category=category)
                    )
                    logger.info(category.id)

            if new_preferences:
                CategoryPreference.objects.bulk_create(new_preferences)

            if commit:
                instance.save()
            return instance
