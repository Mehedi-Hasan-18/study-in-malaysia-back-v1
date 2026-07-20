from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programs", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="program",
            name="duration_months",
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]
