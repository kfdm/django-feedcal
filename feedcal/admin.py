from django.contrib import admin

from feedcal.models import Calendar, Feed, MergedCalendar, MergedFeed

admin.site.register(Feed)
admin.site.register(Calendar)
admin.site.register(MergedFeed)
admin.site.register(MergedCalendar)
