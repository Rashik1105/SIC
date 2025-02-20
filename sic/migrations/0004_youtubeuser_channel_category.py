# Generated by Django 5.1.5 on 2025-02-11 10:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sic", "0003_category_youtubeuser_keywords_alter_youtubeuser_user_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="youtubeuser",
            name="channel_category",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="sic.category",
            ),
            preserve_default=False,
        ),
    ]
