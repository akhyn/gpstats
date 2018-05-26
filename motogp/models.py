import json

from collections import OrderedDict

from django.db import models
from django.conf import settings

from motogp.charts import create_chart

app_name = 'motogp'


class Category(models.Model):
    class_name = models.CharField(max_length=50)

    def __str__(self):
        return self.class_name


class EventLocation(models.Model):
    location = models.CharField(max_length=50)

    def __str__(self):
        return self.location


class Season(models.Model):
    year = models.IntegerField()
    categories = models.ManyToManyField(Category)

    def create_season_chart(self):
        modern_points = {
            1: 25,
            2: 20,
            3: 16,
            4: 13,
            5: 11,
            6: 10,
            7: 9,
            8: 8,
            9: 7,
            10: 6,
            11: 5,
            12: 4,
            13: 3,
            14: 2,
            15: 1,
        }
        results = {cat.__str__(): {} for cat in self.categories.all()}
        for cat in results:
            results[cat]['title'] = f'{str(self.year)} {cat} Championship'
            results[cat]['columns'] = []
            for event in self.event_set.all():
                try:
                    if Category.objects.get(class_name=cat) in event.categories.all():
                        results[cat]['columns'].append(event.__str__())
                except Category.DoesNotExist:
                    return
        counts = {cat: 0 for cat in results}
        for cat in results:
            events = self.event_set.all()
            for event in events:
                try:
                    session = Session.objects.get(point_event=True, category=Category.objects.get(class_name=cat), event=event)
                except Session.DoesNotExist:
                    continue

                # Prepare slots for new score
                for rider in results[cat]:
                    if rider not in ['title', 'columns', ]:
                        if len(results[cat][rider]) > 1:
                            results[cat][rider].append(results[cat][rider][-1])
                        else:
                            results[cat][rider].append(0)

                session_results = session.result_set.all()
                for result in session_results:
                    rider = result.rider.__str__()
                    if rider not in results[cat]:
                        # New rider: update old scores at 0
                        results[cat][rider] = [0 for _ in range(counts[cat] + 1)]
                    try:
                        results[cat][rider][-1] = results[cat][rider][-2] + modern_points.get(result.position, 0)
                    except IndexError:
                        # First event
                        results[cat][rider][-1] = modern_points.get(result.position, 0)

                counts[cat] += 1

                # Re-order by latest position for display reasons
                title = results[cat].pop('title')
                columns = results[cat].pop('columns')
                new_order = OrderedDict(reversed(sorted(results[cat].items(), key=lambda x: x[-1])))
                new_order['title'] = title
                new_order['columns'] = columns
                results[cat] = new_order

        # Save in static files
        for category in results:
            chart = create_chart(results[category], style='aggregate')
            with open(settings.BASE_DIR + f"/{app_name}/static/{app_name}/charts/{self.year}-{category}.svg", 'wb') as file:
                file.write(chart)

    def __str__(self):
        return str(self.year)

    class Meta:
        get_latest_by = 'year'


class Rider(models.Model):
    full_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    nationality = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.first_name[0].upper()}. {self.last_name.upper()}'


class Brand(models.Model):
    brand_name = models.CharField(max_length=50)

    def __str__(self):
        return self.brand_name


class Team(models.Model):
    team_name = models.CharField(max_length=100)

    def __str__(self):
        return self.team_name


