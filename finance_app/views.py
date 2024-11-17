from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from finance_app.forms import (
    RegistrationForm,
    LoginForm,
    CreateTransactionForm,
    CreateCategoryForm,
    CreateBudgetForm,
)
from finance_app.models import Transaction, UserProfile, CategoryPreference, Budget
import logging
from verify_email.email_handler import ActivationMailManager

logger = logging.getLogger(__name__)


def split_transactions_by_month(transactions):
    monthly_summaries = []
    current_month = None
    current_month_transactions = []

    for transaction in transactions:
        month = transaction.performed_at.strftime("%Y-%m")

        if month != current_month:
            if current_month_transactions:
                monthly_summaries.append(current_month_transactions)
            current_month_transactions = []
            current_month = month

        current_month_transactions.append(transaction)

    if current_month_transactions:
        monthly_summaries.append(current_month_transactions)

    return monthly_summaries


def get_monthly_summaries(request, all_transactions):
    transactions_by_month = split_transactions_by_month(all_transactions)

    month_names = [
        "Leden",
        "Únor",
        "Březen",
        "Duben",
        "Květen",
        "Červen",
        "Červenec",
        "Srpen",
        "Září",
        "Říjen",
        "Listopad",
        "Prosinec",
    ]
    monthly_summaries = []

    category_preferences = CategoryPreference.objects.filter(user=request.user)
    color_map = {pref.category_id: pref.color for pref in category_preferences}

    for month_transactions in transactions_by_month:
        year = month_transactions[0].performed_at.year
        month = month_names[month_transactions[0].performed_at.month - 1]

        incoming_totals = {}
        outcoming_totals = {}

        for transaction in month_transactions:
            amount = float(transaction.amount)
            category_name = transaction.category.name
            category_id = transaction.category.id if transaction.category else None

            transaction.category_color = color_map.get(category_id, "#fff")

            if amount >= 0:
                if category_name not in incoming_totals:
                    incoming_totals[category_name] = 0
                incoming_totals[category_name] += amount
            else:
                if category_name not in outcoming_totals:
                    outcoming_totals[category_name] = 0
                outcoming_totals[category_name] += amount

        aggregated_incoming = [
            {"name": cat, "total": total} for cat, total in incoming_totals.items()
        ]
        aggregated_outcoming = [
            {"name": cat, "total": total} for cat, total in outcoming_totals.items()
        ]

        total_income = sum(incoming_totals.values())
        total_expenses = sum(abs(total) for total in outcoming_totals.values())

        monthly_summaries.append(
            {
                "year": year,
                "month": month,
                "income": total_income,
                "expanses": total_expenses,
                "transactions": month_transactions,
                "aggregated_data": {
                    "incoming": aggregated_incoming,
                    "outcoming": aggregated_outcoming,
                },
            }
        )

    return monthly_summaries


def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    user_profile = UserProfile.objects.get(user=request.user)
    categories = CategoryPreference.objects.filter(user=request.user)
    return render(
        request,
        "transaction_detail.html",
        {
            "transaction": transaction,
            "user_profile": user_profile,
            "categories": categories,
        },
    )


def categories_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    categories = CategoryPreference.objects.filter(user=request.user)
    return render(
        request,
        "categories.html",
        {
            "user_profile": user_profile,
            "categories": categories,
        },
    )


def budgets_details(request):
    user_profile = UserProfile.objects.get(user=request.user)
    budgets = Budget.objects.filter(owner=request.user)
    categories = CategoryPreference.objects.filter(user=request.user)
    return render(
        request,
        "budgets_details.html",
        {
            "user_profile": user_profile,
            "budgets": budgets,
            "categories": categories,
        },
    )


@login_required(login_url="login")
def main_page(request):
    context = {
        "monthly_summaries": get_monthly_summaries(
            request, Transaction.objects.filter(user_id=request.user.id)
        ),
        "categories": CategoryPreference.objects.filter(user=request.user),
        "user_profile": UserProfile.objects.get(user=request.user),
        "budgets": Budget.objects.filter(owner=request.user),
    }

    return render(request, "main_page.html", context)


@login_required(login_url="login")
def create_transaction(request):
    if request.method == "POST":
        form = CreateTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True})
            return redirect("main_page")
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "errors": "Invalid request method."})


@login_required(login_url="login")
def create_category(request):
    if request.method == "POST":
        form = CreateCategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category, preference = form.save()
            return JsonResponse({"success": True, "category_name": category.name})
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "errors": "Invalid request method."})


@login_required(login_url="login")
def create_budget(request):
    if request.method == "POST":
        form = CreateBudgetForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "errors": "Invalid request method."})


@login_required(login_url="login")
def budget_view(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, owner=request.user)

    transactions_for_budget = Transaction.objects.filter(
        user=request.user, category__in=budget.categories.all()
    )

    context = {
        "monthly_summaries": get_monthly_summaries(request, transactions_for_budget),
        "categories": CategoryPreference.objects.filter(user=request.user),
        "user_profile": UserProfile.objects.get(user=request.user),
        "budgets": Budget.objects.filter(owner=request.user),
    }

    return render(request, "main_page.html", context)


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
            return redirect("login")
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
