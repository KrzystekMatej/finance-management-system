# Generated by Django 4.2.16 on 2024-10-20 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("finance_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationModel",
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
                        to="finance_app.userprofilemodel",
                    ),
                ),
            ],
        ),
    ]
