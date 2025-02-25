from portal.models import *
from django.contrib import admin


class RecordAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'type',
        'content',
        'ttl',
    )
    list_filter = ('domain', 'type')
    search_fields = ('name', 'content')
    save_as = True
admin.site.register(Record, RecordAdmin)

admin.site.register(Domain)
