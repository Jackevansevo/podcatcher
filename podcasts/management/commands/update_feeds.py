from django.core.management.base import BaseCommand, CommandError

from podcasts.models import Podcast
from podcasts.parser import update_podcast


class Command(BaseCommand):
    help = "Updates all podcast feeds"

    def handle(self, *args, **options):
        for podcast in Podcast.objects.all():
            self.stdout.write(self.style.SUCCESS(f"Updated {podcast}"))
            update_podcast(podcast)
