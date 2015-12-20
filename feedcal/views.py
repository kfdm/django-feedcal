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
from django import forms

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


class ParseView(View):
    def _date_floor(self, dt):
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    def _date_ceil(self, dt):
        return self._date_floor(dt) + datetime.timedelta(days=1)

    def _get_cal(self, request, calendar_url):
        ical = cache.get('calendar: {0}'.format(calendar_url))
        if ical is not None:
            return ical

        logger.info('Reading Calendar %s', calendar_url)
        response = requests.get(calendar_url, headers={'User-Agent': USER_AGENT, 'Referer': get_current_site(request).domain})
        cache.set('calendar: {0}'.format(calendar_url), response.text)
        return response.text

    def _get_buckets(self, request, date):
        days = int(request.GET.get('days', 7))
        now = timezone.localtime(timezone.now())

        if date == 'today':
            days = 1
            start = self._date_floor(now)
            end = now
        elif date == 'yesterday':
            days = 1
            end = self._date_floor(now)
            start = end - datetime.timedelta(days=days)
        else:
            # TODO: Parse date. Just use 'today' for now
            end = now
            start = end - datetime.timedelta(days=days)

        durations = collections.defaultdict(int)

        durations[UNACCOUNTED_TAG] = days * 24 * 60 * 60
        if date == 'today':
            durations[REMAINING_TIME] = (self._date_ceil(now) - now).total_seconds()
            durations[UNACCOUNTED_TAG] -= durations[REMAINING_TIME]

        return durations, start, end

    def filter_calendar(self, ical, start, end):
        for component in ical.subcomponents:
            if 'SUMMARY' not in component:
                continue
            # Filter out non events
            if 'DTSTART' not in component:
                continue
            if 'DTEND' not in component:
                continue

            if 'RRULE' in component:
                for entry in rrulestr(
                        component['RRULE'].to_ical().decode('utf-8'),
                        dtstart=component['DTSTART'].dt).between(start, end):
                    duration = component['DTEND'].dt - component['DTSTART'].dt
                    logger.debug('%s %s', component['SUMMARY'], duration)
                    yield duration.total_seconds(), component['SUMMARY']

            # Filter out all day events
            if not isinstance(component['DTSTART'].dt, datetime.datetime):
                continue

            # Filter out events that are outside our time range
            if component['DTSTART'].dt > end:
                continue
            if component['DTEND'].dt < start:
                continue

            duration = min(component['DTEND'].dt, end) - max(component['DTSTART'].dt, start)
            yield duration.total_seconds(), component['SUMMARY']

    def get(self, request):
        class NameForm(forms.Form):
            calendar = forms.CharField(label='Calendar')
            date = forms.CharField(label='Date', initial='today')
            days = forms.IntegerField(label='Days', initial=7)

        date = request.GET.get('date')
        calendar = request.GET.get('calendar')

        if calendar is None:
            return render(request, 'feedcal/parse.html')
        context = {
            'form': NameForm(request.GET),
            'calendar': calendar,
        }

        ical = self._get_cal(request, calendar)
        ical = Calendar.from_ical(ical)

        durations, start, end = self._get_buckets(request, date)

        for duration, label in self.filter_calendar(ical, start, end):
            durations[label] += duration
            if UNACCOUNTED_TAG in durations:
                durations[UNACCOUNTED_TAG] -= duration

        context['durations'] = json.dumps([['Label', 'Duration']] + list(
            [(label, round(duration / 60 / 60, 2)) for (label, duration) in sorted(durations.items(), key=operator.itemgetter(1), reverse=True)]
        ))

        return render(request, 'feedcal/parse.html', context)


class PieView(ParseView):
    def get(self, request, uuid):
        '''
        Create a Google DataView suitable for being rendered as a pie chart

        @param date string: today, yesterday, yyyymmdd
        @param days integer:
        '''

        date = request.GET.get('date')
        durations, start, end = self._get_buckets(request, date)

        for calset in feedcal.models.MergedCalendar.objects.filter(id=uuid):
            logger.info('Reading Calset %s', calset)
            for calendar in calset.calendars.all():
                ical = self._get_cal(request, calendar.calendar)

                ical = Calendar.from_ical(ical)

                for duration, label in self.filter_calendar(ical, start, end):
                    bucket = label
                    if request.GET.get('tags'):
                        # Set Bucket
                        bucket = calendar.label
                        if '#' in label:
                            for word in label.split():
                                if word.startswith('#'):
                                    bucket = word.strip('#')

                    logger.debug('%s %s', label, duration)
                    durations[bucket] += duration
                    if UNACCOUNTED_TAG in durations:
                        durations[UNACCOUNTED_TAG] -= duration

        context = {'calset': calset, 'durations': json.dumps([['Label', 'Duration']] + list(
            [(label, round(duration / 60 / 60, 2)) for (label, duration) in sorted(durations.items(), key=operator.itemgetter(1), reverse=True)]
        ))}

        return render(request, 'feedcal/charts/pie.html', context)


class BarView(PieView):
    pass
