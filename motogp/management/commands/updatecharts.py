from django.core.management.base import BaseCommand

from motogp.scraper import chart_data
from motogp.models import MenuOptions


class Command(BaseCommand):
    help = 'Updates the charts for specified season'

    def add_arguments(self, parser):
        parser.add_argument("-s", "--season", type=int,
                            help="force a specific season to begin parsing from",
                            )

    def handle(self, *args, **options):
        chart_data(start_year=options['season'])
        m, c = MenuOptions.objects.get_or_create()  # Force update
        m.save()
