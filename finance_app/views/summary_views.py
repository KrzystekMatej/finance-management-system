from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from finance_app.models import (
    Transaction,
    UserProfile,
    Category,
    CategoryPreference,
    Budget,
)
from finance_app.serializers import CategoryPreferenceSerializer
from finance_app.forms import FilterByDateForm


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


@login_required(login_url="login")
def filter(request):
    form = FilterByDateForm(
        request.user, request.GET or None
    )  # Pass the user to the form
    transactions = Transaction.objects.filter(user_id=request.user.id)

    if form.is_valid():
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        min_amount = form.cleaned_data.get("min_amount")
        max_amount = form.cleaned_data.get("max_amount")
        selected_categories = form.cleaned_data.get("categories")

        # date range filter
        if start_date:
            transactions = transactions.filter(performed_at__gte=start_date)
        if end_date:
            transactions = transactions.filter(performed_at__lte=end_date)

        # amount range filter
        if min_amount is not None:
            transactions = transactions.filter(amount__gte=min_amount)
        if max_amount is not None:
            transactions = transactions.filter(amount__lte=max_amount)

        # category filter
        if selected_categories:
            transactions = transactions.filter(category__in=selected_categories)

    category_preferences = CategoryPreference.objects.filter(user=request.user)
    color_map = {pref.category_id: pref.color for pref in category_preferences}
    for transaction in transactions:
        category_id = transaction.category.id if transaction.category else None
        transaction.category_color = color_map.get(category_id, "#fff")

    categories = CategoryPreference.objects.filter(user=request.user).values_list(
        "category", flat=True
    )

    context = {
        "transactions": transactions,
        "categories": Category.objects.filter(id__in=categories).order_by("name"),
        "form": form,
    }

    return render(request, "filter.html", context)


@login_required(login_url="login")
def main_page(request):
    categories = CategoryPreference.objects.filter(user=request.user)

    context = {
        "monthly_summaries": get_monthly_summaries(
            request, Transaction.objects.filter(user_id=request.user.id)
        ),
        "categories": categories,
        "categories_json": CategoryPreferenceSerializer(categories, many=True).data,
        "user_profile": UserProfile.objects.get(user=request.user),
        "budgets": Budget.objects.filter(owner=request.user),
    }

    return render(request, "main_page.html", context)
