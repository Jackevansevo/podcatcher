# Generated by Django 4.2.1 on 2023-06-01 20:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("podcasts", "0009_alter_podcast_options_alter_subscription_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="podcast",
            name="site_link",
            field=models.URLField(blank=True, null=True),
        ),
    ]