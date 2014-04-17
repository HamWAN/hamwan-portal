from models import *
from django.contrib import admin


admin.site.register(Host)

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
