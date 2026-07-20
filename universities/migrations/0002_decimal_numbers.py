from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("universities", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gallery",
            name="display_order",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name="university",
            name="established_year",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name="university",
            name="total_students",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
