# Generated by Django 4.2.1 on 2023-05-25 18:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("podcasts", "0008_episodeinteraction"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="podcast",
            options={"ordering": ["title"]},
        ),
        migrations.AlterModelOptions(
            name="subscription",
            options={"ordering": ["podcast__title"]},
        ),
        migrations.AddField(
            model_name="podcast",
            name="etag",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name="episodeinteraction",
            name="episode",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="interactions",
                to="podcasts.episode",
            ),
        ),
    ]
