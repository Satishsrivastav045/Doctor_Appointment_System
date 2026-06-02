from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("doctors", "0002_doctor_flow_updates"),
    ]

    operations = [
        migrations.AlterField(
            model_name="doctor",
            name="phone_no",
            field=models.CharField(blank=True, max_length=15),
        ),
    ]
