# Generated by Django 4.2 on 2023-05-01 16:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("podcasts", "0003_podcast_image_link"),
    ]

    operations = [
        migrations.RenameField(
            model_name="episode",
            old_name="link",
            new_name="site_link",
        ),
        migrations.AddField(
            model_name="episode",
            name="media_link",
            field=models.URLField(default="test"),
            preserve_default=False,
        ),
    ]