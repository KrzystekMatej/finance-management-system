from django.contrib import admin
from finance_app.models import (
    UserProfile,
    Category,
    CategoryPreference,
    Transaction,
    Budget,
    SharedBudget,
    RecurringTransaction,
    Notification,
)

admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(CategoryPreference)
admin.site.register(Transaction)
admin.site.register(RecurringTransaction)
admin.site.register(Budget)
admin.site.register(SharedBudget)
admin.site.register(Notification)
