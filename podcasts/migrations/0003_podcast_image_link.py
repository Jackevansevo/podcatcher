# Generated by Django 4.2 on 2023-05-01 15:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("podcasts", "0002_alter_podcast_feed_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="podcast",
            name="image_link",
            field=models.URLField(default=""),
            preserve_default=False,
        ),
    ]