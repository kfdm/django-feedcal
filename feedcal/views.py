import collections
import datetime
import json
import logging
import operator

import requests
from dateutil.rrule import rruleset, rrulestr
from icalendar import Calendar, Event

from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.shortcuts import render
from django.utils import timezone
from django.views.generic.base import View

import feedcal.models
from feedcal import USER_AGENT

logger = logging.getLogger(__name__)

UNACCOUNTED_TAG = 'Unaccounted'
REMAINING_TIME = 'Remaining'


def display(cal):
    return cal.to_ical().decode('utf8').replace('\r\n', '\n').strip()


class IndexView(View):
    def get(self, request):
        return render(request, 'feedcal/index.html', {
            'calendars': feedcal.models.MergedCalendar.objects.filter()
        })


class PieView(View):
    def _date_floor(self, dt):
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    def _date_ceil(self, dt):
        return self._date_floor(dt) + datetime.timedelta(days=1)

    def get(self, request, uuid):
        '''
        Create a Google DataView suitable for being rendered as a pie chart
        '''

        now = timezone.localtime(timezone.now())

        if 'today' in request.GET:
            days = 1
        elif 'days' in request.GET:
            days = int(request.GET.get('days'))
        else:
            days = 7

        end = now
        if 'today' in request.GET:
            start = self._date_floor(now)
        else:
            start = end - datetime.timedelta(days=days)

        durations = collections.defaultdict(int)

        durations[UNACCOUNTED_TAG] = days * 24 * 60 * 60
        if 'today' in request.GET:
            durations[REMAINING_TIME] = (self._date_ceil(now) - now).total_seconds()
            durations[UNACCOUNTED_TAG] -= durations[REMAINING_TIME]

        for calset in feedcal.models.MergedCalendar.objects.filter(id=uuid):
            logger.info('Reading Calset %s', calset)
            for calendar in calset.calendars.all():
                ical = cache.get('calendar: {0}'.format(calendar.id))
                if ical is None:
                    logger.info('Reading Calendar %s %s', calendar.label, calendar.calendar)
                    response = requests.get(calendar.calendar, headers={'User-Agent': USER_AGENT, 'Referer': get_current_site(request).domain})
                    cache.set('calendar: {0}'.format(calendar.id), response.text)
                    ical = response.text
                else:
                    logger.info('Reading Calendar from Cache %s %s', calendar.label, calendar.calendar)

                ical = Calendar.from_ical(ical)

                for component in ical.subcomponents:
                    # Filter out non events
                    if 'SUMMARY' not in component:
                        continue
                    # Filter out non events
                    if 'DTSTART' not in component:
                        continue
                    if 'DTEND' not in component:
                        continue

                    if request.GET.get('tags'):
                        # Set Bucket
                        bucket = calendar.label

                        if '#' in component['SUMMARY']:
                            for word in component['SUMMARY'].split():
                                if word.startswith('#'):
                                    bucket = word.strip('#')
                    else:
                        bucket = component['SUMMARY']

                    if 'RRULE' in component:
                        for entry in rrulestr(
                                component['RRULE'].to_ical().decode('utf-8'),
                                dtstart=component['DTSTART'].dt).between(start, end):
                            duration = component['DTEND'].dt - component['DTSTART'].dt
                            logger.debug('%s %s', component['SUMMARY'], duration)
                            durations[bucket] += duration.total_seconds()
                            if UNACCOUNTED_TAG in durations:
                                durations[UNACCOUNTED_TAG] -= duration.total_seconds()
                        continue

                    # Filter out all day events
                    if not isinstance(component['DTSTART'].dt, datetime.datetime):
                        continue

                    # Filter out events that are outside our time range
                    if component['DTEND'].dt > end:
                        continue
                    if component['DTSTART'].dt < start:
                        continue

                    duration = component['DTEND'].dt - component['DTSTART'].dt
                    logger.debug('%s %s', component['SUMMARY'], duration)
                    durations[bucket] += duration.total_seconds()
                    if UNACCOUNTED_TAG in durations:
                        durations[UNACCOUNTED_TAG] -= duration.total_seconds()

        context = {'calset': calset, 'durations': json.dumps([['Label', 'Duration']] + list(
            [(label, round(duration / 60 / 60, 2)) for (label, duration) in sorted(durations.items(), key=operator.itemgetter(1), reverse=True)]
        ))}

        return render(request, 'feedcal/charts/pie.html', context)


class BarView(PieView):
    pass
