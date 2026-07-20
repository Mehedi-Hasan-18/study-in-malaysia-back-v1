from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programs", "0003_decimal_duration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="programrequirement",
            name="description",
            field=models.TextField(blank=True),
        ),
    ]
