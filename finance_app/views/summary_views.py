from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from finance_app.models import (
    Transaction,
    UserProfile,
    CategoryPreference,
    Budget,
    RecurringTransaction,
    Notification,
)
from finance_app.serializers import CategoryPreferenceSerializer
from finance_app.forms import FilterByDateForm
from django.http import JsonResponse


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
            if (
                hasattr(transaction, "recurringtransaction")
                and transaction.recurringtransaction
            ):
                transaction.is_recurring = True
            else:
                transaction.is_recurring = False

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
def filter_page(request):
    process_recurring_transactions(request.user)

    form = FilterByDateForm(
        request.user, request.GET or None
    )  # Pass the user to the form
    transactions = Transaction.get_non_recurring_transactions(user=request.user)

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

    categories = (
        CategoryPreference.objects.filter(user=request.user)
        .select_related("category")
        .order_by("category__name")
    )

    context = {
        "transactions": transactions,
        "categories": categories,
        "categories_json": CategoryPreferenceSerializer(categories, many=True).data,
        "user_profile": UserProfile.objects.get(user=request.user),
        "form": form,
    }

    return render(request, "filter.html", context)


def process_recurring_transactions(user):
    transactions = RecurringTransaction.objects.filter(user=user)

    for transaction in transactions:
        transaction.process()


@login_required(login_url="login")
def main_page(request):
    process_recurring_transactions(request.user)

    categories = CategoryPreference.objects.filter(user=request.user)
    budgets = Budget.objects.filter(owner=request.user)
    monthly_summaries = get_monthly_summaries(
        request, Transaction.get_non_recurring_transactions(user=request.user)
    )

    notifications = []
    show_notifications_modal = False

    for budget in budgets:

        transactions = Transaction.objects.filter(
                user=request.user,
                category__in=budget.categories.all(),
                performed_at__range=(budget.period_start, budget.period_end)
            )

        # Expenses is absolute number, eq. sum outcoming 
        # transactions of -500 and -200 ends up as +700
        expenses = 0
        for transaction in transactions:
          # Transaction is outcoming
          if transaction.amount < 0:
            expenses += abs(float(transaction.amount))

        limit = float(budget.limit)
        # Breached the limit, create a notification entry
        if limit < expenses:
            # Unique string as identification
            subject = f"{budget.name}-{budget.created_at}"
            message = f'V rozpočtu "{budget.name}" jste překročili Váš nastavený limit ({limit} Kč v období \
              {budget.period_start.date()} až {budget.period_end.date()}) o {expenses - limit} Kč'
            notifications = Notification.objects.filter(receiver_id=request.user.id)
            print(message)
            is_duplicate = False
            for notification in notifications:
                if notification.subject == subject:
                    is_duplicate = True

            if not is_duplicate:
                Notification.objects.create(
                    receiver_id=request.user.id,
                    subject=subject,
                    message=message,
                    is_read=False,
                )
                # Send email - disabled so we don't spam possible test email addresses
                # Tested and it works
                # from django.core.mail import send_mail
                # subject = "Finance app - překročení limitu"
                # from_email = "systemfinance5@gmail.com"
                # recipient_list = [request.user.email]
                # send_mail(subject, message, from_email, recipient_list)

            # Not very effective, but it just works
            notifications = Notification.objects.filter(receiver_id=request.user.id)

            # If at least one notification is unread, show modal
            for notification in notifications:
                if notification.is_read is False:
                    show_notifications_modal = True
                    break

    context = {
        "monthly_summaries": monthly_summaries,
        "categories": categories,
        "categories_json": CategoryPreferenceSerializer(categories, many=True).data,
        "user_profile": UserProfile.objects.get(user=request.user),
        "budgets": budgets,
        "notifications": notifications,
        "show_notifications_modal": show_notifications_modal,
    }

    return render(request, "main_page.html", context)


def update_notification(request, pk):
    if request.method == "POST":
        notification = get_object_or_404(Notification, pk=pk)
        notification.is_read = True
        notification.save()
        return JsonResponse(
            {"status": "success", "message": "Notification updated successfully."}
        )
    return JsonResponse({"status": "error", "message": "Invalid request method."})


def mark_all_notifications_as_unread(request):
    if request.method == "POST" and request.user.is_authenticated:
        notifications = Notification.objects.filter(receiver=request.user)
        notifications.update(is_read=False)

        return JsonResponse(
            {"status": "success", "message": "All notifications set to unread."}
        )

    return JsonResponse(
        {"status": "error", "message": "Invalid request or user not authenticated."}
    )
