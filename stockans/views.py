from django.shortcuts import render
from . import models as stockans_models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from . import forms as stockans_forms
from django.contrib.admin.views.main import ChangeList
from .admin import StockProfileAdmin
from home.admin import HomeAdminSite


# Create your views here.
def profile_list(request):
    """
    概要信息列表
    :param request:
    :return:
    """

    num_per_page = 20
    qs = stockans_models.StockProfile.objects.all().values()

    paginator = Paginator(qs, num_per_page)
    page = request.GET.get('page')
    try:
        qs_list = paginator.page(page)
    except PageNotAnInteger:
        qs_list = paginator.page(1)
    except EmptyPage:
        qs_list = paginator.page(paginator.num_pages)

    verbose_names = []
    for field in qs.model._meta.fields:
        verbose_names.append(field.verbose_name)

    search_form = stockans_forms.ProfileSearchForm()
    action_form = stockans_forms.ProfileActionForm()

    return render(request, 'stockans/profile_list.html', {'search_form': search_form, 'action_form': action_form,
                                                          'verbose_names': verbose_names, 'qs': qs_list})