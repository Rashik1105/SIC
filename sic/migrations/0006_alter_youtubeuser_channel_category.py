# Generated by Django 5.1.5 on 2025-02-12 14:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sic", "0005_alter_youtubeuser_channel_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="youtubeuser",
            name="channel_category",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="sic.category",
            ),
        ),
    ]
