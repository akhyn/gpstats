from django.core.management.base import BaseCommand

from motogp.scraper import scrape_data, chart_data


class Command(BaseCommand):
    help = 'Updates the charts for specified season'

    def add_arguments(self, parser):
        parser.add_argument("-s", "--season", type=int,
                            help="force a specific season to begin parsing from",
                            )
        parser.add_argument("-e", "--event", type=str,
                            help="force a specific event to begin parsing from",
                            )

    def handle(self, *args, **options):
        scrape_data(start_season=options['season'], start_event=options['event'])
        chart_data(start_year=options['season'], start_event=options['event'])
