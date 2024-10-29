from django import forms
from django.contrib.auth import get_user_model
from finance_app.models import Transaction, Category, CategoryPreference, Budget
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy
from django.utils import timezone
import re
import logging

logger = logging.getLogger(__name__)


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Jméno")
    last_name = forms.CharField(max_length=30, required=True, label="Příjmení")
    email = forms.EmailField(required=True, label="Email")

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
        error_messages = {
            "username": {
                "unique": gettext_lazy("Toto uživatelské jméno je již používáno."),
            },
            "password_mismatch": gettext_lazy("Hesla se neshodují!"),
        }

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


class CreateTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount", "performed_at", "category", "name", "description"]

    def clean_performed_at(self):
        performed_at = self.cleaned_data.get("performed_at")
        if performed_at and performed_at > timezone.now():
            raise ValidationError("Datum provedení transakce nemůže být v budoucnosti.")
        return performed_at


class CreateCategoryForm(forms.Form):
    name = forms.CharField(label="Název kategorie", max_length=100, required=True)
    color = forms.CharField(label="Barva", max_length=7, required=True)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.category = None

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

        if category_name:
            # ToDo: Can be written with one database query - join
            self.category = Category.objects.filter(name=category_name).first()

            if (
                self.category
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

        if commit:
            preference.save()

        return self.category, preference


class CreateBudgetForm(forms.ModelForm):
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

    def clean_period_end(self):
        period_start = self.cleaned_data.get("period_start")
        period_end = self.cleaned_data.get("period_end")
        if period_end and period_start and period_end <= period_start:
            raise ValidationError("Konec období musí být po začátku období.")
        return period_end

    def save(self, commit=True):
        budget = super().save(commit=False)
        budget.owner = self.user
        if commit:
            budget.save()
            self.save_m2m()
        return budget
