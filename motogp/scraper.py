import requests
import time
import re

from collections import OrderedDict

from bs4 import BeautifulSoup
from django.utils import timezone
from django.conf import settings

from .models import Season, Result, Category, Brand, Team, Session, EventLocation, UpdateData, Rider


def rate_limit(delayed_func, delay=1):
    """
    Delay function call

    Simple decorator to delay a function call

    :param delayed_func: The function to delay
    :param delay: Delay in seconds (default = 1)

    :return: Closure call for the delayed function
    """
    def wrapper(*args, **kwargs):
        time.sleep(delay)
        return delayed_func(*args, **kwargs)

    return wrapper


@rate_limit
def get_options(source_url, tag, only_accept_after=None):
    """
    Parse a BS4 tag on a page for the available menu options.

    :param source_url: The url we wish to parse.
    :param tag: The current BS4 tag we are looking at.
    :param only_accept_after: Used if we wish to discard options before this point (previously parsed)
    :return: Dictionary-compatible object containing the options. Format: {option1: [], opption2: []}
    """
    page = requests.get(source_url)
    s = BeautifulSoup(page.text, 'html.parser')

    option_source = s.find(id=tag)
    options = []
    try:
        for source in option_source.contents:
            try:
                options.append(source['value'])
            except TypeError:
                pass
    except AttributeError:
        pass
    if only_accept_after is not None:
        # reject everything prior to parameter
        candidate_options = OrderedDict()
        for option in options:
            candidate_options[option] = []
        valid_options = OrderedDict()
        start_accepting = False
        for opt in candidate_options:
            if not start_accepting:
                if opt == only_accept_after:
                    start_accepting = True
            else:
                valid_options[opt] = []
        return valid_options
    else:
        # Accept all values
        return {option: [] for option in options}


@rate_limit
def get_results_from(source_url):
    """
    Parse and organize results from a page.

    :param source_url: The actual page containing the data

    :return: The parsed data in the format: ([source_url], [event_info], [results1], [results2],..)
    """
    unwanted_items = ['Not Classified', 'Fastest Lap: ', 'Circuit Record Lap: ', 'Best Lap:', 'Pole Lap: ',
                      'Not Finished 1st Lap', 'Not Starting', 'Excluded', ]
    attempts = 5
    while attempts > 0:
        try:
            page = requests.get(source_url)
            attempts = 0
        except:
            attempts -= 1
            if attempts > 0:
                time.sleep(180)
            else:
                exit()

    s = BeautifulSoup(page.text, 'html.parser')

    event_info = ''
    try:
        event_info = s.find(class_='padbot5').text
    except AttributeError:
        pass

    col_names = s.find_all('th')
    results_table = [[item.text for item in col_names if item.text not in unwanted_items]]

    rows_count = results_line_count(page.text, unwanted_items)
    rows = s.find_all('td')
    col_count = len(results_table[0])
    row = 0
    # Create a tuple of the parsed results for each row
    while row < len(rows) and len(results_table) <= rows_count and rows[row].contents != ['\xa0']:
        rider_result = []
        try:
            if rows[row].text in unwanted_items:
                row += 1
            else:
                for col in range(col_count):
                    rider_result.append(rows[row + col].text)

                results_table.append(tuple(rider_result))
                row += col_count
        except IndexError:
            pass

    return tuple([source_url] + [event_info] + results_table)


def results_line_count(source, to_skip=None):
    """
    Return the number of results contained in a page

    :param source: The source text
    :param to_skip:  The text found in result tables that is not a result

    :return: Number of results
    """
    if to_skip is None:
        to_skip = []
    start = source.find('<tbody>')
    end = source.find('</tbody>') + len('</tbody>')

    count = source[start:end].count('</tr>')
    skip_count = 0
    for item in to_skip:
        skip_count += source[start:end].count(item)
    return count - skip_count


def scrape_data(start_season=None):
    """
    Scrape a data source for all the relevant data.

    Iterate through seasons, events, categories to gather the menu options available, then calls get_results_from to
    gather results and insert_in_database to store then.

    :param start_season: The first season to begin parsing with. (default = last season parsed)
    """
    base_page = 'http://www.motogp.com/en/Results+Statistics/'
    banned_events = ['T22', ]

    update_data, created = UpdateData.objects.get_or_create()
    if start_season is None:
        start_season = update_data.most_recent_scraped_season
        start_event = update_data.most_recent_scraped_event
    else:
        start_event = None

    seasons = [str(item) for item in list(range(start_season, timezone.now().year + 1))]
    for season in seasons:
        if settings.DEBUG:
            print(f'\nParsing season: {season}')
        events = get_options(base_page + season, 'event', only_accept_after=start_event)
        for event in events:
            if event in banned_events:
                continue
            if settings.DEBUG:
                print(f'{season}: {event}')
            categories = get_options(base_page + season + '/' + event, 'category')
            if len(categories) > 0:
                update_data.most_recent_scraped_event = event
                update_data.save(update_fields=['most_recent_scraped_event'])

            for category in categories:
                if settings.DEBUG:
                    print(f'{season}: {event}: {category}')
                sessions = get_options(base_page + season + '/' + event + '/' + category, 'session')

                for session in sessions:
                    results = get_results_from(base_page + season + '/' + event + '/' + category + '/' + session)
                    insert_in_database(season, event, category, session, results)
        update_data.most_recent_scraped_season = season
        update_data.save(update_fields=['most_recent_scraped_season'])


