from pathlib import Path

import urllib3
import xmltodict
from django.db import IntegrityError

from podcasts.models import Podcast
from podcasts.parser import ingest_podcast

p = Path("/home/jack/Downloads/podcasts_opml.xml")

opml_data = xmltodict.parse(p.read_bytes())
feed_urls = [
    outline["@xmlUrl"] for outline in opml_data["opml"]["body"]["outline"]["outline"]
]


for url in feed_urls:
    print(url)
    try:
        podcast = Podcast.objects.get(feed_link=url)
    except Podcast.DoesNotExist:
        resp = urllib3.request("GET", url=url)
        podcast = ingest_podcast(resp.data, url=resp)
