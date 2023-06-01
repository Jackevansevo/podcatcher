import datetime as dt
from email.utils import parsedate_to_datetime
from http import HTTPStatus

import urllib3
import xmltodict
from django.db import IntegrityError

from .models import Episode, Podcast


def ingest_podcast(data, url=None):
    parsed_podcast, parsed_episodes = parse_podcast(data)

    if not parsed_podcast.get("feed_link") and url is not None:
        parsed_podcast["feed_link"] = url

    try:
        podcast = Podcast.objects.get(feed_link=parsed_podcast["feed_link"])
    except Podcast.DoesNotExist:
        podcast = Podcast(**parsed_podcast)
        podcast.save()
        for parsed_episode in parsed_episodes:
            if not parsed_episode.get("media_link"):
                continue

            episode = Episode(**parsed_episode, podcast=podcast)
            episode.save()
    else:
        breakpoint()
    return podcast


def parse_guid(guid):
    if isinstance(guid, str):
        return guid
    elif isinstance(guid, dict):
        return guid.get("#text")


def parse_item(data):
    return {
        "title": data.get("title"),
        "description": data.get("description", data.get("content:encoded")),
        "site_link": data.get("link", data.get("enclosure", {}).get("@url")),
        "media_link": data.get("enclosure", {}).get("@url"),
        "guid": parse_guid(data.get("guid")),
        "pub_date": parsedate_to_datetime(data.get("pubDate")),
    }


def parse_podcast(data):
    data = xmltodict.parse(data)
    rss = data["rss"]
    channel = rss["channel"]
    pub_date = channel.get("pubDate")
    last_build_date = channel.get("lastBuildDate")
    ttl = channel.get("ttl")
    return {
        "title": channel.get("title"),
        "description": channel.get("description"),
        "site_link": channel.get("link"),
        "feed_link": channel.get("atom:link", channel.get("itunes:new-feed-url", {})),
        "image_link": channel.get("itunes:image", {}).get("@href"),
        "pub_date": parsedate_to_datetime(pub_date) if pub_date is not None else None,
        "last_build_date": parsedate_to_datetime(last_build_date)
        if last_build_date is not None
        else None,
        "ttl": dt.timedelta(minutes=int(ttl)) if ttl is not None else None,
    }, [parse_item(item) for item in channel.get("item")]


def update_podcast(podcast):
    headers = {}

    if podcast.etag:
        headers["If-None-Match"] = podcast.etag

    print("sending", headers)
    resp = urllib3.request("GET", podcast.feed_link, headers=headers)

    if resp.status == HTTPStatus.NOT_MODIFIED:
        print("nothing changed", resp.data)
        return podcast

    _, parsed_episodes = parse_podcast(resp.data)
    guids = set(podcast.episode_set.values_list("guid", flat=True))
    for parsed_episode in parsed_episodes:
        if parsed_episode["guid"] not in guids:
            print("adding episode", parsed_episode["title"])
            episode = Episode(**parsed_episode, podcast=podcast)
            episode.save()

    print(resp.headers)
    etag = resp.headers.get("ETag")
    if etag is not None:
        podcast.etag = etag
        podcast.save(update_fields=["etag"])

    return podcast
