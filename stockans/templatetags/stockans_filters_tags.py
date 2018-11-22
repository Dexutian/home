from django import template

register = template.Library()


@register.inclusion_tag('stockans/result_list.html', takes_context=True)
def stockans_result_list(context):
    return {
        'verbose_names': context['verbose_names'],
        'qs': context['qs'],
    }