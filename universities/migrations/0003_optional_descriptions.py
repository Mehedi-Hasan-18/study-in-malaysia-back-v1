from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("universities", "0002_decimal_numbers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="university",
            name="full_description",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="university",
            name="short_description",
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
