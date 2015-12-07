from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

import feedcal.views

urlpatterns = patterns(
    '',
    url(r'^pie/(?P<uuid>[^/]+)/$', login_required(feedcal.views.PieView.as_view())),
)
