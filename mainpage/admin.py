from django.contrib import admin
from . import models as mainpage_models
from django.db import models
from .widgets import TreeWidget
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import messages


# Register your models here.
class DomainAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'referer', 'url', 'added_time', 'is_link', 'link_time']


class UsersOfMenuAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'menu', 'date_joined']


class UsersOfMenuInline(admin.TabularInline):
    model = mainpage_models.UsersOfMenu
    extra = 1


class UserAdmin(UserAdmin):
    inlines = (UsersOfMenuInline,)


class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_menu', 'slug', 'link_app', 'link_app_view', 'link_address']
    inlines = (UsersOfMenuInline,)
    actions = ['up_menu', 'down_menu']
    list_per_page = 5

    def save_model(self, request, obj, form, change):
        """
        重构默认的保存函数
        :param request:
        :param obj:
        :param form:
        :param change:
        :return:
        """
        if change:
            # Update操作
            if 'parent_menu' in form.changed_data:
                obj.slug = mainpage_models.Menu.extra_objects.generate_menu_slug(obj)
                obj.update_child_menu_slug()
            if ('link_app' in form.changed_data) or ('link_app_view' in form.changed_data):
                obj.link_address = obj.generate_link_address()
        else:
            # Create操作
            obj.slug = mainpage_models.Menu.extra_objects.generate_menu_slug(obj)
            if obj.link_app and obj.link_app_view:
                obj.link_address = obj.generate_link_address()
            else:
                obj.link_address = None
        super().save_model(request, obj, form, change)

    def up_menu(self, request, queryset):
        """
        上移菜单
        :param request:
        :param queryset:
        :return:
        """
        if queryset.count() > 1:
            self.message_user(request,"一次只允许处理一个菜单", level=messages.WARNING)
        else:
            m = queryset.first()
            m.slug = m.slug[:-3] + str(int(m.slug[-3:]) - 1).zfill(3)
            m.save()
            m.update_child_menu_slug()
            self.message_user(request, "%s 上移成功！" % str(m))
    up_menu.short_description = "上移菜单"

    def down_menu(self, request, queryset):
        """
        下移菜单
        :param request:
        :param queryset:
        :return:
        """
        if queryset.count() > 1:
            self.message_user(request,  "一次只允许处理一个菜单", level=messages.WARNING)
        else:
            m = queryset.first()
            m.slug = m.slug[:-3] + str(int(m.slug[-3:]) + 1).zfill(3)
            m.save()
            m.update_child_menu_slug()
            self.message_user(request, "%s 下移成功！" % str(m))
    down_menu.short_description = "下移菜单"

    formfield_overrides = {
        models.ForeignKey: {
            'widget': TreeWidget
        }
    }


admin.site.register(mainpage_models.Domain, DomainAdmin)
admin.site.register(mainpage_models.Menu, MenuAdmin)
admin.site.register(mainpage_models.UsersOfMenu, UsersOfMenuAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)