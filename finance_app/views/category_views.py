from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from finance_app.forms import (
    CategoryForm,
)
from finance_app.models import (
    Transaction,
    UserProfile,
    CategoryPreference,
    Category,
)
from finance_app.serializers import CategoryPreferenceSerializer
from django.db.models import Q
from .summary_views import parse_notifications


@login_required(login_url="login")
def categories_page(request):
    user_profile = UserProfile.objects.get(user=request.user)
    categories = CategoryPreference.objects.filter(user=request.user)

    notifications, show_notifications_modal = parse_notifications(request)

    return render(
        request,
        "categories.html",
        {
            "user_profile": user_profile,
            "categories": categories,
            "notifications": notifications,
            "show_notifications_modal": show_notifications_modal,
        },
    )


@login_required(login_url="login")
def create_category(request):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        form = CategoryForm(request.POST, user=request.user)

        if form.is_valid():
            preference = form.save()
            preference_data = CategoryPreferenceSerializer(preference).data
            return JsonResponse(
                {
                    "success": True,
                    "message": "Kategorie byla úspěšně vytvořena.",
                    "category_preference": preference_data,
                }
            )
        else:
            # ToDo all form errors
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse(
        {"success": False, "message": "Nesprávný typ požadavku."}, status=400
    )


@login_required(login_url="login")
def edit_category(request, category_preference_id):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        category_preference = get_object_or_404(
            CategoryPreference, id=category_preference_id, user=request.user
        )
        form = CategoryForm(
            request.POST, user=request.user, existing_instance=category_preference
        )

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
def delete_category(request, category_preference_id):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        category_preference = get_object_or_404(
            CategoryPreference, id=category_preference_id, user=request.user
        )

        default_category = Category.objects.filter(is_default=True).first()
        affected_transactions = Transaction.objects.filter(
            Q(user=request.user) & Q(category=category_preference.category)
        )
        updated_count = affected_transactions.update(category=default_category)

        category = category_preference.category
        category_preference.delete()

        if CategoryPreference.objects.filter(category=category).count() <= 0:
            category.delete()

        # ToDo do all inflections
        if updated_count < 1 or updated_count >= 5:
            transactions_inflection = "transakcí"
        else:
            transactions_inflection = "transakce"

        return JsonResponse(
            {
                "success": True,
                "message": (
                    f"Kategorie byla úspěšně smazána, {updated_count} {transactions_inflection} "
                    'bylo přiřazeno k výchozí kategorii "Ostatní".'
                ),
            }
        )

    return JsonResponse(
        {"success": False, "message": "Nesprávný typ požadavku."}, status=400
    )
