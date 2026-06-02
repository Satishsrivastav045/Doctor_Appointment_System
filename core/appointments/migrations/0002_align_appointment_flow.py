import django.db.models.deletion
from django.db import migrations, models


def migrate_appointments_to_patients(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Patient = apps.get_model("accounts", "Patient")
    Appointment = apps.get_model("appointments", "Appointment")

    for user in User.objects.select_related("role").all():
        role_name = (user.role.role_name or "").lower() if user.role_id else ""
        if role_name == "patient":
            Patient.objects.get_or_create(
                user_id=user.id,
                defaults={"patient_name": user.first_name or user.username},
            )

    for appointment in Appointment.objects.select_related("user", "availability").all():
        patient, _ = Patient.objects.get_or_create(
            user_id=appointment.user_id,
            defaults={"patient_name": appointment.user.first_name or appointment.user.username},
        )
        appointment.patient_id = patient.id
        appointment.appointment_date = appointment.availability.available_date
        appointment.save(update_fields=["patient", "appointment_date"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_patient"),
        ("doctors", "0002_doctor_flow_updates"),
        ("appointments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="appointment",
            name="appointment_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="appointment",
            name="patient",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="appointments",
                to="accounts.patient",
            ),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.RunPython(migrate_appointments_to_patients, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="appointment",
            name="appointment_date",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="patient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="appointments",
                to="accounts.patient",
            ),
        ),
        migrations.RemoveField(
            model_name="appointment",
            name="user",
        ),
    ]
