# Generated by Django 4.2 on 2023-05-05 18:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("podcasts", "0004_rename_link_episode_site_link_episode_media_link"),
    ]

    operations = [
        migrations.AlterField(
            model_name="podcast",
            name="last_build_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="podcast",
            name="pub_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="podcast",
            name="ttl",
            field=models.DurationField(blank=True, null=True),
        ),
    ]
