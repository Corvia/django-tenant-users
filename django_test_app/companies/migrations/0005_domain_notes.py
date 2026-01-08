from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("companies", "0004_company_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="domain",
            name="notes",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
