from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from finance_app.models import RecurringTransaction, UserProfile, CategoryPreference


@login_required(login_url="login")
def recurring_transactions_page(request):
    user_profile = UserProfile.objects.get(user=request.user)
    categories = CategoryPreference.objects.filter(user=request.user)
    recurring_transactions = RecurringTransaction.objects.filter(user=request.user)
    return render(
        request,
        "recurring_transaction.html",
        {
            "user_profile": user_profile,
            "recurring_transactions": recurring_transactions,
            "categories": categories,
        },
    )
