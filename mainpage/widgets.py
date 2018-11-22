from django.forms import widgets
from .models import Menu as m


class TreeWidget(widgets.Select):
    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        groups = []
        has_selected = False

        self.choices = m.extra_objects.get_tree_choices()
        for index, (option_value, option_label, option_step) in enumerate(self.choices):
            if option_value is None:
                option_value = ''

            subgroup = []
            if isinstance(option_label, (list, tuple)):
                group_name = option_value
                subindex = 0
                choices = option_label
            else:
                group_name = None
                subindex = None
                choices = [(option_value, option_label)]
            groups.append((group_name, subgroup, index))

            for subvalue, sublabel in choices:
                selected = (
                        str(subvalue) in value and
                        (not has_selected or self.allow_multiple_selected)
                )
                has_selected |= selected
                sublabel = '---' * option_step + sublabel
                subgroup.append(self.create_option(
                    name, subvalue, sublabel, selected, index,
                    subindex=subindex, attrs=attrs,
                ))
                if subindex is not None:
                    subindex += 1
        return groups