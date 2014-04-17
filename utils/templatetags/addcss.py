from django import template


register = template.Library()


@register.filter(name='addcss')
def addcss(field, css):
    try:
        return field.as_widget(attrs={"class":css})
    except:
        return field
