import datetime as dt
from email.utils import parsedate_to_datetime

import xmltodict


def parse_item(data):
    return {
        "title": data.get("title"),
        "description": data.get("description"),
        "site_link": data.get("link"),
        "media_link": data.get("enclosure", {}).get("@url"),
        "guid": data.get("guid", {}).get("#text"),
        "pub_date": parsedate_to_datetime(data.get("pubDate")),
    }


def parse_podcast(data):
    data = xmltodict.parse(data)
    rss = data["rss"]
    channel = rss["channel"]
    return {
        "title": channel.get("title"),
        "description": channel.get("description"),
        "site_link": channel.get("link"),
        "feed_link": channel.get("atom:link", {}).get("@href"),
        "image_link": channel.get("itunes:image", {}).get("@href"),
        "pub_date": parsedate_to_datetime(channel.get("pubDate")),
        "last_build_date": parsedate_to_datetime(channel.get("lastBuildDate")),
        "ttl": dt.timedelta(minutes=int(channel.get("ttl"))),
    }, [parse_item(item) for item in channel.get("item")]
