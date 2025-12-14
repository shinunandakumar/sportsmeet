from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Meet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[("DRAFT", "Draft"), ("ACTIVE", "Active"), ("COMPLETED", "Completed")],
                        default="DRAFT",
                        max_length=16,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                (
                    "meet",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="categories", to="meet.meet"),
                ),
            ],
            options={"unique_together": {("name", "meet")}},
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                (
                    "event_type",
                    models.CharField(
                        choices=[("TRACK", "Track"), ("FIELD", "Field"), ("OTHER", "Other")],
                        default="OTHER",
                        max_length=16,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("ACTIVE", "Active"), ("INACTIVE", "Inactive")],
                        default="ACTIVE",
                        max_length=16,
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="meet.category"),
                ),
            ],
            options={"unique_together": {("name", "category")}},
        ),
    ]
