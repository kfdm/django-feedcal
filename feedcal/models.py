import uuid

from django.db import models


class Feed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=32)
    feed = models.fields.URLField()

    def __str__(self):
        return self.label


class Calendar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=32)
    calendar = models.URLField()

    def __str__(self):
        return self.label


class MergedFeed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=32)
    feeds = models.ManyToManyField(Feed)

    def __str__(self):
        return self.label


class MergedCalendar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=32)
    calendars = models.ManyToManyField(Calendar)

    def __str__(self):
        return self.label
