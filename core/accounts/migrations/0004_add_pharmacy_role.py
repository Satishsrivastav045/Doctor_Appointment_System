from django.db import migrations


def add_pharmacy_role(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    Role.objects.get_or_create(role_name="pharmacy")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_patient"),
    ]

    operations = [
        migrations.RunPython(add_pharmacy_role, migrations.RunPython.noop),
    ]
