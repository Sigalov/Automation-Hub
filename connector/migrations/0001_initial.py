# Generated by Django 4.2.5 on 2023-09-19 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Block",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("block_id", models.CharField(max_length=255, unique=True)),
                ("status", models.CharField(default="STOPPED", max_length=255)),
                ("running", models.BooleanField(default=False)),
                ("output_data", models.TextField(default="")),
                ("app_name", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "pt_username",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("pt_token", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "aws_access_key",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "aws_secret_key",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("filter_id_list", models.TextField(blank=True, null=True)),
            ],
        ),
    ]
