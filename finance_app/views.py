from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from finance_app.forms import RegistrationForm, LoginForm, TransactionForm, CategoryForm
from finance_app.models import (
    Transaction,
    UserProfile,
    CategoryPreference,
)

def get_monthly_summaries(request):
    # Fetch all transactions for the user
    all_transactions = get_transactions_by_month(
        Transaction.objects.filter(user_id=request.user.id)
    )

    month_names = [
        "Leden", "Únor", "Březen", "Duben", "Květen", "Červen", 
        "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"
    ]

    monthly_summaries = []

    for month_transactions in all_transactions:
        year = month_transactions[0].performed_at.year
        month = month_names[month_transactions[0].performed_at.month - 1]

        incoming_totals = {}
        outcoming_totals = {}

        for transaction in month_transactions:
            amount = float(transaction.amount)
            print(amount)
            category_name = transaction.category.name
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

        monthly_summaries.append({
            "year": year,
            "month": month,
            "income": total_income,
            "expanses": total_expenses,
            "transactions": month_transactions,
            "aggregated_data": {
                "incoming": aggregated_incoming,
                "outcoming": aggregated_outcoming,
            }
        })

    return monthly_summaries


def get_transactions_by_month(transactions):
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

@login_required(login_url="login")
def main_page(request):
    context = {
        "monthly_summaries": get_monthly_summaries(request),
        "categories": CategoryPreference.objects.filter(user_id=request.user.id),
        "user_profile": UserProfile.objects.get(id=request.user.id),
    }

    return render(request, "main_page.html", context)


def create_transaction(request):

    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user_id = request.user.id
            transaction.save()
            return redirect("main_page")
        else:
            print(form.errors)
    else:
        form = TransactionForm()

    # Render the form with categories on both GET and POST
    return render(
        request,
        "modal_create_transaction.html",
        {
            "form": form,
            "categories": CategoryPreference.objects.filter(user_id=request.user.id),
        },
    )


def create_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.save()
            # main_page(request)
            return redirect("main_page")
        else:
            print(form.errors)


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
