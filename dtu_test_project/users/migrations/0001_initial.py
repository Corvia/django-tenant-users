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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('email', models.EmailField(verbose_name='Email Address', max_length=254, db_index=True, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(verbose_name='Name', blank=True, max_length=100)),
                ('tenants', models.ManyToManyField(verbose_name='tenants', blank=True, help_text='The tenants this user belongs to.', to='customers.Client', related_name='user_set')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, tenant_users.permissions.models.PermissionsMixinFacade),
        ),
    ]
