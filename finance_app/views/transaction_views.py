from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from finance_app.forms import TransactionForm, RecurringTransactionForm
from finance_app.models import Transaction, UserProfile, CategoryPreference


@login_required(login_url="login")
def create_transaction(request):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        if request.POST.get("is-recurring") == "on":
            form = RecurringTransactionForm(request.POST)
        else:
            form = TransactionForm(request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return JsonResponse(
                {"success": True, "message": "Transakce byla úspěšně vytvořena."}
            )
        else:
            # ToDo all form errors
            return JsonResponse(
                {"success": False, "message": form.non_field_errors()}, status=400
            )

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

        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return JsonResponse(
                {"success": True, "message": "Vaše změny byly uloženy."}
            )
        else:
            # ToDo all form errors
            return JsonResponse(
                {"success": False, "message": form.non_field_errors()}, status=400
            )

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
        transaction.delete()
        return JsonResponse(
            {"success": True, "message": "Transakce byla úspěšně smazána."}
        )
    return JsonResponse(
        {"success": False, "message": "Nesprávný typ požadavku."}, status=400
    )
