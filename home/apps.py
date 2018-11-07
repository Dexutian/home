from django.contrib.admin.apps import AdminConfig


class HomeAdminConfig(AdminConfig):
    default_site = 'home.admin.HomeAdminSite'
