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


def parse_feed_link(data):
    if isinstance(data, dict):
        return data.get("@href")
    elif isinstance(data, list):
        for elem in data:
            if elem.get("@rel") == "self":
                return parse_feed_link(elem)


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
        "feed_link": parse_feed_link(channel.get("atom:link", {})),
        "image_link": channel.get("itunes:image", {}).get("@href"),
        "pub_date": parsedate_to_datetime(pub_date) if pub_date is not None else None,
        "last_build_date": parsedate_to_datetime(last_build_date)
        if last_build_date is not None
        else None,
        "ttl": dt.timedelta(minutes=int(ttl)) if ttl is not None else None,
    }, [parse_item(item) for item in channel.get("item")]
