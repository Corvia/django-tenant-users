from django.db import migrations, models
from django_tenants.postgresql_backend.base import (  # noqa: WPS433, WPS450
    _check_schema_name as check_schema_name,
)


class Migration(migrations.Migration):
    """Initial migration for test_django_tenants.companies app."""

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
                (
                    'schema_name',
                    models.CharField(
                        db_index=True,
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
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Domain',
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
                (
                    'domain',
                    models.CharField(
                        db_index=True,
                        max_length=253,
                        unique=True,
                    ),
                ),
                (
                    'is_primary',
                    models.BooleanField(
                        db_index=True,
                        default=True,
                    ),
                ),
                (
                    'tenant',
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name='domains',
                        to='companies.company',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
