# Generated by Django 4.2.16 on 2024-10-26 11:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Budget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("exceeded_at", models.DateTimeField(blank=True, null=True)),
                ("limit", models.DecimalField(decimal_places=2, max_digits=10)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("description", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("performed_at", models.DateTimeField()),
                ("description", models.TextField(blank=True)),
                (
                    "category",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="finance_app.category",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RecurringTransaction",
            fields=[
                (
                    "transaction_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="finance_app.transaction",
                    ),
                ),
                (
                    "_interval",
                    models.CharField(
                        choices=[
                            ("DAY", "Day"),
                            ("WEEK", "Week"),
                            ("MONTH", "Month"),
                            ("YEAR", "Year"),
                        ],
                        default="MONTH",
                        max_length=10,
                    ),
                ),
            ],
            bases=("finance_app.transaction",),
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "balance",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "_global_notification_mode",
                    models.CharField(
                        choices=[
                            ("NONE", "None"),
                            ("APP", "App"),
                            ("EMAIL", "Email"),
                            ("APP_EMAIL", "App_email"),
                        ],
                        default="APP",
                        max_length=10,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="transaction",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="finance_app.userprofile",
            ),
        ),
        migrations.CreateModel(
            name="SharedBudget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "_permission",
                    models.CharField(
                        choices=[("VIEW", "View"), ("EDIT", "Edit")],
                        default="VIEW",
                        max_length=10,
                    ),
                ),
                (
                    "_role",
                    models.CharField(
                        choices=[
                            ("PARTICIPANT", "Participant"),
                            ("OBSERVER", "Observer"),
                        ],
                        default="PARTICIPANT",
                        max_length=20,
                    ),
                ),
                ("on_exceeded", models.BooleanField(default=True)),
                ("on_limit_change", models.BooleanField(default=True)),
                ("on_transaction", models.BooleanField(default=True)),
                (
                    "_notification_mode",
                    models.CharField(
                        choices=[
                            ("NONE", "None"),
                            ("APP", "App"),
                            ("EMAIL", "Email"),
                            ("APP_EMAIL", "App_email"),
                        ],
                        default="APP",
                        max_length=10,
                    ),
                ),
                (
                    "budget",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="finance_app.budget",
                    ),
                ),
                (
                    "shared_with",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="finance_app.userprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subject", models.CharField(max_length=100)),
                ("message", models.CharField(max_length=255)),
                ("sent_at", models.DateTimeField(auto_now_add=True)),
                ("is_read", models.BooleanField(default=False)),
                (
                    "receiver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="finance_app.userprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CategoryPreference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("color", models.CharField(max_length=7)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="finance_app.category",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="finance_app.userprofile",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="budget",
            name="categories",
            field=models.ManyToManyField(blank=True, to="finance_app.category"),
        ),
        migrations.AddField(
            model_name="budget",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="finance_app.userprofile",
            ),
        ),
    ]
