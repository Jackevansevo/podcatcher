import datetime as dt
import hashlib
import os
import time
from http import HTTPStatus

import httpx
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import URLValidator
from django.db import transaction
from django.db.models import Exists, OuterRef, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
from django.views.generic.detail import View
from django.views.generic.list import ListView

from .models import Episode, EpisodeInteraction, Podcast, Subscription
from .parser import ingest_podcast, parse_podcast


@require_POST
def mark_playing(request, pk):
    # TODO, when a user clicks 'play' we can replace the playing audio bottom bar with
    # a new HTMX partial with all the appropriate episode details, then begin playing on
    # load
    interaction, _ = EpisodeInteraction.objects.update_or_create(
        episode_id=pk, user=request.user
    )
    print("made it here")
    print(interaction.episode)
    if request.htmx:
        return render(
            request,
            "podcasts/player_bar_partial.html",
            {"playing": True, "episode": interaction.episode},
        )
    else:
        raise NotImplementedError("only supports htmx")


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
                podcast, _ = ingest_podcast(url)
            except httpx.HTTPError as ex:
                messages.error(request, f"Failed to fetch podcast: {str(ex)}")
                referer = request.META.get("HTTP_REFERER")
                return redirect(referer)
            else:
                Subscription.objects.get_or_create(podcast=podcast, user=request.user)
                return redirect(podcast)


@require_GET
def search(request):
    search_term = request.GET.get("search")

    # determine if the search term is a link
    validate = URLValidator()

    is_url = True
    try:
        validate(search_term)
    except ValidationError:
        is_url = False

    if is_url:
        try:
            podcast = Podcast.objects.get(feed_link=search_term)
        except Podcast.DoesNotExist:
            resp = httpx.get(search_term, follow_redirects=True)
            parsed_podcast, parsed_episodes = parse_podcast(resp.content)
            results = {
                "feeds": [
                    {
                        "title": parsed_podcast["title"],
                        "image": parsed_podcast["image_link"],
                        "url": parsed_podcast["feed_link"],
                        "lastUpdateTime": parsed_podcast.get("last_build_date")
                        or parsed_episodes[0]["pub_date"],
                    }
                ]
            }
        else:
            return redirect(podcast.get_absolute_url() + "?external_redirect=True")
    else:
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

        resp = httpx.post(url, headers=headers)

        results = {}
        if resp.status_code == HTTPStatus.OK:
            results = resp.json()

        if results.get("feeds"):
            subscriptions = set(
                Subscription.objects.filter(user=request.user).values_list(
                    "podcast__feed_link", flat=True
                )
            )
            for index, result in enumerate(results["feeds"]):
                results["feeds"][index]["subscribed"] = result["url"] in subscriptions

                results["feeds"][index][
                    "lastUpdateTime"
                ] = dt.datetime.utcfromtimestamp(
                    results["feeds"][index]["lastUpdateTime"]
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
    paginate_by = 500

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["component"] = "podcasts/episode_list_item_with_cover_art_partial.html"
        return context

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
            interactions__listened=False,
        )


class EpisodeDetailView(View):
    def get(self, request, podcast_id, episode_id):
        episode = get_object_or_404(Episode, podcast_id=podcast_id, id=episode_id)
        context = {
            "episode": episode,
        }
        if self.request.htmx:
            template = "podcasts/episode_detail_partial.html"
        else:
            template = "podcasts/episode_detail.html"

        return render(request, template, context)


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
    paginator = Paginator(podcast.episode_set.all(), 500)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    if request.htmx:
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
