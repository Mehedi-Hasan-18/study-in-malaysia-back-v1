from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scholarships", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scholarship",
            name="coverage_percentage",
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]
