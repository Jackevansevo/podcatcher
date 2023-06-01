from pathlib import Path

from django.test import TestCase

from .parser import ingest_podcast


class TestParser(TestCase):
    def test_parser(self):
        for path in (Path(__file__).parent / "testdata").glob("*.rss"):
            # if path.stem != "sourcegraph":
            #     continue
            with self.subTest(path=path):
                data = path.read_bytes()
                # TODO would be nice to keep the original URL
                podcast = ingest_podcast(data, url=path)
