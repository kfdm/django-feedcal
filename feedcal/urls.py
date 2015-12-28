from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

import feedcal.views

urlpatterns = [
    url(r'^$', login_required(feedcal.views.IndexView.as_view()), name='index'),
    url(r'^(?P<uuid>[^/]+)/pie/(?P<date>(today|yesterday))?$', login_required(feedcal.views.PieView.as_view()), name='pie'),
    url(r'^(?P<uuid>[^/]+)/pie/(?P<date>\d{4}\-\d{2}\-\d{2})$', login_required(feedcal.views.PieView.as_view()), name='pie'),
    url(r'^(?P<uuid>[^/]+)/bar/$', login_required(feedcal.views.BarView.as_view()), name='bar'),
    url(r'^parse/$', feedcal.views.ParseView.as_view(), name='parse'),
]


def subnav(namespace, request):
    print(request.resolver_match)
    if not request.user.is_authenticated():
        return {
            _('Feeds'): [
                (_('parse'), reverse(namespace + ':parse'))
            ]
        }
    return {
        _('Feeds'): [
            (_('index'), reverse(namespace + ':index')),
            (_('parse'), reverse(namespace + ':parse')),
        ]
    }
