from django.contrib import admin

from .models import Season, Session, Event, EventLocation, Rider, Result, MenuOptions, UpdateData

admin.site.register(MenuOptions)
admin.site.register(Session)
admin.site.register(Season)
admin.site.register(EventLocation)
admin.site.register(Event)
admin.site.register(Rider)
admin.site.register(Result)
admin.site.register(UpdateData)
