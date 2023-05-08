import hashlib
import json
import os
import time
from datetime import date
from http import HTTPStatus
from urllib.parse import urlparse

import urllib3
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Episode, Podcast, Subscription
from .parser import ingest_podcast, parse_podcast


@require_GET
def import_feed(request):
    url = request.GET.get("url")
    if url:
        resp = urllib3.request("GET", url)
        with transaction.atomic():
            podcast = ingest_podcast(resp.data)
            Subscription.objects.create(podcast=podcast, user=request.user)
            return redirect(podcast)


@require_GET
def search(request):
    search_term = request.GET["search"]
    if search_term:
        try:
            podcast = Podcast.objects.get(feed_link=search_term)
        except Podcast.DoesNotExist:
            pass
        else:
            return redirect(podcast)

    # results = Podcast.objects.filter(title__contains=search_term)

    url = "https://api.podcastindex.org/api/1.0/search/byterm?q=" + search_term

    # we'll need the unix time
    epoch_time = int(time.time())

    api_key = os.environ.get("PODCAST_INDEX_API_KEY")
    api_secret = os.environ.get("PODCAST_INDEX_API_SECRET")

    # our hash here is the api key + secret + time
    data_to_hash = api_key + api_secret + str(epoch_time)
    # which is then sha-1'd
    sha_1 = hashlib.sha1(data_to_hash.encode()).hexdigest()

    # now we build our request headers
    headers = {
        "X-Auth-Date": str(epoch_time),
        "X-Auth-Key": api_key,
        "Authorization": sha_1,
        "User-Agent": "postcasting-index-python-cli",
    }

    try:
        resp = urllib3.request("POST", url, headers=headers)
    except urllib3.exceptions.MaxRetryError:
        return render(request, "podcasts/search.html", {"results": {}})

    if resp.status == HTTPStatus.OK:
        results = resp.json()
        return render(request, "podcasts/search.html", {"results": results})
    else:
        return render(request, "podcasts/search.html", {"results": {}})


class SubscriptionListView(ListView, LoginRequiredMixin):
    model = Subscription

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class PodcastDetailView(DetailView):
    model = Podcast
