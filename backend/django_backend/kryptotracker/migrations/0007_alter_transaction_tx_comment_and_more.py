# Generated by Django 4.2.8 on 2024-01-17 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "kryptotracker",
            "0006_alter_assetinfo_acronym_alter_assetinfo_api_id_name_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="tx_comment",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="kryptotracker.comment",
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="tx_fee",
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]
