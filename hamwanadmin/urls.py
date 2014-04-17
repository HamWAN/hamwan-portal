from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('portal.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/profile/$', 'portal.views.user_detail'),
    url(r'^accounts/password/change/$',
        'django.contrib.auth.views.password_change'),
    url(r'^accounts/password/change/done/$',
        'django.contrib.auth.views.password_change_done'),
    url(r'^accounts/password/reset/$',
        'django.contrib.auth.views.password_reset'),
    url(r'^accounts/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    url(r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm'),
    url(r'^accounts/password/done/$',
        'django.contrib.auth.views.password_reset_complete'),
)
