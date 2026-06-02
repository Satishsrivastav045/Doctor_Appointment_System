from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("doctors", "0004_doctor_photo_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="doctor",
            name="consultation_fee",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="doctor",
            name="rating",
            field=models.DecimalField(decimal_places=1, default=4.5, max_digits=3),
        ),
        migrations.AddField(
            model_name="doctor",
            name="review_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="doctor",
            name="whatsapp_number",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
