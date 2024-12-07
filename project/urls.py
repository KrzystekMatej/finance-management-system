from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from finance_app.views.auth_views import (
    login_page,
    register_page,
    logout_page,
    register_success,
)
from finance_app.views.summary_views import filter_page, main_page
from finance_app.views.guide_views import tutorial
from finance_app.views.transaction_views import (
    create_transaction,
    transaction_detail,
    delete_transaction,
)
from finance_app.views.category_views import (
    categories_page,
    create_category,
    edit_category,
    delete_category,
)
from finance_app.views.budget_views import (
    budgets_page,
    budget_view,
    create_budget,
    edit_budget,
    delete_budget,
)
from finance_app.views.recurring_transaction_views import (
    recurring_transactions_page,
)

urlpatterns = [
    # auth views
    path("admin/", admin.site.urls),
    path("login/", login_page, name="login"),
    path("logout/", logout_page, name="logout"),
    path("register/", register_page, name="register"),
    path("register-success/", register_success, name="register-success"),
    path("verification/", include("verify_email.urls")),
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
    # summary views
    path("filter/", filter_page, name="filter"),
    path("", main_page, name="main_page"),
    # guide views
    path("tutorial/", tutorial, name="tutorial"),
    # transaction views
    path("create-transaction/", create_transaction, name="create-transaction"),
    path(
        "transaction/<int:transaction_id>/",
        transaction_detail,
        name="transaction_detail",
    ),
    path(
        "delete-transaction/<int:transaction_id>/",
        delete_transaction,
        name="delete-transaction",
    ),
    # category views
    path("categories/", categories_page, name="categories"),
    path("create-category/", create_category, name="create-category"),
    path(
        "edit-category/<int:category_preference_id>/",
        edit_category,
        name="edit-category",
    ),
    path(
        "delete-category/<int:category_preference_id>/",
        delete_category,
        name="delete-category",
    ),
    # budget views
    path("budgets/", budgets_page, name="budgets"),
    path("budget/<int:budget_id>/", budget_view, name="budget_view"),
    path("create-budget/", create_budget, name="create-budget"),
    path("edit-budget/<int:budget_id>/", edit_budget, name="edit-budget"),
    path("delete-budget/<int:budget_id>/", delete_budget, name="delete-budget"),
    # recurring transaction
    path(
        "recurring-transactions/",
        recurring_transactions_page,
        name="recurring_transactions",
    ),
]
