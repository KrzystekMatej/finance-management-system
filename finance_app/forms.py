from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        required=True
    )  # Fixes email not giving error when not filled
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Hesla se neshodují!")

        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, label=("Password"))

    # def clean(self):
    #     cleaned_data = super().clean()
    #     email = cleaned_data.get("email")
    #     password = cleaned_data.get("password")
    #
    #     if email and password:
    #          user = authenticate(username=email, password=password)
    #          if user is None:
    #              raise forms.ValidationError("Invalid email or password.")
    #          elif not user.is_active:
    #              raise forms.ValidationError("This account is inactive.")

    #     return cleaned_data
