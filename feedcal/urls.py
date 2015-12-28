from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

import feedcal.views

urlpatterns = [
    url(r'^$', login_required(feedcal.views.IndexView.as_view()), name='index'),
    url(r'^(?P<uuid>[^/]+)/pie/$', login_required(feedcal.views.PieView.as_view()), name='pie'),
    url(r'^(?P<uuid>[^/]+)/bar/$', login_required(feedcal.views.BarView.as_view()), name='bar'),
    url(r'^parse/$', feedcal.views.ParseView.as_view(), name='parse'),
]


def subnav(namespace, request):
    print(namespace)
    if not request.user.is_authenticated():
        return {
            'Feeds': [
                ('Parse', reverse(namespace + ':parse'))
            ]
        }
    return {
        'Feeds': [
            ('Index', reverse(namespace + ':index')),
            ('Parse', reverse(namespace + ':parse')),
        ]
    }
