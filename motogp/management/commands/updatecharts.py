from django.core.management.base import BaseCommand

from motogp.scraper import chart_data


class Command(BaseCommand):
    help = 'Updates the charts for specified season'

    def add_arguments(self, parser):
        parser.add_argument("-s", "--season", type=int,
                            help="force a specific season to begin parsing from",
                            )

    def handle(self, *args, **options):
        chart_data(start_year=options['season'])
