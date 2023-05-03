import uuid

from django.db import models
from django.urls import reverse


class Podcast(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    description = models.TextField()
    site_link = models.URLField()
    feed_link = models.URLField(unique=True)
    image_link = models.URLField()
    pub_date = models.DateTimeField()
    last_build_date = models.DateTimeField()
    ttl = models.DurationField()

    def get_absolute_url(self):
        return reverse("podcast-detail", kwargs={"pk": self.id})

    def __str__(self):
        return self.title


class Episode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    description = models.TextField()
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    site_link = models.URLField()
    media_link = models.URLField()
    pub_date = models.DateTimeField()
    guid = models.CharField(max_length=300)

    def __str__(self):
        return self.title
