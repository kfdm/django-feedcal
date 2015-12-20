from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

import feedcal.views

urlpatterns = patterns(
    '',
    url(r'^$', login_required(feedcal.views.IndexView.as_view()), name='index'),
    url(r'^(?P<uuid>[^/]+)/pie/$', login_required(feedcal.views.PieView.as_view()), name='pie'),
    url(r'^(?P<uuid>[^/]+)/bar/$', login_required(feedcal.views.BarView.as_view()), name='bar'),
    url(r'^parse/$', feedcal.views.ParseView.as_view(), name='parse'),
)
