from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("intakes", "0002_remove_application_deadline"),
    ]

    operations = [
        migrations.AlterField(
            model_name="intake",
            name="start_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
