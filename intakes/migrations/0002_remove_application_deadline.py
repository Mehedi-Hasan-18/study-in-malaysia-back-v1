from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("intakes", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="intake",
            name="application_deadline",
        ),
    ]
