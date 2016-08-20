# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tenant_users.permissions.models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TenantUser',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(blank=True, verbose_name='last login', null=True)),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='Email Address', db_index=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(blank=True, verbose_name='Name', max_length=100)),
                ('companies', models.ManyToManyField(blank=True, related_name='user_set', to='customers.Client', verbose_name='companies', help_text='The companies this user belongs to.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, tenant_users.permissions.models.PermissionsMixinFacade),
        ),
    ]
