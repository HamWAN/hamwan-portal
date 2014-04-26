from models import *
from django.contrib import admin


def send_to_ampr(modeladmin, request, queryset):
    for record in queryset:
        record._save_ampr_dns_command()
send_to_ampr.short_description = "Re-send selected records to AMPR"


class RecordAdmin(admin.ModelAdmin):
    actions = [send_to_ampr]
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
