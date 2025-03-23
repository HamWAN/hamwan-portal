from django import template
from django.urls import reverse


register = template.Library()


@register.inclusion_tag('portal/hosttable.html', takes_context=True)
def hosttable(context, hosts, **kwargs):
    kwargs['hosts'] = hosts
    return kwargs


@register.inclusion_tag('portal/subnettable.html', takes_context=True)
def subnettable(context, subnets, **kwargs):
    kwargs['subnets'] = subnets
    return kwargs
