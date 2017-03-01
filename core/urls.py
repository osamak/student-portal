from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

urlpatterns = patterns('',
    url(r'^$', 'core.views.portal_home', name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^aboutsc/$', 'core.views.about_sc', name='about_sc'),
    url(r'^copy/$', TemplateView.as_view(template_name='copy.html'), name='copy'),
    url(r'^debate/$', 'core.views.debate', name='debate'),
    url(r'^indicators/$', 'core.views.indicators', name='indicators'),
    url(r'^indicators/(?P<city_code>\w)/$', 'core.views.indicators', name='indicators_for_city'),
    url(r'^aboutsc/(deanship_cp4)/$', RedirectView.as_view(pattern_name='media:show_post'), name='cp4_bader'),
    url(r'^visit/(?P<pk>\d+)/$', "core.views.visit_announcement", name='visit_announcement'),
    url(r'^cancel_twitter_connection$', "core.views.cancel_twitter_connection", name='cancel_twitter_connection'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^user_count/$', TemplateView.as_view(template_name='user_count.html'), name='user_count'),
    url(r'^user_count/update$', "core.views.update_user_count", name='update_user_count'),
)
