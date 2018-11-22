from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import types

register = template.Library()


@register.filter(is_safe=True, needs_autoescape=True)
def stockans_unordered_list(value, autoescape=True):
    """
    Recursively take a self-nested list and return an HTML unordered list --
    WITHOUT opening and closing <ul> tags.

    Assume the list is in the proper format. For example, if ``var`` contains:
    ``['States', ['Kansas', ['Lawrence', 'Topeka'], 'Illinois']]``, then
    ``{{ var|unordered_list }}`` returns::

        <li>States
        <ul>
                <li>Kansas
                <ul>
                        <li>Lawrence</li>
                        <li>Topeka</li>
                </ul>
                </li>
                <li>Illinois</li>
        </ul>
        </li>
    """
    if autoescape:
        escaper = conditional_escape
    else:
        def escaper(x):
            return x

    def walk_items(item_list):
        item_iterator = iter(item_list)
        try:
            item = next(item_iterator)
            while True:
                try:
                    if item['child_menus'] is not None:
                        next_item = item['child_menus']
                    else:
                        next_item = next(item_iterator)
                except StopIteration:
                    yield item, None
                    break
                if isinstance(next_item, (list, tuple, types.GeneratorType)):
                    try:
                        iter(next_item)
                    except TypeError:
                        pass
                    else:
                        yield item, next_item
                        item = next(item_iterator)
                        continue
                yield item, None
                item = next_item
        except StopIteration:
            pass

    def list_formatter(item_list, tabs=1):
        indent = '\t' * tabs
        output = []
        for item, children in walk_items(item_list):
            sublist = ''
            if children:
                sublist = '\n%s<ul id="%s">\n%s\n%s</ul>\n%s' % (
                    indent, escaper(item['id']), list_formatter(children, tabs + 1), indent, indent)
            output.append('%s<li><span class="btn" href="%s"><i></i>%s</span>%s</li>' % (
                indent, escaper(item['link_address']), escaper(item['name']), sublist))
        return '\n'.join(output)

    return mark_safe(list_formatter(value))

