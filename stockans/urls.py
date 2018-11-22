from django.urls import path
from . import views as stockans_views

# mainpage urlpatterns
app_name = 'stockans'
urlpatterns = [
    path('profile_list/', stockans_views.profile_list, name='profile_list'),
]