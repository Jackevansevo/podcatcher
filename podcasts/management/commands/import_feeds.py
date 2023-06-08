import argparse
from pathlib import Path

import httpx
import xmltodict
from django.core.management.base import BaseCommand

from podcasts.models import Podcast, Subscription
from podcasts.parser import ingest_podcast


class Command(BaseCommand):
    help = "Updates all podcast feeds"

    def add_arguments(self, parser):
        parser.add_argument("opml_file", nargs="?", type=argparse.FileType("r"))

    def handle(self, *args, **options):
        opml_data = xmltodict.parse(options["opml_file"].read())
        outlines = [opml_data["opml"]["body"]["outline"]["outline"]]
        for outline in outlines:
            for sub_outline in outline:
                url = sub_outline["@xmlUrl"]
                name = sub_outline["@text"]
                try:
                    podcast = Podcast.objects.get(feed_link=url)
                except Podcast.DoesNotExist:
                    resp = httpx.get(url=url, follow_redirects=True)
                    self.stdout.write('Fetching "%s"' % url)
                    if resp.url != url:
                        self.stdout.write(
                            self.style.WARNING(
                                '%s %s redirected -> "%s"' % (name, url, resp.url)
                            )
                        )
                        try:
                            podcast = Podcast.objects.get(feed_link=resp.url)
                        except Podcast.DoesNotExist:
                            pass
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    '"%s" "%s" already exists' % (name, resp.url)
                                )
                            )
                            continue

                    podcast, created = ingest_podcast(resp)
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                'Successfully imported "%s" "%s"' % (name, url)
                            )
                        )
