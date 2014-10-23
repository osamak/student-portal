from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from activities import views
from niqati import views as niqati_views

urlpatterns = patterns('',
    url(r'^$', views.list_activities, name='list'),
    url(r'^create/$', views.create, name='create'),
    url(r'^(?P<activity_id>\d+)/$', views.show, name='show'),
    url(r'^(?P<activity_id>\d+)/edit/$', views.edit, name='edit'),
    url(r'^(?P<activity_id>\d+)/review/$', views.review, name='review'),
    url(r'^(?P<activity_id>\d+)/review/(?P<lower_review_type>\w)/$', views.review, name='review_with_type'),
    url(r'^(?P<activity_id>\d+)/participate/$', views.participate, name='participate'),
    url(r'^(?P<activity_id>\d+)/niqati/$', niqati_views.coordinator_view, name='niqati_orders'),
    # url(r'^(?P<activity_id>\d+)/niqati/create/$', niqati_views.coordinator_view, name='niqati_create'),
)