class Event(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    event_location = models.ForeignKey(EventLocation, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)

    def create_event_history_chart(self, season_count=5):
        results = {}
        result_counts = {}

        motogp_present = False
        moto2_present = False
        moto3_present = False
        for year in reversed(range(self.season.year - season_count, self.season.year + 1)):
            try:
                season = Season.objects.get(year=year)
            except Season.DoesNotExist:
                continue
            try:
                event = Event.objects.get(season=season, event_location=self.event_location)
            except Event.DoesNotExist:
                continue

            categories = season.categories.all()
            for category in categories:
                try:
                    session = Session.objects.get(category=category, event=event, point_event=True)
                except Session.DoesNotExist:
                    continue

                cat = category.__str__()
                if cat == 'MotoGP':
                    motogp_present = True
                elif cat == 'Moto2':
                    moto2_present = True
                elif cat == 'moto3':
                    moto3_present = True
                elif cat == '500cc' and motogp_present is True:
                    cat = 'MotoGP'
                elif cat == '250cc' and moto2_present is True:
                    cat = 'Moto2'
                elif cat == '125cc' and moto3_present is True:
                    cat = 'Moto3'
                if cat not in results:
                    results[cat] = {'title': f'{event.event_location.__str__()} {cat} Results History', 'columns': []}
                if cat not in result_counts:
                    result_counts[cat] = 1
                else:
                    result_counts[cat] += 1

                session_results = session.result_set.all()
                if len(session_results) > 0:
                    results[cat]['columns'] = [str(year)] + results[cat]['columns']
                for result in session_results:
                    rider = result.rider.__str__()

                    if rider not in results[cat]:
                        results[cat][rider] = [] + [None for _ in range(result_counts[cat] - 1)]

                    results[cat][rider] = [result.position] + results[cat][rider]

                for rider in results[cat]:
                    if rider not in ['columns', 'title']:
                        while len(results[cat][rider]) < result_counts[cat]:
                            results[cat][rider] = [None] + results[cat][rider]

        # Save in static files
        for category in results:
            chart = create_chart(results[category], high_score_first=True)
            with open(settings.BASE_DIR + f"/{app_name}/static/{app_name}/charts/{self.__str__()}-{category}.svg", 'wb') as file:
                file.write(chart)

    def create_session_history_chart(self):
        count_riders_skipping_Q1 = 10
        results = {session.category.__str__(): OrderedDict() for session in self.session_set.all()}
        for cat in results:
            results[cat]['times'] = {}
            results[cat]['title'] = f'{self.event_location.__str__()} {self.season.__str__()} {cat} Results'
            results[cat]['columns'] = [session.session_type for session in self.session_set.all() if cat == session.category.__str__()]

        if self.season.year < 2005:
            session_order = ['RAC']
        elif 2006 <= self.season.year <= 2008:
            session_order = ['FP1', 'QP1', 'FP2', 'QP2', 'QP', 'WUP', 'RAC']
        else:
            session_order = ['FP1', 'FP2', 'FP3', 'FP4', 'QP', 'Q1', 'Q2', 'WUP', 'RAC']
        counts = {cat: 0 for cat in results}
        for cat in results:
            for session in session_order:
                try:
                    s = Session.objects.get(event=self, session_type=session, category=Category.objects.get(class_name=cat))
                    # Prepare slots for new score
                    for rider in results[cat]:
                        if rider not in ['title', 'columns', 'times']:
                            results[cat][rider].append(None)

                    # Store result
                    last_position = -100
                    session_results = s.result_set.all()
                    for result in session_results:
                        rider = result.rider.__str__()

                        # Rider missed previous sessions: catch up results
                        if rider not in results[cat]:
                            results[cat][rider] = [None for _ in range(counts[cat] + 1)]

                        # Store time of first 3 sessions for Q1/Q2
                        if s.session_type in ('FP1', 'FP2', 'FP3'):
                            if rider not in results[cat]['times'] or result.time < results[cat]['times'][rider]:
                                results[cat]['times'][rider] = result.time

                        if s.session_type == 'RAC' and len(results[cat]) < 4: # Old race only result
                            results[cat][rider] = [result.position]

                        results[cat][rider][-1] = result.position
                        if s.session_type == 'Q1':  # Make room for rider times good enough to skip Q1
                            results[cat][rider][-1] += count_riders_skipping_Q1
                        last_position = max(last_position, results[cat][rider][-1])

                    # Session specific adjustments
                    if s.session_type == 'Q1':
                        # Fastest riders get to skip Q1, their position is based on best lap times
                        fastest_times = {}
                        for rider in results[cat]['times']:
                            lap_time = results[cat]['times'][rider]
                            fastest_times[lap_time] = rider
                        position = 1
                        for lap_time in sorted(fastest_times.keys()):
                            results[cat][fastest_times[lap_time]][-1] = position
                            position += 1
                            if position > count_riders_skipping_Q1:
                                break
                    elif s.session_type == 'Q2':
                        # Give missing riders their previous results
                        for rider in results[cat]:
                            if rider not in ['title', 'columns', 'times'] and results[cat][rider][-1] is None:
                                results[cat][rider][-1] = results[cat][rider][-2]
                    elif s.session_type == 'RAC':
                        # Place missing riders at bottom
                        for rider in results[cat]:
                            if rider not in ['title', 'columns', 'times']:
                                if results[cat][rider][-1] is None:
                                    results[cat][rider][-1] = last_position + 1
                                    last_position += 1
                    counts[cat] += 1
                except Session.DoesNotExist:
                    continue

            # Re-sort results by most recent rider result (for display reasons)
            new_order = OrderedDict()
            del results[cat]['times']
            new_order['columns'] = results[cat].pop('columns')
            new_order['title'] = results[cat].pop('title')
            by_latest_pos = {}
            for rider in results[cat]:
                if results[cat][rider][-1] is not None:
                    by_latest_pos[results[cat][rider][-1]] = (rider, results[cat][rider])
            pos = 1
            while pos in by_latest_pos:
                new_order[by_latest_pos[pos][0]] = by_latest_pos[pos][1]
                pos += 1
            results[cat] = new_order

        # Save in static files
        for category in results:
            chart = create_chart(results[category], high_score_first=True)
            with open(settings.BASE_DIR + f"/{app_name}/static/{app_name}/charts/{self.season.__str__()}-{self.__str__()}-{category}.svg", 'wb') as file:
                file.write(chart)

    def __str__(self):
        return f'{self.event_location.__str__()}'

    class Meta:
        get_latest_by = 'season'


class Session(models.Model):
    session_type = models.CharField(max_length=50)
    point_event = models.BooleanField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    source_url = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.event}-{self.session_type}: race={self.point_event}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        m, c = MenuOptions.objects.get_or_create()  # Force update
        m.save()


