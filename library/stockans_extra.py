from django.utils.http import urlencode
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.admin.utils import lookup_field


SEARCH_VAR = 'q'
ORDER_VAR = 'o'
PAGE_VAR = 'p'
SEARCH_PAGE_VAR = 'sp'


class ChangeList_StockAns:
    def __init__(self, request, model):
        self.model = model
        self.list_display = self.model._meta.fields
        self.root_queryset = self.model.objects.all()
        self.num_per_page = 20

        self.params = dict(request.GET.items())
        if PAGE_VAR not in self.params:
            self.params[PAGE_VAR] = '1'

        self.queryset = self.get_queryset()  # 依赖params[q]
        self.order_queryset = self.get_order_queryset()  # 依赖params[o]
        self.headers = list(self.results_headers())
        self.results = self.get_results()
        self.previous_page_link = self.get_previous_page_link()
        self.next_page_link = self.get_next_page_link()

    def get_queryset(self):
        qs = self.root_queryset
        if SEARCH_VAR in self.params and self.params[SEARCH_VAR] is not None:
            new_qs = qs.filter(stock_code__icontains=self.params[SEARCH_VAR])
        else:
            new_qs = qs
        if new_qs is not None:
            qs = new_qs
        return qs

    def get_order_queryset(self):

        def make_qs_param(t):
            return '-' if t == 'desc' else ''
        qs = self.queryset
        ordering_field_columns = self.get_ordering_field_columns()
        if ordering_field_columns is not None:
            for i, field in enumerate(self.list_display):
                for p, v in ordering_field_columns.items():
                    if p == i+1:
                        order_type = v.lower()
                        new_qs = qs.order_by(make_qs_param(order_type) + str(field.name))
                        qs = new_qs
        return qs

    def get_query_string(self, new_params=None, remove=None):
        if new_params is None:
            new_params = {}
        if remove is None:
            remove = []
        p = self.params.copy()
        for r in remove:
            for k in list(p):
                if k.startswith(r):
                    del p[k]
        for k, v in new_params.items():
            if v is None:
                if k in p:
                    del p[k]
            else:
                p[k] = v
        return '?%s' % urlencode(sorted(p.items()))

    def get_ordering_field_columns(self):
        ordering_fields = {}
        if ORDER_VAR not in self.params:
            ordering_fields = None
        else:
            for p in self.params[ORDER_VAR].split('.'):
                none, pfx, idx = p.rpartition('-')
                try:
                    idx = int(idx)
                except ValueError:
                    continue  # skip it
                ordering_fields[idx] = 'desc' if pfx == '-' else 'asc'
        return ordering_fields

    def results_headers(self):
        ordering_field_columns = self.get_ordering_field_columns()
        if ordering_field_columns is None:
            for i, field in enumerate(self.list_display):
                new_order_type = 'asc'

                o_list_primary = []

                def make_qs_param(t, n):
                    return ('-' if t == 'desc' else '') + str(n)

                param = make_qs_param(new_order_type, i+1)
                o_list_primary.insert(0, param)

                yield {
                    "text": field.verbose_name,
                    "url_primary": self.get_query_string({ORDER_VAR: '.'.join(o_list_primary)}),
                }
        else:
            def make_qs_param(t, n):
                return ('-' if t == 'desc' else '') + str(n)

            for i, field in enumerate(self.list_display):
                o_list_primary = []
                for j, ot in ordering_field_columns.items():
                    order_type = ordering_field_columns.get(j).lower()
                    new_order_type = {'asc': 'desc', 'desc': 'asc'}[order_type]
                    if j-1 == i:
                        param = make_qs_param(new_order_type, j)
                        o_list_primary.insert(0, param)
                    else:
                        param = make_qs_param(ot, j)
                        o_list_primary.append(param)
                if i+1 not in ordering_field_columns:
                    o_list_primary.insert(0, make_qs_param('asc', i+1))

                yield {
                    "text": field.verbose_name,
                    "url_primary": self.get_query_string({ORDER_VAR: '.'.join(o_list_primary)}),
                }

    def get_results(self):
        paginator = Paginator(self.order_queryset, self.num_per_page)

        if SEARCH_PAGE_VAR in self.params and self.params[SEARCH_PAGE_VAR] is not None:
            try:
                page = int(self.params[SEARCH_PAGE_VAR])
            except:
                page = int(self.params[PAGE_VAR])
        else:
            page = int(self.params[PAGE_VAR])

        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        object_list = []
        for instance in results:
            list_one = []
            for field in self.model._meta.fields:
                f, attr, value = lookup_field(field.name, instance)
                list_one.append(value)
            object_list.append(list_one)

        results.object_list = object_list

        return results

    def get_previous_page_link(self):
        page_num = int(self.params[PAGE_VAR])
        previous_page_num = page_num - 1
        previous_page_link = self.get_query_string(new_params={PAGE_VAR: str(previous_page_num)}, remove={PAGE_VAR: self.params[PAGE_VAR]})
        return previous_page_link

    def get_next_page_link(self):
        page_num = int(self.params[PAGE_VAR])
        next_page_num = page_num + 1
        next_page_link = self.get_query_string(new_params={PAGE_VAR: str(next_page_num)}, remove={PAGE_VAR: self.params[PAGE_VAR]})
        return next_page_link