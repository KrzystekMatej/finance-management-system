from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from finance_app.models import RecurringTransaction, UserProfile, CategoryPreference
from django.http import JsonResponse
from finance_app.forms import RecurringTransactionForm


@login_required(login_url="login")
def recurring_transactions_page(request):
    user_profile = UserProfile.objects.get(user=request.user)
    categories = CategoryPreference.objects.filter(user=request.user)
    recurring_transactions = RecurringTransaction.objects.filter(user=request.user)
    return render(
        request,
        "recurring_transactions.html",
        {
            "user_profile": user_profile,
            "recurring_transactions": recurring_transactions,
            "categories": categories,
        },
    )


@login_required(login_url="login")
def edit_recurring_transaction(request, transaction_id):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        transaction = get_object_or_404(
            RecurringTransaction, id=transaction_id, user=request.user
        )

        form = RecurringTransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return JsonResponse(
                {"success": True, "message": "Vaše změny byly uloženy."}
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse(
        {"success": False, "message": "Nesprávný typ požadavku."}, status=400
    )


@login_required(login_url="login")
def delete_recurring_transaction(request, transaction_id):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        transaction = get_object_or_404(
            RecurringTransaction, id=transaction_id, user=request.user
        )

        transaction.delete()
        return JsonResponse(
            {"success": True, "message": "Rekurentní transakce byla úspěšně smazána."}
        )
    return JsonResponse(
        {"success": False, "message": "Nesprávný typ požadavku."}, status=400
    )
