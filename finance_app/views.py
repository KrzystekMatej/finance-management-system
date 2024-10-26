from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm


# DEBUG: Comment if you don't want to bother with logging in
@login_required(login_url="login")
def main_page(request):

    # TODO: Implement actual logic for fetching real data
    monthly_summaries = [
        {
            "year": 2024,
            "month": "Leden",  # January
            "positive_income": 45000,
            "negative_income": 25000,
            "transactions": [
                {
                    "date": "10/01/2024",
                    "source": "Freelance",
                    "amount": 15352,
                    "title": "Job 13555",
                },
                {
                    "date": "05/01/2024",
                    "source": "Rent",
                    "amount": -12000,
                    "title": "Poruba, Ostrava",
                },
                {
                    "date": "01/01/2024",
                    "source": "Salary",
                    "amount": 45000,
                    "title": "MyCompany s.r.o.",
                },
            ],
        },
        {
            "year": 2024,
            "month": "Únor",  # February
            "positive_income": 48000,
            "negative_income": 27000,
            "transactions": [
                {
                    "date": "07/02/2024",
                    "source": "Groceries",
                    "amount": -3000,
                    "title": "spaceholder",
                },
                {
                    "date": "10/02/2024",
                    "source": "Freelance",
                    "amount": 16000,
                    "title": "",
                },
                {
                    "date": "08/02/2024",
                    "source": "Groceries",
                    "amount": -3500,
                    "title": "spaceholder",
                },
                {
                    "date": "05/02/2024",
                    "source": "Rent",
                    "amount": -12000,
                    "title": "spaceholder",
                },
                {
                    "date": "02/02/2024",
                    "source": "Salary",
                    "amount": 48000,
                    "title": "",
                },
                {
                    "date": "15/02/2024",
                    "source": "Utilities",
                    "amount": -3000,
                    "title": "spaceholder",
                },
            ],
        },
        {
            "year": 2024,
            "month": "Březen",  # March
            "positive_income": 50000,
            "negative_income": 20000,
            "transactions": [
                {
                    "date": "10/03/2024",
                    "source": "Freelance",
                    "amount": 17000,
                    "title": "spaceholder",
                },
                {
                    "date": "07/03/2024",
                    "source": "Groceries",
                    "amount": -4000,
                    "title": "spaceholder",
                },
                {
                    "date": "05/03/2024",
                    "source": "Rent",
                    "amount": -12000,
                    "title": "spaceholder",
                },
                {
                    "date": "01/03/2024",
                    "source": "Salary",
                    "amount": 50000,
                    "title": "spaceholder",
                },
                {
                    "date": "20/03/2024",
                    "source": "Investment",
                    "amount": 5000,
                    "title": "spaceholder",
                },
                {
                    "date": "25/03/2024",
                    "source": "Freelance",
                    "amount": 8000,
                    "title": "spaceholder",
                },
                {
                    "date": "28/03/2024",
                    "source": "Car Maintenance",
                    "amount": -2500,
                    "title": "spaceholder",
                },
            ],
        },
        {
            "year": 2024,
            "month": "Duben",  # April
            "positive_income": 55000,
            "negative_income": 30000,
            "transactions": [
                {
                    "date": "10/04/2024",
                    "source": "Freelance",
                    "amount": 18000,
                    "title": "spaceholder",
                },
                {
                    "date": "07/04/2024",
                    "source": "Groceries",
                    "amount": -5000,
                    "title": "spaceholder",
                },
                {
                    "date": "05/04/2024",
                    "source": "Rent",
                    "amount": -12000,
                    "title": "spaceholder",
                },
                {
                    "date": "01/04/2024",
                    "source": "Salary",
                    "amount": 55000,
                    "title": "spaceholder",
                },
            ],
        },
        {
            "year": 2024,
            "month": "Květen",  # May
            "positive_income": 60000,
            "negative_income": 25000,
            "transactions": [
                {
                    "date": "10/05/2024",
                    "source": "Freelance",
                    "amount": 19000,
                    "title": "spaceholder",
                },
                {
                    "date": "07/05/2024",
                    "source": "Groceries",
                    "amount": -4000,
                    "title": "spaceholder",
                },
                {
                    "date": "05/05/2024",
                    "source": "Rent",
                    "amount": -12000,
                    "title": "spaceholder",
                },
                {
                    "date": "01/05/2024",
                    "source": "Salary",
                    "amount": 60000,
                    "title": "spaceholder",
                },
                {
                    "date": "15/05/2024",
                    "source": "Investment",
                    "amount": 7000,
                    "title": "spaceholder",
                },
                {
                    "date": "18/05/2024",
                    "source": "Car Insurance",
                    "amount": -1500,
                    "title": "spaceholder",
                },
            ],
        },
        {
            "year": 2024,
            "month": "Červen",  # June
            "positive_income": 65000,
            "negative_income": 26000,
            "transactions": [
                {
                    "date": "10/06/2024",
                    "source": "Freelance",
                    "amount": 20000,
                    "title": "spaceholder",
                },
                {
                    "date": "07/06/2024",
                    "source": "Groceries",
                    "amount": -3000,
                    "title": "spaceholder",
                },
                {
                    "date": "05/06/2024",
                    "source": "Rent",
                    "amount": -12000,
                    "title": "spaceholder",
                },
                {
                    "date": "01/06/2024",
                    "source": "Salary",
                    "amount": 65000,
                    "title": "spaceholder",
                },
                {
                    "date": "22/06/2024",
                    "source": "Dining Out",
                    "amount": -4000,
                    "title": "spaceholder",
                },
                {
                    "date": "29/06/2024",
                    "source": "Gift",
                    "amount": -2500,
                    "title": "spaceholder",
                },
            ],
        },
        {
            "year": 2024,
            "month": "Červenec",  # July
            "positive_income": 70000,
            "negative_income": 28000,
            "transactions": [
                {
                    "date": "10/07/2024",
                    "source": "Freelance",
                    "amount": 21000,
                    "title": "spaceholder",
                },
                {
                    "date": "07/07/2024",
                    "source": "Groceries",
                    "amount": -4500,
                    "title": "spaceholder",
                },
                {
                    "date": "05/07/2024",
                    "source": "Rent",
                    "amount": -12000,
                    "title": "spaceholder",
                },
                {
                    "date": "01/07/2024",
                    "source": "Salary",
                    "amount": 70000,
                    "title": "spaceholder",
                },
                {
                    "date": "15/07/2024",
                    "source": "Utilities",
                    "amount": -2000,
                    "title": "spaceholder",
                },
            ],
        },
        {
            "year": 2024,
            "month": "Srpen",  # August
            "positive_income": 72000,
            "negative_income": 29000,
            "transactions": [
                {
                    "date": "10/08/2024",
                    "source": "Freelance",
                    "amount": 22000,
                    "title": "spaceholder",
                },
                {
                    "date": "07/08/2024",
                    "source": "Groceries",
                    "amount": -5000,
                    "title": "spaceholder",
                },
                {
                    "date": "05/08/2024",
                    "source": "Rent",
                    "amount": -12000,
                    "title": "spaceholder",
                },
                {
                    "date": "01/08/2024",
                    "source": "Salary",
                    "amount": 72000,
                    "title": "spaceholder",
                },
                {
                    "date": "20/08/2024",
                    "source": "Vacation",
                    "amount": -15000,
                    "title": "spaceholder",
                },
            ],
        },
        {
            "year": 2024,
            "month": "Září",  # September
            "positive_income": 40000,
            "negative_income": 20000,
            "transactions": [
                {
                    "date": "11/09/2024",
                    "source": "Car Repair",
                    "amount": -8000,
                    "title": "spaceholder",
                },
                {
                    "date": "08/09/2024",
                    "source": "Rent",
                    "amount": -12000,
                    "title": "spaceholder",
                },
                {
                    "date": "02/09/2024",
                    "source": "Salary",
                    "amount": 40000,
                    "title": "spaceholder",
                },
            ],
        },
        {
            "year": 2024,
            "month": "Říjen",  # October
            "positive_income": 50000,
            "negative_income": 30000,
            "transactions": [
                {
                    "date": "10/10/2024",
                    "source": "Freelance",
                    "amount": 20000,
                    "title": "spaceholder",
                },
                {
                    "date": "07/10/2024",
                    "source": "Groceries",
                    "amount": -2000,
                    "title": "spaceholder",
                },
                {
                    "date": "05/10/2024",
                    "source": "Rent",
                    "amount": -15000,
                    "title": "spaceholder",
                },
                {
                    "date": "01/10/2024",
                    "source": "Salary",
                    "amount": 50000,
                    "title": "spaceholder",
                },
                {
                    "date": "15/10/2024",
                    "source": "Miscellaneous",
                    "amount": -1000,
                    "title": "spaceholder",
                },
                {
                    "date": "20/10/2024",
                    "source": "Side Job",
                    "amount": 3000,
                    "title": "spaceholder",
                },
            ],
        },
    ]

    context = {"monthly_summaries": monthly_summaries}

    return render(request, "main_page.html", context)


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
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect("main_page")
            else:
                form.add_error(None, "Nesprávný email nebo heslo.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


@login_required(login_url="login")
def logout_page(request):
    logout(request)
    return render(request, "logout.html")
