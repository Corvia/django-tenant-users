# Generated by Django 3.2.21 on 2023-09-11 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_alter_company_created_alter_company_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='type',
            field=models.CharField(default='type1', max_length=100),
        ),
    ]
