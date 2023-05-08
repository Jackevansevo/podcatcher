import urllib3
from django.contrib import admin

from .models import Episode, Podcast, Subscription
from .parser import ingest_podcast, parse_podcast


class EpisodeInline(admin.TabularInline):
    model = Episode
    fields = ["title", "site_link", "media_link", "pub_date", "guid"]
    readonly_fields = fields


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "podcast"]


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    inlines = [
        EpisodeInline,
    ]
    fields = ["title", "description", "feed_link", "pub_date", "last_build_date"]
    readonly_fields = fields

    def save_model(self, request, obj, form, change):
        resp = urllib3.request("GET", obj.feed_link)
        ingest_podcast(resp.data)
