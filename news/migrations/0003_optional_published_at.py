from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0002_decimal_display_order"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blog",
            name="published_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="news",
            name="published_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
