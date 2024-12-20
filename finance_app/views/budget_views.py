from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from finance_app.forms import BudgetForm, SharedBudgetForm
from .summary_views import get_monthly_summaries, parse_notifications
from finance_app.models import (
    Transaction,
    UserProfile,
    CategoryPreference,
    Budget,
    SharedBudget,
    BudgetRole,
    BudgetPermission,
    NotificationMode,
)
from django.db.models import Prefetch, Q
import json


def get_user_budgets_with_shared(user):
    shared_budget_prefetch = Prefetch(
        "sharedbudget_set",
        queryset=SharedBudget.objects.select_related("user"),
        to_attr="shared_budgets",
    )

    budgets = (
        Budget.objects.filter(Q(owner=user) | Q(sharedbudget__user=user))
        .distinct()
        .prefetch_related(shared_budget_prefetch)
    )

    for budget in budgets:
        user_shared_budget = next(
            (
                shared_budget
                for shared_budget in budget.shared_budgets
                if shared_budget.user == user
            ),
            None,
        )

        budget.can_edit = user_shared_budget.permission == BudgetPermission.EDIT
        budget.app_on = (
            user_shared_budget.notification_mode == NotificationMode.APP
            or user_shared_budget.notification_mode == NotificationMode.APP_EMAIL
        )
        budget.email_on = (
            user_shared_budget.notification_mode == NotificationMode.EMAIL
            or user_shared_budget.notification_mode == NotificationMode.APP_EMAIL
        )

    return budgets


@login_required(login_url="login")
def budgets_page(request):
    user_profile = UserProfile.objects.get(user=request.user)

    budgets = get_user_budgets_with_shared(request.user)

    categories = CategoryPreference.objects.filter(user=request.user)
    notifications, show_notifications_modal = parse_notifications(request)

    return render(
        request,
        "budgets.html",
        {
            "user_profile": user_profile,
            "budgets": budgets,
            "categories": categories,
            "notifications": notifications,
            "show_notifications_modal": show_notifications_modal,
        },
    )


@login_required(login_url="login")
def budget_view(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, sharedbudget__user=request.user)

    associated_users = SharedBudget.objects.filter(
        budget=budget, _role=BudgetRole.PARTICIPANT.value
    ).values_list("user", flat=True)

    transactions_for_budget = Transaction.objects.filter(
        user__in=associated_users, category__in=budget.categories.all()
    ).select_related("user")

    notifications, show_notifications_modal = parse_notifications(request)

    context = {
        "monthly_summaries": get_monthly_summaries(request, transactions_for_budget),
        "categories": CategoryPreference.objects.filter(user=request.user),
        "user_profile": UserProfile.objects.get(user=request.user),
        "budgets": Budget.objects.filter(sharedbudget__user=request.user),
        "notifications": notifications,
        "show_notifications_modal": show_notifications_modal,
    }

    return render(request, "main_page.html", context)


# Pred upravou pro nacitani vsech PARTICIPANTS z rozpoctu do budget summary:

# @login_required(login_url="login")
# def budget_view(request, budget_id):
#     budget = get_object_or_404(Budget, id=budget_id, owner=request.user)

#     transactions_for_budget = Transaction.objects.filter(
#         user=request.user, category__in=budget.categories.all()
#     )

#     notifications, show_notifications_modal = parse_notifications(
#         request, Budget.objects.filter(owner=request.user)
#     )

#     context = {
#         "monthly_summaries": get_monthly_summaries(request, transactions_for_budget),
#         "categories": CategoryPreference.objects.filter(user=request.user),
#         "user_profile": UserProfile.objects.get(user=request.user),
#         "budgets": Budget.objects.filter(owner=request.user),
#         "notifications": notifications,
#         "show_notifications_modal": show_notifications_modal,
#     }

#     return render(request, "main_page.html", context)


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


def get_budgets_from_json(request):
    try:
        return json.loads(request.POST.get("shared_budgets", "[]"))
    except json.JSONDecodeError:
        return None


def get_budget_from_query(shared_budget_id, shared_budgets_query):
    try:
        return shared_budgets_query.get(id=shared_budget_id)
    except SharedBudget.DoesNotExist:
        return None


def update_shared_budgets(request, is_owner, shared_budgets_query):
    shared_budgets = get_budgets_from_json(request)

    for shared_budget in shared_budgets:
        try:
            query_budget = get_budget_from_query(
                int(shared_budget.get("id")), shared_budgets_query
            )
            if query_budget is None:
                return False
            if is_owner:
                query_budget.permission = BudgetPermission(
                    shared_budget.get("permission")
                )
                query_budget.role = BudgetRole(shared_budget.get("role"))
            if request.user == query_budget.user:
                query_budget.role = BudgetRole(shared_budget.get("role"))
                query_budget.notification_mode = NotificationMode(
                    request.POST.get("notification_mode")
                )
            query_budget.save()
        except Exception:
            return False

    return True


@login_required(login_url="login")
def edit_budget(request, budget_id):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        budget = get_object_or_404(Budget, id=budget_id)
        shared_budgets_query = SharedBudget.objects.filter(budget=budget)
        user_shared_budget = next(
            (
                shared_budget
                for shared_budget in budget.shared_budgets
                if shared_budget.user == request.user
            ),
            None,
        )

        if user_shared_budget is None:
            return JsonResponse(
                {"success": False, "message": "Nemáte právo na úpravy."}, status=400
            )

        if (
            budget.owner == request.user
            or user_shared_budget.permission == BudgetPermission.EDIT
        ):
            form = BudgetForm(request.POST, user=request.user, instance=budget)
            if form.is_valid():
                if not update_shared_budgets(
                    request, budget.owner == request.user, shared_budgets_query
                ):
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Sdílené účty dodané ve špatném formátu.",
                        },
                        status=400,
                    )

                form.save()
                return JsonResponse(
                    {"success": True, "message": "Vaše změny byly uloženy."}
                )
            else:
                return JsonResponse(
                    {"success": False, "errors": form.errors}, status=400
                )

        if not update_shared_budgets(
            request, budget.owner == request.user, shared_budgets_query
        ):
            return JsonResponse(
                {
                    "success": False,
                    "message": "Sdílené účty dodané ve špatném formátu.",
                },
                status=400,
            )

        return JsonResponse(
            {"success": True, "message": "Vaše změny byly uloženy."}, status=200
        )

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


@login_required(login_url="login")
def create_shared_budget(request):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        budget = None
        try:
            budget_id = request.POST.get("budget_id")
            budget = get_object_or_404(Budget, id=int(budget_id), owner=request.user)
        except Exception:
            return JsonResponse(
                {"success": False, "message": "Daný rozpočet neexistuje."}, status=400
            )

        form = SharedBudgetForm(request.POST, budget=budget)
        if form.is_valid():
            form.save()
            return JsonResponse(
                {
                    "success": True,
                    "message": "Uživatel byl úspěšně přidán do sdíleného rozpočtu.",
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse(
        {"success": False, "message": "Nesprávný typ požadavku."}, status=400
    )


@login_required(login_url="login")
def delete_shared_budget(request, budget_id):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        shared_budget = get_object_or_404(SharedBudget, id=budget_id)

        if shared_budget.budget.owner != request.user:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Nemáte práva na odstranění uživatele z rozpočtu.",
                },
                status=400,
            )

        shared_budget.delete()

        return JsonResponse(
            {
                "success": True,
                "message": "Uživatel byl úspěšně odebrán ze sdíleného rozpočtu.",
            }
        )

    return JsonResponse(
        {"success": False, "message": "Nesprávný typ požadavku."}, status=400
    )
