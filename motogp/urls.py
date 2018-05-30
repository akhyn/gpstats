from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'motogp'
urlpatterns = [
    path('', views.index, name='index'),
    path('seasons/', views.seasons_view, name='seasons'),
    path('events/', views.events_view, name='events'),
    path('<int:year>/', views.season_view, name='season'),
    path('season/<int:year>/', views.season_view, name='season'),
    path('track/<str:track>', views.track_view, name='track'),
    path('event/<int:season>/<str:event_name>/', views.event_view, name='event'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
