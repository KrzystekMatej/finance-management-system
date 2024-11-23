from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from finance_app.forms import (
    RegistrationForm,
    LoginForm,
)
from verify_email.email_handler import ActivationMailManager


def register_success(request):
    return render(request, "register_success.html")


def register_page(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            inactive_user = form.save(commit=False)
            inactive_user.is_active = False
            inactive_user.save()

            # Send verification email with the correct domain and full URL
            ActivationMailManager.send_verification_link(
                inactive_user=inactive_user, form=form, request=request
            )
            return redirect("register-success")
    else:
        form = RegistrationForm()

    return render(request, "register.html", {"form": form})


def login_page(request):
    if request.user.is_authenticated:
        return redirect("main_page")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("main_page")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


@login_required(login_url="login")
def logout_page(request):
    logout(request)
    return render(request, "logout.html")
