# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tenant_schemas.postgresql_backend.base


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('domain_url', models.CharField(max_length=128, unique=True)),
                ('schema_name', models.CharField(max_length=63, validators=[tenant_schemas.postgresql_backend.base._check_schema_name], unique=True)),
                ('slug', models.SlugField(blank=True, verbose_name='Company URL Name')),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField(blank=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
