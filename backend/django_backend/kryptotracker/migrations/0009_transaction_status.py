# Generated by Django 4.2.8 on 2024-01-29 15:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kryptotracker", "0008_alter_assetinfo_image_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="status",
            field=models.BooleanField(default=False),
        ),
    ]
