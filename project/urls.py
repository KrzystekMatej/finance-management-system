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
from django.urls import path
from finance_app import views

urlpatterns = [
    path("login/", views.login_page, name="login"),
    path("admin/", admin.site.urls),
    path("register/", views.register_page, name="register"),
    path("logout/", views.logout_page, name="logout"),
    path("create-category/", views.create_category, name="create-category"),
    path("create-transaction/", views.create_transaction, name="create-transaction"),
    path("create-budget/", views.create_budget, name="create-budget"),
    path("", views.main_page, name="main_page"),
    path("budget/<int:budget_id>/", views.budget_view, name="budget_view"),
]
