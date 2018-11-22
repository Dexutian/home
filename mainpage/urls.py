from django.urls import path
from . import views as mainpage_views

# mainpage urlpatterns
app_name = 'mainpage'
urlpatterns = [
    path('index/', mainpage_views.index, name='index'),
    path('domain_list/', mainpage_views.domain_list, name='domain_list'),
    path('link_check/', mainpage_views.link_check, name='link_check'),
]