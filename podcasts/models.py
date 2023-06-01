import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse


class Podcast(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    site_link = models.URLField(blank=True, null=True)
    feed_link = models.URLField(unique=True)
    image_link = models.URLField()
    pub_date = models.DateTimeField(blank=True, null=True)
    last_build_date = models.DateTimeField(blank=True, null=True)
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Subscription"
    )

    ttl = models.DurationField(blank=True, null=True)
    etag = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        ordering = ["title"]

    def get_absolute_url(self):
        return reverse("podcast-detail", kwargs={"pk": self.id})

    def __str__(self):
        return self.title


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    podcast = models.ForeignKey(
        Podcast,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["podcast__title"]
        unique_together = [["user", "podcast"]]

    def __str__(self):
        return self.podcast.title


class Episode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    site_link = models.URLField()
    media_link = models.URLField()
    pub_date = models.DateTimeField()
    guid = models.CharField(max_length=300)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.title


class EpisodeInteraction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    episode = models.ForeignKey(
        Episode,
        on_delete=models.CASCADE,
        related_name="interactions",
    )

    progress = models.IntegerField(blank=True, null=True)
    favourite = models.BooleanField(default=False)
    listened = models.BooleanField(default=False)

    class Meta:
        unique_together = [["user", "episode"]]

    def __str__(self):
        return self.episode.title
