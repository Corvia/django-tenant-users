from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("permissions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="usertenantpermissions",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                help_text="The date and time when the user was added to this tenant.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="usertenantpermissions",
            name="modified_at",
            field=models.DateTimeField(
                auto_now=True,
                help_text="The date and time when the user's permissions were last modified.",
                null=True,
            ),
        ),
    ]
