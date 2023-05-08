# Generated by Django 4.2 on 2023-05-08 13:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        (
            "podcasts",
            "0005_alter_podcast_last_build_date_alter_podcast_pub_date_and_more",
        ),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="episode",
            options={"ordering": ["-pub_date"]},
        ),
        migrations.CreateModel(
            name="Subscription",
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
                (
                    "podcast",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="podcasts.podcast",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="podcast",
            name="subscribers",
            field=models.ManyToManyField(
                through="podcasts.Subscription", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
