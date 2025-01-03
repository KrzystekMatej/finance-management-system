from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from finance_app.forms import TransactionForm, RecurringTransactionForm
from finance_app.models import Transaction, UserProfile, CategoryPreference
from django.db import transaction as db_transaction


@login_required(login_url="login")
def create_transaction(request):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        if request.POST.get("is_recurring") == "on":
            form = RecurringTransactionForm(request.POST, user=request.user)
        else:
            form = TransactionForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
            return JsonResponse(
                {
                    "success": True,
                    "message": "Transakce byla úspěšně vytvořena.",
                    "balance": form.balance,
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse(
        {"success": False, "message": "Nesprávný typ požadavku."}, status=400
    )


@login_required(login_url="login")
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    if request.method == "POST":
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse(
                {"success": False, "message": "Nesprávný typ požadavku."}, status=400
            )

        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse(
                {
                    "success": True,
                    "message": "Vaše změny byly uloženy.",
                    "balance": form.balance,
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

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


@login_required(login_url="login")
def delete_transaction(request, transaction_id):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        transaction = get_object_or_404(
            Transaction, id=transaction_id, user=request.user
        )
        user_profile = None

        with db_transaction.atomic():
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.balance -= transaction.amount
            user_profile.save()
            transaction.delete()

        return JsonResponse(
            {
                "success": True,
                "message": "Transakce byla úspěšně smazána.",
                "balance": user_profile.balance,
            }
        )
    return JsonResponse(
        {"success": False, "message": "Nesprávný typ požadavku."}, status=400
    )
