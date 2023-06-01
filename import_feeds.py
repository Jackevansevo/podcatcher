from pathlib import Path

import httpx
import xmltodict
from django.contrib.auth.models import User
from django.db import IntegrityError

from podcasts.models import Podcast, Subscription
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
        resp = httpx.get(url=url, follow_redirects=True)
        podcast = ingest_podcast(resp)

    user = User.objects.first()
    Subscription.objects.create(user=user, podcast=podcast)
