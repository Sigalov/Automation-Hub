# Generated by Django 4.2.5 on 2023-10-25 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("connector", "0006_alter_block_status"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="block",
            name="block_id",
        ),
    ]