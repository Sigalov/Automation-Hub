# Generated by Django 4.2.5 on 2023-10-10 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector", "0002_serviceblock"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ServiceBlock",
        ),
        migrations.AddField(
            model_name="block",
            name="console_output",
            field=models.TextField(blank=True, default=""),
        ),
    ]