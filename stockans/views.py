from django.shortcuts import render
from . import models as stockans_models
from mainpage.models import Domain
from library.stockans_extra import ChangeList_StockAns
from library.stockdataspider import GetStockProfile
from django.http import HttpResponseRedirect, JsonResponse
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from .cron import get_stock_attentioned_price_online, pull_price_online

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'default')


@register_job(scheduler, 'interval', seconds=20)
def get_price_online():
    get_stock_attentioned_price_online()

register_events(scheduler)
scheduler.start()


# Create your views here.
def update_stockprofile(request):
    """
    更新概要信息分配
    :param request:
    :return:
    """
    ss_domain = Domain.extra_objects.get_stock_profile_spider_url("上交所")
    sz_domain = Domain.extra_objects.get_stock_profile_spider_url("深交所")
    if request.method == "POST":
        action_type = request.POST['action']
        if action_type is not None and action_type != "":
            g = GetStockProfile(ss_domain=ss_domain, sz_domain=sz_domain)
            if action_type == "update_all":
                data_list = g.get_all_stock_profile()
            if action_type == "update_ss":
                data_list = g.get_ss_stock_profile()
            if action_type == "update_sz":
                data_list = g.get_sz_stock_profile()
            update_num = stockans_models.StockProfile.extra_objects.update_by_bulk(data_list)
        else:
            update_num = 0

    return JsonResponse({'update_num': update_num})


def profile_list(request):
    """
    概要信息列表
    :param request:
    :return:
    """

    model = stockans_models.StockProfile
    cl = ChangeList_StockAns(request, model)

    return render(request, 'stockans/profile_list.html', {'cl': cl})


def price_online(request):
    """
    实时价格信息
    :param request:
    :return:
    """
    stock_queryset = stockans_models.AttentionedStock.extra_objects.get_attentioned_stock_by_user(request)
    return render(request, 'stockans/price_online.html', {'stock_queryset': stock_queryset})


def update_price_online_data(request):
    """
    实时更新价格信息
    :param request:
    :return:
    """
    stock_queryset = stockans_models.AttentionedStock.extra_objects.get_attentioned_stock_by_user(request)
    price_data = pull_price_online(stock_queryset)
    return JsonResponse(price_data, safe=False)