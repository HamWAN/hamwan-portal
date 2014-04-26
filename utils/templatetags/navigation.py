from django import template
from django.core import urlresolvers


register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, url_name, return_value=' active', **kwargs):
    matches = active_url_equals(context, url_name, **kwargs)
    return return_value if matches else url_name


def active_url_equals(context, url_name, **kwargs):
    resolved = False
    try:
        resolved = urlresolvers.resolve(context.get('request').path)
    except:
        pass
    matches = resolved and resolved.url_name == url_name
    if matches and kwargs:
        for key in kwargs:
            kwarg = kwargs.get(key)
            resolved_kwarg = resolved.kwargs.get(key)
            if not resolved_kwarg or kwarg != resolved_kwarg:
                return False
    return matches


def easy_tag(func):
    """Decorator to facilitate template tag creation"""

    def inner(parser, token):
        """deal with the repetitive parts of parsing template tags"""
        try:
            return func(*token.split_contents())
        except TypeError:
            raise template.TemplateSyntaxError('Bad arguments for tag "%s"' % token.split_contents()[0])
    inner.__name__ = func.__name__
    inner.__doc__ = inner.__doc__
    return inner


class AppendGetNode(template.Node):
    def __init__(self, dict):
        self.dict_pairs = {}
        for pair in dict.split(','):
            pair = pair.split('=')
            self.dict_pairs[pair[0]] = template.Variable(pair[1])

    def render(self, context):
        get = context['request'].GET.copy()

        for key in self.dict_pairs:
            get[key] = self.dict_pairs[key].resolve(context)

        path = context['request'].META['PATH_INFO']

        if len(get):
            path += "?%s" % "&".join(["%s=%s" % (key, value) for (key, value) in get.items() if value])


        return path


@register.tag()
@easy_tag
def append_to_get(_tag_name, dict):
    return AppendGetNode(dict)
