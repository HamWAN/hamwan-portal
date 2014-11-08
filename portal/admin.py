from models import *
from forms import IPAddressFormset
from django.contrib import admin


class IPAddressAdmin(admin.ModelAdmin):
    list_display = (
        'host',
        'ip',
        'fqdn',
        'auto_dns',
    )
    search_fields = ('ip', )
admin.site.register(IPAddress, IPAddressAdmin)


class IPAddressInline(admin.TabularInline):
    model = IPAddress
    formset = IPAddressFormset
    extra = 1


admin.site.register(Site)


class HostAdmin(admin.ModelAdmin):
    list_display = (
        'site',
        '__unicode__',
        'owner',
        'get_ips'
    )
    list_display_links = '__unicode__',
    list_filter = ('owner', 'site')
    search_fields = ('name', 'site__name')
    save_as = True
    save_on_top = True
    inlines = [IPAddressInline]

    def get_ips(self, obj):
        return "\n".join([str(a.ip) for a in obj.ipaddresses.all()])
    get_ips.short_description = "IP Addresses"
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
