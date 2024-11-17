"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from finance_app import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", views.login_page, name="login"),
    path("admin/", admin.site.urls),
    path("register/", views.register_page, name="register"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "password-reset-done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("verification/", include("verify_email.urls")),
    path("logout/", views.logout_page, name="logout"),
    path("create-category/", views.create_category, name="create-category"),
    path("create-transaction/", views.create_transaction, name="create-transaction"),
    path("create-budget/", views.create_budget, name="create-budget"),
    path("", views.main_page, name="main_page"),
    path("budget/<int:budget_id>/", views.budget_view, name="budget_view"),
    path(
        "transaction/<int:transaction_id>/",
        views.transaction_detail,
        name="transaction_detail",
    ),
]
