from django.shortcuts import render
from . import models as mainpage_models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    """
    网站首页
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        menus = mainpage_models.Menu.extra_objects.get_tree_menu(request.user)
    else:
        menus = mainpage_models.Menu.extra_objects.get_tree_menu()
    return render(request, 'mainpage/index.html', {'menus': menus})


def domain_list(request):
    """
    站点可连接性检查页面
    :param request:
    :return:
    """
    domains = mainpage_models.Domain.objects.all()
    return render(request, 'mainpage/domain_list.html', {'domains': domains})


@csrf_exempt
def link_check(request):
    """
    站点连接性检查
    :param request:
    :param id:
    :return:
    """
    if request.method == "POST":
        id = request.POST["id"]
    check_state = mainpage_models.Domain.objects.get(id=id).update_link_state()
    return JsonResponse({"checked": check_state})