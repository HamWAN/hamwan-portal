from django.urls import re_path

from dns import views


urlpatterns = [
    re_path(r'^$', views.own_dns, name='own_dns'),
    re_path(r'^all/$', views.RecordListView.as_view(), name='record_list'),
    re_path(r'^new/$', views.RecordCreate.as_view(), name="record_create"),
    re_path(r'^(?P<pk>\d+)/$', views.RecordUpdate.as_view(), name="record_update"),
    re_path(r'^(?P<pk>\d+)/delete/$', views.RecordDelete.as_view(), name="record_delete"),
]
