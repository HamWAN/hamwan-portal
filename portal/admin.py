from django.contrib import admin
from django.utils.html import format_html
from portal.models import *
from .forms import IPAddressFormset


class IPAddressAdmin(admin.ModelAdmin):
    list_display = (
        'host',
        'ip',
        'fqdn',
        'auto_dns',
    )
    search_fields = ('ip', 'host__name', 'host__site__name')
admin.site.register(IPAddress, IPAddressAdmin)


class IPAddressInline(admin.TabularInline):
    model = IPAddress
    formset = IPAddressFormset
    extra = 1


admin.site.register(Site)


class HostAdmin(admin.ModelAdmin):
    list_display = (
        'site',
        '__str__',
        'owner',
        'type',
        'os',
        'get_ips'
    )
    list_display_links = '__str__',
    list_filter = ('owner', 'site', 'type', 'os')
    search_fields = ('name', 'ipaddresses__ip', 'owner__username')
    save_as = True
    save_on_top = True
    inlines = [IPAddressInline]

    def get_ips(self, obj):
        return format_html("<br>".join(str(a.ip) for a in obj.ipaddresses.all()))
    get_ips.short_description = "IP Addresses"
    get_ips.allow_tags = True
admin.site.register(Host, HostAdmin)


class SubnetAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        '__str__',
        'min',
        'max',
        'numhosts',
        'notes_short',
    )
    list_display_links = '__str__',
    list_filter = ('owner', )
    readonly_fields = ('hosts', )
    search_fields = ('notes', )
admin.site.register(Subnet, SubnetAdmin)
