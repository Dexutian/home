from django.contrib import admin


class HomeAdminSite(admin.AdminSite):
    site_header = 'StockAns-后台管理系统'
    site_title = 'StockAns'
