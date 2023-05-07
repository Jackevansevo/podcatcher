import urllib3
from django.contrib import admin

from .models import Episode, Podcast
from .parser import ingest_podcast, parse_podcast


class EpisodeInline(admin.TabularInline):
    model = Episode


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    pass


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    inlines = [
        EpisodeInline,
    ]
    fields = ["feed_link"]

    def save_model(self, request, obj, form, change):
        resp = urllib3.request("GET", obj.feed_link)
        ingest_podcast(resp.data)
