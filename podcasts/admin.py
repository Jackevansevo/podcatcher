import urllib3
from django.contrib import admin

from .models import Episode, Podcast
from .parser import parse_podcast


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
        parsed_podcast, parsed_episodes = parse_podcast(resp.data)
        podcast = Podcast(**parsed_podcast)
        podcast.save()
        for parsed_episode in parsed_episodes:
            episode = Episode(**parsed_episode, podcast=podcast)
            episode.save()
