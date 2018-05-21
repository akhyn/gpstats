import json

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Season, EventLocation, Category, Event, MenuOptions
from .scraper import scrape_data

categories_order = ['MotoGP', '500cc', 'Moto2', '250cc', 'Moto3', '125cc', '80cc', '50cc']

def index(request):
    season = get_object_or_404(Season, year=Season.objects.all().latest().year)
    return season_view(request, season.year)


def event_view(request, season, event_name):
    y = Season.objects.get(year=int(season))
    e_loc = EventLocation.objects.get(location=event_name)
    event = get_object_or_404(Event, season=y, event_location=e_loc)
    categories = [cat.__str__() for cat in y.categories.all()]
    charts = [f'motogp/charts/{y.__str__()}-{event.__str__()}-{cat}.svg' for cat in categories_order if cat in categories]
    return render(request, 'motogp/event.html', {**{'charts': charts}, **menu_context()})


def track_view(request, track):
    e_loc = EventLocation.objects.get(location=track)
    latest_season = Event.objects.filter(event_location=e_loc).latest().season
    categories = [cat.__str__() for cat in latest_season.categories.all()]
    charts = [f'motogp/charts/{e_loc.__str__()}-{cat}.svg' for cat in categories_order if cat in categories]
    return render(request, 'motogp/event.html', {**{'charts': charts}, **menu_context()})


def season_view(request, year):
    season = get_object_or_404(Season, year=year)
    categories = [cat.__str__() for cat in season.categories.all()]
    charts = [f'motogp/charts/{season.__str__()}-{cat}.svg' for cat in categories_order if cat in categories]
    return render(request, 'motogp/season.html', {**{'charts': charts}, **menu_context()})


def seasons_view(request):
    return render(request, 'motogp/seasons.html', {**menu_context()})


def events_view(request):
    return render(request, 'motogp/events.html', {**menu_context()})


def populate(request):
    scrape_data()
    return HttpResponseRedirect(reverse('motogp:index'))


def menu_context():
    menu, created = MenuOptions.objects.get_or_create()  # Safe: only one object
    menu_data = {'menu_data': json.loads(menu.JSON_menu)}
    return menu_data
