from django.urls import path
from . import views as stockans_views

# mainpage urlpatterns
app_name = 'stockans'
urlpatterns = [
    path('profile_list/', stockans_views.profile_list, name='profile_list'),
    path('update_stockprofile/', stockans_views.update_stockprofile, name='update_stockprofile'),
    path('price_online/', stockans_views.price_online, name='price_online'),
    path('update_price_online_data/', stockans_views.update_price_online_data, name='update_price_online_data'),
]