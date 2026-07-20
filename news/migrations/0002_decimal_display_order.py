from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="faq",
            name="display_order",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
