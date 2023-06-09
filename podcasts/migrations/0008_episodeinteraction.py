# Generated by Django 4.2.1 on 2023-05-19 16:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("podcasts", "0007_alter_subscription_unique_together"),
    ]

    operations = [
        migrations.CreateModel(
            name="EpisodeInteraction",
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
                ("progress", models.IntegerField(blank=True, null=True)),
                ("favourite", models.BooleanField(default=False)),
                ("listened", models.BooleanField(default=False)),
                (
                    "episode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="podcasts.episode",
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
            options={
                "unique_together": {("user", "episode")},
            },
        ),
    ]
