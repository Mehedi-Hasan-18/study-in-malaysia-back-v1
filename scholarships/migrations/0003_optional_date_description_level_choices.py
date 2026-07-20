from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scholarships", "0002_decimal_coverage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scholarship",
            name="application_deadline",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="scholarship",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="scholarship",
            name="eligible_level",
            field=models.CharField(
                choices=[
                    ("foundation", "Foundation"),
                    ("diploma", "Diploma"),
                    ("bachelor", "Bachelor"),
                    ("masters", "Masters"),
                ],
                max_length=20,
            ),
        ),
    ]
