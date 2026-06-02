from django.db import migrations, models


def populate_doctor_fields(apps, schema_editor):
    Doctor = apps.get_model("doctors", "Doctor")
    Availability = apps.get_model("doctors", "Availability")

    for doctor in Doctor.objects.select_related("user").all():
        doctor.name = doctor.name or doctor.user.first_name or doctor.user.username
        doctor.email_id = doctor.email_id or doctor.user.email or ""
        doctor.save(update_fields=["name", "email_id"])

    for availability in Availability.objects.all():
        if availability.end_time is None:
            availability.end_time = availability.start_time
            availability.save(update_fields=["end_time"])


class Migration(migrations.Migration):

    dependencies = [
        ("doctors", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="doctor",
            old_name="phone",
            new_name="phone_no",
        ),
        migrations.AddField(
            model_name="doctor",
            name="email_id",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="doctor",
            name="name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name="doctor",
            name="specialization",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.RenameField(
            model_name="availability",
            old_name="date",
            new_name="available_date",
        ),
        migrations.RenameField(
            model_name="availability",
            old_name="time_slot",
            new_name="start_time",
        ),
        migrations.AddField(
            model_name="availability",
            name="end_time",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.RunPython(populate_doctor_fields, migrations.RunPython.noop),
    ]
