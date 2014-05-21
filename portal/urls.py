from django.conf.urls import patterns, url

from portal import views


urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^host/$', views.own_hosts),
    url(r'^host/all$', views.all_hosts),
    url(r'^host/ansible.json$', views.ansible_hosts),
    url(r'^host/new$', views.host_detail),
    url(r'^host/(?P<name>[a-zA-Z0-9-\.]+)/$', views.host_detail),
    url(r'^host/(?P<slug>[a-zA-Z0-9-\.]+)/delete/$', views.HostDelete.as_view(),
        name="host_delete"),
    url(r'^subnet/$', views.own_subnets),
    url(r'^subnet/all$', views.all_subnets),
    url(r'^subnet/new$', views.subnet_detail),
    url(r'^subnet/(?P<network>[0-9/\.]+)/$', views.subnet_detail),
    url(r'^subnet/(?P<slug>[0-9/\.]+)/delete/$',
        views.SubnetDelete.as_view(), name="subnet_delete"),
)