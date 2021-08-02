from django.db import migrations, models

from tenant_users.permissions.models import PermissionsMixinFacade


class Migration(migrations.Migration):
    """Initial migration for test_django_tenants.users app."""

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TenantUser',
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
                    'password',
                    models.CharField(
                        max_length=128,
                        verbose_name='password',
                    ),
                ),
                (
                    'last_login',
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name='last login',
                    ),
                ),
                (
                    'email',
                    models.EmailField(
                        db_index=True,
                        max_length=254,
                        unique=True,
                        verbose_name='Email Address',
                    ),
                ),
                (
                    'is_active',
                    models.BooleanField(
                        default=True,
                        verbose_name='active',
                    ),
                ),
                (
                    'is_verified',
                    models.BooleanField(default=False, verbose_name='verified'),
                ),
                ('name', models.CharField(blank=True, max_length=64)),
                (
                    'tenants',
                    models.ManyToManyField(
                        blank=True,
                        help_text='The tenants this user belongs to.',
                        related_name='user_set',
                        to='companies.Company',
                        verbose_name='tenants',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
            bases=(
                models.Model,
                PermissionsMixinFacade,
            ),
        ),
    ]
