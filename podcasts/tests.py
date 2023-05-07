from pathlib import Path

from django.test import TestCase

from .models import Episode, Podcast
from .parser import ingest_podcast, parse_podcast


class TestParser(TestCase):
    def test_parser(self):
        for path in (Path(__file__).parent / "testdata").glob("*.rss"):
            with self.subTest(path=path):
                data = path.read_bytes()
                ingest_podcast(data)