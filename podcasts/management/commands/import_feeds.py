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
                podcast, created = ingest_podcast(url)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            'Successfully imported "%s" "%s"' % (name, url)
                        )
                    )
