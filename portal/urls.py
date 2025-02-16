from django.urls import include, re_path

from portal.views import index, own_hosts, all_hosts, ansible_hosts, host_detail, HostDelete
from portal.views import smokeping, own_subnets, all_subnets, subnet_detail, SubnetDelete


urlpatterns = [
    re_path(r'^$', index, name='index'),
    re_path(r'^host/$', own_hosts, name='own_hosts'),
    re_path(r'^host/all$', all_hosts, name='all_hosts'),
    re_path(r'^host/ansible.json$', ansible_hosts, name='ansible_hosts'),
    re_path(r'^host/new$', host_detail, name='host_detail'),
    re_path(r'^host/(?P<name>[a-zA-Z0-9-\.]+)/$', host_detail, name='host_detail'),
    re_path(r'^host/(?P<slug>[a-zA-Z0-9-\.]+)/delete/$', HostDelete.as_view(),
        name="host_delete"),
    re_path(r'^smokeping/$', smokeping, name='smokeping'),
    re_path(r'^subnet/$', own_subnets, name='own_subnets'),
    re_path(r'^subnet/all/visual$', all_subnets,
        {'template': 'portal/subnet_diagram.html'}, name='subnet_diagram'),
    re_path(r'^subnet/all$', all_subnets, name='all_subnets'),
    re_path(r'^subnet/new$', subnet_detail, name='subnet_detail'),
    re_path(r'^subnet/(?P<network>[0-9/\.:]+)/$', subnet_detail, name='subnet_detail'),
    re_path(r'^subnet/(?P<slug>[0-9/\.]+)/delete/$',
        SubnetDelete.as_view(), name="subnet_delete"),
]
