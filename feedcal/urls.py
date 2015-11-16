from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

import feedcal.views

urlpatterns = patterns(
    '',
    url(r'^pie\.values', login_required(feedcal.views.PieView.as_view())),
    url(r'^pie', login_required(TemplateView.as_view(template_name="feedcal/charts/pie.html"))),
)
