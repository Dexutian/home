from django import template

register = template.Library()


@register.inclusion_tag('stockans/result_list.html')
def result_list_tag(cl):
    return {
        'headers': cl.headers,
        'results': cl.results,
        'previous_page_link': cl.previous_page_link,
        'next_page_link': cl.next_page_link,
    }