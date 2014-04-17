from models import *
from django.contrib import admin


class HostAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__',
        'owner',
        'eth_ipv4',
        'wlan_ipv4',
    )
    list_filter = ('owner',)
    search_fields = ('name', 'eth_ipv4', 'wlan_ipv4')
    save_as = True
admin.site.register(Host, HostAdmin)

class SubnetAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        '__unicode__',
        'min',
        'max',
        'numhosts',
        'notes_short',
    )
    list_display_links = '__unicode__',
admin.site.register(Subnet, SubnetAdmin)
