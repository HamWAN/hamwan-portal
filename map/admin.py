from models import *
from django.contrib import admin


class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'site',
        'type',
        'survey_data',
        'public',
    )
    list_filter = (
        'site',
        'type',
    )
    search_fields = (
        'name',
        'site__name',
    )
admin.site.register(Client, ClientAdmin)


class LinkAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'site1',
        'site2',
    )
admin.site.register(Link, LinkAdmin)

class SiteAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'comment',
    )
admin.site.register(Site, SiteAdmin)