class Result(models.Model):
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    position = models.IntegerField(default=0)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    top_speed = models.CharField(max_length=10)
    time = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.rider.__str__()} on {self.brand.__str__()}'


class UpdateData(models.Model):
    most_recent_scraped_season = models.IntegerField(default=1993)
    most_recent_scraped_event = models.CharField(max_length=10, default='')
    most_recent_charted_season = models.IntegerField(default=1993)
    most_recent_charted_event = models.CharField(max_length=10, default='')


class MenuOptions(models.Model):
    JSON_menu = models.CharField(max_length=2000)

    def save(self, *args, **kwargs):
        menu_data = {
            'season_data': {},
            'event_data': {},
        }

        seasons = Season.objects.all()
        for season in seasons:
            year = season.__str__()
            menu_data['season_data'][year] = {}

            events = Event.objects.filter(season=season)
            for event in events:
                loc = event.__str__()
                menu_data['season_data'][year][loc] = {}

                classes = event.categories.all()
                for category in classes:
                    cat = category.__str__()
                    menu_data['season_data'][year][loc][cat] = True

        locations = EventLocation.objects.all()
        for location in locations:
            loc = location.__str__()
            menu_data['event_data'][loc] = {}

            events = Event.objects.filter(event_location=location)
            for event in events:
                season = event.season.__str__()
                menu_data['event_data'][loc][season] = {}

                categories = event.categories.all()
                for category in categories:
                    cat = category.__str__()
                    menu_data['event_data'][loc][season][cat] = True

        self.JSON_menu = json.dumps(menu_data)
        super().save(*args, **kwargs)

