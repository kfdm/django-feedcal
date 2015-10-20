import uuid

from django.db import models


class Feed(models.Model):
    feed = models.fields.URLField()


class Calendar(models.Model):
    calendar = models.fields.URLField()


class MergedFeed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feeds = models.ManyToManyField(Feed)


class MergedCalendar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    calendars = models.ManyToManyField(Calendar)
