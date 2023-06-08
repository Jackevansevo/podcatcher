from pathlib import Path
from unittest.mock import Mock, patch

from django.test import TestCase
from httpx import Request, Response

from .parser import ingest_podcast

url_map = {
    "https://feeds.simplecast.com/xyBuzW92": "2 Bears, 1 Cave with Tom Segura & Bert Kreischer",
    "https://feeds.megaphone.fm/TPC7413106767": "Are You Garbage? Comedy Podcast",
    "https://access.acast.com/rss/512e6e5b-1328-4152-869e-16ad11c71e70/": "Athletico Mince",
    "https://feeds.fireside.fm/beamradio/rss": "Beam Radio",
    "https://feed.podbean.com/cienciasuja/feed.xml": "Ciência Suja",
    "https://corecursive.libsyn.com/feed": "CoRecursive: Coding Stories",
    "https://feeds.fireside.fm/coder/rss": "Coder Radio",
    "https://feeds.feedburner.com/cognicast": "Cognicast",
    "https://www.relay.fm/cortex/feed": "Cortex",
    "https://feeds.megaphone.fm/darknetdiaries": "Darknet Diaries",
    "https://feeds.buzzsprout.com/1121972.rss": "Deep Questions with Cal Newport",
    "https://feeds.simplecast.com/WpQaX_cs": "Django Chat",
    "https://feeds.transistor.fm/full-stack-radio": "Full Stack Radio",
    "https://anchor.fm/s/97c7ec04/podcast/rss": "GRIFTONOMICS",
    "https://anchor.fm/s/8c9756d0/podcast/rss": "Garza Podcast",
    "https://changelog.com/gotime/feed": "Go Time: Golang, Software Engineering",
    "https://feeds.simplecast.com/l2i9YnTd": "Hard Fork",
    "https://haskellweekly.news/podcast.rss": "Haskell Weekly",
    "https://hipsters.tech/feed/podcast/": "Hipsters Ponto Tech",
    "https://rss.art19.com/how-i-built-this": "How I Built This with Guy Raz",
    "https://changelog.com/jsparty/feed": "JS Party: JavaScript, CSS, Web Development",
    "https://feeds.fireside.fm/linuxunplugged/rss": "LINUX Unplugged",
    "https://lexfridman.com/feed/podcast/": "Lex Fridman Podcast",
    "https://feeds.fireside.fm/linuxactionnews/rss": "Linux Action News",
    "https://feeds.simplecast.com/7y1CbAbN": "Maintainable",
    "https://wakingup.libsyn.com/rss": "Making Sense with Sam Harris",
    "https://malicious.life/feed/podcast/": "Malicious Life",
    "https://www.omnycontent.com/d/playlist/651a251e-06e1-47e0-9336-ac5a00f41628/c7d40835-26d2-4ce6-bb56-acd401531b79/29d28dbf-9a33-4dd4-82e0-acd401531b87/podcast.rss": "Mamilos",
    "https://feeds.acast.com/public/shows/b19ac1f5-6adf-4c8b-aa1a-2af2160f99e4": "Off Menu with Ed Gamble and James Acaster",
    "https://feeds.simplecast.com/fQ3mywpV": "Offline with Jon Favreau",
    "https://feeds.transistor.fm/on-the-metal-0294649e-ec23-4eab-975a-9eb13fd94e06": "On The Metal",
    "https://anchor.fm/s/2e4db538/podcast/rss": "OsProgramadores",
    "https://feeds.transistor.fm/oxide-and-friends": "Oxide and Friends",
    "https://www.theguardian.com/politics/series/politicsweekly/podcast.xml": "Politics Weekly UK",
    "https://podcasts.files.bbci.co.uk/m0015nfd.rss": "Putin",
    "https://pythonbytes.fm/episodes/rss": "Python Bytes",
    "https://feeds.transistor.fm/rework": "Rework",
    "http://risky.biz/feeds/risky-business/": "Risky Business",
    "https://feeds.megaphone.fm/search-engine": "Search Engine",
    "https://shoptalkshow.com/feed/podcast/": "ShopTalk",
    "https://feed.podbean.com/speakingbrazilian/feed.xml": "Speaking Brazilian Podcast",
    "https://www.omnycontent.com/d/playlist/885ace83-027a-47ad-ad67-aca7002f1df8/5d83b9d2-b0e8-44e7-9293-afee0165cff3/cfe296ac-ea11-4d6e-a22b-afee0165d026/podcast.rss": "Stavvy's World",
    "https://feed.syntax.fm/rss": "Syntax - Tasty Web Development Treats",
    "https://podcasts.files.bbci.co.uk/p02pcb4w.rss": "Tailenders",
    "https://talkpython.fm/episodes/rss": "Talk Python To Me",
    "https://feeds.buzzsprout.com/1004689.rss": "Tech Won't Save Us",
    "https://www.theguardian.com/news/series/the-audio-long-read/podcast.xml": "The Audio Long Read",
    "https://feeds.fireside.fm/bikeshed/rss": "The Bike Shed",
    "https://feeds.buzzsprout.com/1817535.rss": "The Haskell Interlude",
    "https://crabfeast.libsyn.com/rss": "The HoneyDew with Ryan Sickler",
    "https://feed.podbean.com/nerdoftherings/feed.xml": "The Nerd of the Rings",
    "https://feeds.acast.com/public/shows/a8a5a759-8cb1-52ad-b50a-8e08dcee4d1f": "The Slow Newscast",
    "https://feeds.buzzsprout.com/1097978.rss": "The Sourcegraph Podcast",
    "https://daringfireball.net/thetalkshow/rss": "The Talk Show With John Gruber",
    "https://feeds.megaphone.fm/vergecast": "The Vergecast",
    "https://feeds.fireside.fm/thinkingelixir/rss": "Thinking Elixir Podcast",
    "https://www.theguardian.com/news/series/todayinfocus/podcast.xml": "Today in Focus",
    "https://feeds.simplecast.com/OhtQwqx1": "Tom Segura En Español",
    "https://feeds.listenbox.app/rss/4r06ZysvAJsy/audio.rss": "Trash Taste After Dark",
    "https://feeds.megaphone.fm/trashtaste": "Trash Taste Podcast",
    "https://feeds.megaphone.fm/STU4418364045": "Waveform: The MKBHD Podcast",
    "https://www.omnycontent.com/d/playlist/e73c998e-6e60-432f-8610-ae210140c5b1/40fa8192-202d-4013-a673-af2500f51945/62c5a2fc-0e1b-4dfb-a223-af2500f55bfa/podcast.rss": "What Future with Joshua Topolsky",
    "https://podcasts.files.bbci.co.uk/p07mdbhg.rss": "You're Dead To Me",
    "https://feeds.simplecast.com/RpkoyXpU": "Your Mom's House with Christina P. and Tom Segura",
    "https://feeds.soundcloud.com/users/soundcloud:users:220484243/sounds.rss": "defn",
}


def mock_fetch(url, **kwargs):
    return Response(
        200,
        request=Request(method="GET", url=url),
        content=(
            Path(__file__).parent / Path(f"testdata/{url_map[url]}.rss")
        ).read_bytes(),
    )


class TestParser(TestCase):
    def test_parser(self):
        with patch("podcasts.parser.httpx.get", mock_fetch):
            for url in url_map:
                podcast, _ = ingest_podcast(url)
