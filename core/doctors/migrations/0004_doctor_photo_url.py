from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("doctors", "0003_alter_doctor_phone_no"),
    ]

    operations = [
        migrations.AddField(
            model_name="doctor",
            name="photo_url",
            field=models.URLField(blank=True),
        ),
    ]
