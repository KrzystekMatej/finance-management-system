from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from finance_app.forms import (
    RegistrationForm,
    LoginForm,
    CreateTransactionForm,
    CreateCategoryForm,
)
from finance_app.models import (
    Transaction,
    UserProfile,
    CategoryPreference,
    Budget,
)
import logging

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


def get_monthly_summaries(request):
    all_transactions = split_transactions_by_month(
        Transaction.objects.filter(user_id=request.user.id)
    )
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

    for month_transactions in all_transactions:
        year = month_transactions[0].performed_at.year
        month = month_names[month_transactions[0].performed_at.month - 1]
        income = sum(t.amount for t in month_transactions if t.amount >= 0)
        expanses = sum(t.amount for t in month_transactions if t.amount < 0)
        transactions = month_transactions
        monthly_summaries.append(
            {
                "year": year,
                "month": month,
                "income": income,
                "expanses": expanses,
                "transactions": transactions,
            }
        )

    return monthly_summaries


@login_required(login_url="login")
def main_page(request):
    context = {
        "monthly_summaries": get_monthly_summaries(request),
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
    else:
        form = CreateTransactionForm()

    # TODO: optional - redirect to main page with transaction modal window
    return redirect("main_page")


@login_required(login_url="login")
def create_category(request):
    if request.method == "POST":
        form = CreateCategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category, preference = form.save()
            return JsonResponse({"success": True, "category_name": category.name})
        return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = CreateCategoryForm()

    # TODO: optional - redirect to main page with category modal window
    return redirect("main_page")


def register_page(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
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
