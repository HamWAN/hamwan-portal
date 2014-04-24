from django.conf.urls import patterns, url

import views


urlpatterns = patterns('',
    url(r'^$', views.own_dns),
    url(r'^all/$', views.all_dns),
    url(r'^new/$', views.RecordCreate.as_view(), name="record_create"),
    url(r'^(?P<pk>\d+)/$', views.RecordUpdate.as_view(), name="record_update"),
    url(r'^(?P<pk>\d+)/delete/$', views.RecordDelete.as_view(), name="record_delete"),
)