def chart_data(start_year=None):
    """
    Iterate through all the seasons and events to create their data charts.

    :param start_year: First year to start charting. (default = last year charted)
    """
    update_data, created = UpdateData.objects.get_or_create()
    if start_year is None:
        start_year = update_data.most_recent_charted_season
        start_event = update_data.most_recent_charted_event
        try:
            loc = EventLocation.objects.get(location=start_event)
        except EventLocation.DoesNotExist:
            loc = None
    else:
        loc = None

    years = list(range(start_year, timezone.now().year + 1))
    for year in years:
        try:
            s = Season.objects.get(year=year)
            if settings.DEBUG:
                print(f'Charting season: {year}')
        except Season.DoesNotExist:
            return
        events_temp = s.event_set.all()
        events = []
        if year == start_year and loc is not None:
            for event in events_temp:
                if event.event_location == loc:
                    events.append(event)
                elif len(events) > 0:
                    events.append(event)
        else:
            events = events_temp

        for event in events:
            event.create_event_history_chart()
            event.create_session_history_chart()
            update_data.most_recent_charted_event = event.event_location.__str__()
            update_data.save(update_fields=['most_recent_charted_event'])
        s.create_season_chart()
        update_data.most_recent_charted_season = year
        update_data.save(update_fields=['most_recent_charted_season'])


def insert_in_database(season, event, category, session, results):
    """
    Insert a set of results in the proper database objects

    :param season: Source season
    :param event: Source event
    :param category: Source category
    :param session: Source session
    :param results: Set of results
    """
    # Get or create DB references for session
    y, created = Season.objects.get_or_create(year=int(season))
    event_loc, created = EventLocation.objects.get_or_create(location=event)
    cat, created = Category.objects.get_or_create(class_name=category)
    y.categories.add(cat)
    e, created = event_loc.event_set.get_or_create(season=y, event_location=event_loc)
    e.categories.add(cat)
    is_point_event = session in ('RAC', 'RAC2')

    # RAC2 or WUP2 mean restarted sessions, find any old one and remove
    if session == 'RAC2':
        try:
            sessions = Session.objects.filter(point_event=is_point_event,
                                              category=cat,
                                              event=e,
                                              session_type='RAC',
                                              )
            for s in sessions:
                s.delete()
        except Session.DoesNotExist:
            if settings.DEBUG:
                print('Previous session should exist!', session)
            return
        session = 'RAC'
    if session == 'WUP2':
        try:
            sessions = Session.objects.filter(point_event=is_point_event,
                                              category=cat,
                                              event=e,
                                              session_type='WUP',
                                              )
            for s in sessions:
                s.delete()
        except Session.DoesNotExist:
            if settings.DEBUG:
                print('Previous session should exist!', session)
            return
        session = 'WUP'

    s, created = Session.objects.get_or_create(point_event=is_point_event,
                                               category=cat,
                                               event=e,
                                               session_type=session,
                                               source_url=results[0],
                                               )
    if is_point_event:
        # Columns where appropriate data is located for each type of result
        data = {
            'rider': 3,
            'nation': 4,
            'team': 5,
            'bike': 6,
            'speed': 7,
            'time': 8,
        }
    else:
        data = {
            'rider': 2,
            'nation': 3,
            'team': 4,
            'bike': 5,
            'speed': 6,
            'time': 7,
        }

    position = 1
    for row in results[3:]:
        try:
            rider = row[data['rider']]
            try:
                rider_last = re.search('\ [A-ZÓÑØÜÄÖÉÚÁÉ(Mc)]([A-ZÓÜÑØÄÖÉÚÁÉ(Mc)(Jr)\'\-\ ])*.?$', rider).group(0)
            except:
                if settings.DEBUG:
                    print(f'rider_last Error!: s={season}, e={event}, c={category}, sesh={session}, r={rider}\n{row}\n')
                continue
            rider_last = rider_last.strip().lower()
            rider_first = rider[:rider.find(rider_last)].strip().lower()
            if len(rider) < 1 or len(rider_last) < 1 or len(rider_first) < 1:
                # Unparseable result, ignored
                continue
            r, created = Rider.objects.get_or_create(
                full_name=rider,
                last_name=rider_last,
                first_name=rider_first,
                nationality=row[data['nation']].lower())
            r.save()
        except IndexError:
            continue

        t, created = Team.objects.get_or_create(team_name=row[data['team']])
        b, created = Brand.objects.get_or_create(brand_name=row[data['bike']])

        speed = row[data['speed']]
        lap_time = row[data['time']]

        new = Result(rider=r, brand=b, team=t, session=s, top_speed=speed, time=lap_time, position=position)
        new.save()
        position += 1
