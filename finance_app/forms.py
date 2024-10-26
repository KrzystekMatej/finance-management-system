from django import forms
from django.contrib.auth.models import User
from finance_app.models import UserProfile
from django.core.exceptions import ValidationError


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(required=True, max_length=150, label="Username")
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 8:
            raise ValidationError("Heslo musí obsahovat alespoň 8 znaků.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Hesla se neshodují!")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            UserProfile.objects.create(user=user)
        return user


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
