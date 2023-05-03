from pathlib import Path

from django.test import TestCase

from .models import Episode, Podcast
from .parser import parse_podcast


class TestParser(TestCase):
    def test_parser(self):
        with Path(__file__).parent / "testdata/talk_python.rss" as f:
            data = f.read_bytes()
        parsed_podcast, parsed_episodes = parse_podcast(data)
        self.assertIsNotNone(data)
        self.assertIsNotNone(parsed_episodes)
        self.assertEqual(len(parsed_episodes), 4)
        podcast = Podcast(**parsed_podcast)
        podcast.save()
        for parsed_episode in parsed_episodes:
            episode = Episode(**parsed_episode, podcast=podcast)
            episode.save()

        self.assertEqual(Podcast.objects.count(), 1)
        self.assertEqual(Episode.objects.count(), 4)
