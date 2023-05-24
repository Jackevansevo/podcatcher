import hashlib
import os
import time
from http import HTTPStatus
from urllib.parse import urlparse

import urllib3
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Exists, OuterRef, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Episode, EpisodeInteraction, Podcast, Subscription
from .parser import ingest_podcast


@require_POST
def update_episode(request, pk, defaults):
    interaction, _ = EpisodeInteraction.objects.update_or_create(
        episode_id=pk, user=request.user, defaults=defaults
    )
    if request.htmx:
        return render(
            request,
            "podcasts/episode_list_item_partial.html",
            {"interaction": interaction, "episode": interaction.episode},
        )
    else:
        return redirect(interaction.episode.podcast)


def favourite(request, pk):
    return update_episode(request, pk, {"favourite": True})


@require_POST
def unfavourite(request, pk):
    return update_episode(request, pk, {"favourite": False})


@require_GET
def unsubscribe(request):
    url = request.GET.get("url")
    if url:
        try:
            subscription = Subscription.objects.get(
                podcast__feed_link=url, user=request.user
            )
        except Subscription.DoesNotExist:
            pass
        else:
            subscription.delete()
    return redirect("subscription-list")


@require_GET
def subscribe(request):
    url = request.GET.get("url")
    if url:
        with transaction.atomic():
            try:
                subscription = Subscription.objects.get(
                    podcast__feed_link=url, user=request.user
                )
            except Subscription.DoesNotExist:
                pass
            else:
                return redirect(subscription.podcast)
            try:
                podcast = Podcast.objects.get(feed_link=url)
            except Podcast.DoesNotExist:
                resp = urllib3.request("GET", url)
                podcast = ingest_podcast(resp.data)
            finally:
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

    results = {}
    if resp.status == HTTPStatus.OK:
        results = resp.json()

    if results.get("feeds"):
        subscriptions = set(
            Subscription.objects.filter(user=request.user).values_list(
                "podcast__feed_link", flat=True
            )
        )
        for index, result in enumerate(results["feeds"]):
            results["feeds"][index]["subscribed"] = (
                result["originalUrl"] in subscriptions
            )

    if request.htmx:
        return render(request, "podcasts/search_partial.html", {"results": results})
    else:
        return render(request, "podcasts/search.html", {"results": results})


class SubscriptionListView(LoginRequiredMixin, ListView):
    model = Subscription

    def get_template_names(self):
        if self.request.htmx:
            return ["podcasts/subscription_list_partial.html"]
        else:
            return ["podcasts/subscription_list.html"]

    def get_queryset(self):
        return (
            Subscription.objects.select_related("podcast")
            .filter(user=self.request.user)
            .all()
        )


class EpisodeListView(LoginRequiredMixin, ListView):
    model = Episode

    def get_template_names(self):
        if self.request.htmx:
            return ["podcasts/episode_list_partial.html"]
        else:
            return ["podcasts/episode_list.html"]

    def get_queryset(self):
        return Episode.objects.prefetch_related("podcast").filter(
            podcast__subscription__user=self.request.user
        )


class EpisodeFavouriteView(EpisodeListView):
    def get_queryset(self):
        return Episode.objects.prefetch_related("podcast").filter(
            podcast__subscription__user=self.request.user,
            interactions__favourite=True,
        )


class EpisodeListeningView(EpisodeListView):
    def get_queryset(self):
        return Episode.objects.prefetch_related("podcast").filter(
            podcast__subscription__user=self.request.user,
            interactions__progress__isnull=False,
        )


def podcast_detail_view(request, pk):
    queryset = Podcast.objects.prefetch_related(
        Prefetch(
            "episode_set",
            queryset=Episode.objects.prefetch_related(
                Prefetch(
                    "interactions",
                    queryset=EpisodeInteraction.objects.filter(user=request.user),
                    to_attr="user_interactions",
                )
            ),
        )
    ).annotate(
        subscribed=Exists(
            Subscription.objects.filter(user=request.user, podcast=OuterRef("pk"))
        )
    )
    podcast = get_object_or_404(queryset, pk=pk)
    paginator = Paginator(podcast.episode_set.all(), 100)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    if request.htmx:
        referer = request.META.get("HTTP_REFERER")
        if referer and urlparse(referer).path == request.path:
            return render(
                request,
                "podcasts/podcast_episode_list_partial.html",
                {"podcast": podcast, "page_obj": page_obj},
            )
        return render(
            request,
            "podcasts/podcast_detail_partial.html",
            {"podcast": podcast, "page_obj": page_obj},
        )
    else:
        return render(
            request,
            "podcasts/podcast_detail.html",
            {"podcast": podcast, "page_obj": page_obj},
        )
