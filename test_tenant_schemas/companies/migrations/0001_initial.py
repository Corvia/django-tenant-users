from django.db import migrations, models
from tenant_schemas.postgresql_backend.base import (  # noqa: WPS433, WPS450
    _check_schema_name as check_schema_name,
)


class Migration(migrations.Migration):
    """Initial migration for test_tenant_schemas.companies app."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('domain_url', models.CharField(max_length=128, unique=True)),
                (
                    'schema_name',
                    models.CharField(
                        max_length=63,
                        unique=True,
                        validators=[check_schema_name],
                    ),
                ),
                (
                    'slug',
                    models.SlugField(
                        blank=True,
                        verbose_name='Tenant URL Name',
                    ),
                ),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField(blank=True)),
                ('name', models.CharField(blank=True, max_length=64)),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
