from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from finance_app.forms import (
    BudgetForm,
)
from .summary_views import get_monthly_summaries, parse_notifications
from finance_app.models import (
    Transaction,
    UserProfile,
    CategoryPreference,
    Budget,
    SharedBudget,
)
from ..logging import logger


@login_required(login_url="login")
def budgets_page(request):
    user_profile = UserProfile.objects.get(user=request.user)

    budgets = Budget.objects.filter(sharedbudget__user=request.user)

    # Fallback if shared budget fails. Idk what shared budget is even
    # meant to do here, but it sure isn't working correctly
    if not budgets.exists():
        budgets = Budget.objects.filter(owner=request.user)

    categories = CategoryPreference.objects.filter(user=request.user)

    shared_budgets = SharedBudget.objects.filter(budget__in=budgets).select_related(
        "user"
    )

    notifications, show_notifications_modal = parse_notifications(request, budgets)

    return render(
        request,
        "budgets.html",
        {
            "user_profile": user_profile,
            "budgets": budgets,
            "categories": categories,
            "shared_budgets": shared_budgets,
            "notifications": notifications,
            "show_notifications_modal": show_notifications_modal,
        },
    )


@login_required(login_url="login")
def budget_view(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, owner=request.user)

    transactions_for_budget = Transaction.objects.filter(
        user=request.user, category__in=budget.categories.all()
    )

    notifications, show_notifications_modal = parse_notifications(
        request, Budget.objects.filter(owner=request.user)
    )

    context = {
        "monthly_summaries": get_monthly_summaries(request, transactions_for_budget),
        "categories": CategoryPreference.objects.filter(user=request.user),
        "user_profile": UserProfile.objects.get(user=request.user),
        "budgets": Budget.objects.filter(owner=request.user),
        "notifications": notifications,
        "show_notifications_modal": show_notifications_modal,
    }

    return render(request, "main_page.html", context)


@login_required(login_url="login")
def create_budget(request):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):

        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse(
                {"success": True, "message": "Rozpočet byl úspěšně vytvořen."}
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse(
        {"success": False, "message": "Nesprávný typ požadavku."}, status=400
    )


@login_required(login_url="login")
def edit_budget(request, budget_id):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        logger.info(request.POST)
        budget = get_object_or_404(Budget, id=budget_id, owner=request.user)
        form = BudgetForm(request.POST, user=request.user, instance=budget)
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
def delete_budget(request, budget_id):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        budget = get_object_or_404(Budget, id=budget_id, owner=request.user)

        budget.delete()

        return JsonResponse(
            {"success": True, "message": "Rozpočet byl úspěšně smazán."}
        )

    return JsonResponse(
        {"success": False, "message": "Nesprávný typ požadavku."}, status=400
    )
