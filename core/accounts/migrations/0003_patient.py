from django.db import migrations, models
import django.db.models.deletion


def create_patient_profiles(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Patient = apps.get_model("accounts", "Patient")

    for user in User.objects.select_related("role").all():
        role_name = (user.role.role_name or "").lower() if user.role_id else ""
        if role_name == "patient":
            Patient.objects.get_or_create(
                user_id=user.id,
                defaults={
                    "patient_name": user.first_name or user.username,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_alter_user_role"),
    ]

    operations = [
        migrations.CreateModel(
            name="Patient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("patient_name", models.CharField(max_length=150)),
                ("dob", models.DateField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="patient_profile",
                        to="accounts.user",
                    ),
                ),
            ],
        ),
        migrations.RunPython(create_patient_profiles, migrations.RunPython.noop),
    ]
