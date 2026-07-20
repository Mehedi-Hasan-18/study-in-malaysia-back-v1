from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scholarships", "0003_optional_date_description_level_choices"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    ALTER TABLE scholarship
                    ALTER COLUMN eligible_level TYPE jsonb
                    USING CASE
                        WHEN eligible_level IS NULL OR eligible_level = '' THEN '[]'::jsonb
                        ELSE jsonb_build_array(eligible_level)
                    END;
                    ALTER TABLE scholarship
                    ALTER COLUMN eligible_level SET DEFAULT '[]'::jsonb;
                    """,
                    reverse_sql="""
                    ALTER TABLE scholarship
                    ALTER COLUMN eligible_level DROP DEFAULT;
                    ALTER TABLE scholarship
                    ALTER COLUMN eligible_level TYPE varchar(20)
                    USING COALESCE(eligible_level->>0, '');
                    """,
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="scholarship",
                    name="eligible_level",
                    field=models.JSONField(blank=True, default=list),
                ),
            ],
        ),
    ]
