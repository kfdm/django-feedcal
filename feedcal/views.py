import collections
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
from icalendar import Calendar, Event
from django.utils import timezone
import requests
from django.core.cache import cache
import feedcal.models
import operator
import datetime

import logging

logger = logging.getLogger(__name__)

def display(cal):
    return cal.to_ical().decode('utf8').replace('\r\n', '\n').strip()

class PieView(View):
    def get(self, request):
        '''
        Create a Google DataView suitable for being rendered as a pie chart
        '''

        end = timezone.now()
        start = end - datetime.timedelta(days=7)
        print(end)
        print(start)

        dataset = {'cols': [
            {'id': 'Category', 'type': 'string'},
            {'id': 'Duration', 'type': 'number'},
        ], 'rows': []}

        durations = collections.defaultdict(int)

        for calset in feedcal.models.MergedCalendar.objects.all():
            logger.info('Reading Calset %s', calset)
            for calendar in calset.calendars.all():
                ical = cache.get('calendar: {0}'.format(calendar.id))
                if ical is None:
                    logger.info('Reading Calendar %s %s', calendar.label, calendar.calendar)
                    response = requests.get(calendar.calendar)
                    cache.set('calendar: {0}'.format(calendar.id), response.text)
                    ical = response.text
                else:
                    logger.info('Reading Calendar from Cache %s %s', calendar.label, calendar.calendar)

                ical = Calendar.from_ical(ical)

                for component in ical.subcomponents:
                    if 'RRULE' in component:
                        print('-' * 80)
                        print(component['DTSTART'].dt)
                        print(component['DTEND'].dt)
                        print(display(component))
                        print('-' * 80)
                        continue

                    # Filter out non events
                    if 'DTSTART' not in component:
                        continue
                    if 'DTEND' not in component:
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

                    #durations[calendar.label] += (component['DTEND'].dt - component['DTSTART'].dt).seconds
                    durations[component['SUMMARY']] += duration.seconds

        for category, value in sorted(durations.items(), key=operator.itemgetter(1), reverse=True):
            dataset['rows'].append({'c': [{'v': category}, {'v': round(value / 60, 2)}]})

        response = HttpResponse(content_type='application/json')
        response.write('google.visualization.Query.setResponse(' + json.dumps({
            'version': '0.6',
            'table': dataset,
            'reqId': '0',
            'status': 'ok',
        }) + ');')
        return response
