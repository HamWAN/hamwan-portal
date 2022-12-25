from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from django.contrib.flatpages import views as flatpages_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('portal.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^api/', include('api.urls')),
    url(r'^dns/', include('dns.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/profile/$', 'portal.views.user_detail'),
    url(r'^password/change/$',
        auth_views.password_change, name='password_change'),
    url(r'^password/change/done/$',
        auth_views.password_change_done, name='password_change_done'),
    url(r'^password/reset/$',
        auth_views.password_reset, name='password_reset'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done, name='password_reset_done'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^(?P<url>.*/)$', flatpages_views.flatpage),
)
