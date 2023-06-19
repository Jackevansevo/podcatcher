import argparse
import sqlite3
from pathlib import Path

import httpx
import xmltodict
from django.core.management.base import BaseCommand
from podcasts.models import Podcast, Subscription
from podcasts.parser import ingest_podcast


class Command(BaseCommand):
    help = "Updates all podcast feeds"

    def add_arguments(self, parser):
        parser.add_argument("input_file", nargs="?", type=argparse.FileType("r"))

    def handle(self, *args, input_file, **options):
        if input_file.name.endswith(".db"):
            con = sqlite3.connect(input_file.name)
            cur = con.cursor()
            for row in cur.execute("SELECT url, title FROM podcasts"):
                url, title = row
                try:
                    podcast, created = ingest_podcast(url)
                except Exception as ex:
                    self.stdout.write(
                        self.style.ERROR(
                            'Failed to parse "%s" "%s" "%s"' % (title, url, str(ex))
                        )
                    )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            'Successfully imported "%s" "%s"' % (title, url)
                        )
                    )
        else:
            opml_data = xmltodict.parse(input_file.read())
            body = opml_data["opml"]["body"]

            def parse(outline):
                url = outline["@xmlUrl"]
                name = outline["@text"]
                podcast, created = ingest_podcast(url)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            'Successfully imported "%s" "%s"' % (name, url)
                        )
                    )

            outline = body["outline"]

            if isinstance(outline, dict) and "outline" in outline:
                for sub_outline in outline["outline"]:
                    parse(sub_outline)
