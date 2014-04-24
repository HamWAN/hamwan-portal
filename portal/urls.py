from django.conf.urls import patterns, url

from portal import views


urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^host/$', views.own_hosts),
    url(r'^host/all$', views.all_hosts),
    url(r'^host/new$', views.host_detail),
    url(r'^host/(?P<name>[a-zA-Z0-9-\.]+)/$', views.host_detail),
    url(r'^subnet/$', views.own_subnets),
    url(r'^subnet/all$', views.all_subnets),
    url(r'^subnet/(?P<network>[0-9/\.]+)/$', views.subnet_detail),
)