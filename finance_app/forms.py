from django import forms
from django.contrib.auth import get_user_model
from finance_app.models import Transaction, Category
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password1", "password2"]
        error_messages = {
            "username": {
                "unique": _("Toto uživatelské jméno je již používáno."),
            },
            "password_mismatch": _("Hesla se neshodují!"),
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
        "invalid_login": _("Nesprávné uživatelské jméno nebo heslo."),
        "inactive": _("Tento účet je neaktivní."),
    }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount", "performed_at", "category", "name", "description"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
