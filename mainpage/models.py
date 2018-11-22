from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.contrib.auth.models import User
from library.stockdataspider import DomainLinkTest
from django.urls.exceptions import NoReverseMatch


# Create your models here.
class ExtraDomainManager(models.Manager):
    def get_stock_profile_spider_url(self, name):
        """
        获取站点信息结构
        :param name:
        :return:
        """
        domain = self.get(name=name)
        spider_url = {'host': domain.host, 'referer': domain.referer, 'url': domain.url}
        return spider_url


class Domain(models.Model):
    """
    域名信息
    """
    class Meta:
        verbose_name = _('域名信息')
        verbose_name_plural = _("域名信息")

    name = models.CharField(unique=True, max_length=100, verbose_name=_('名称'))
    host = models.CharField(null=True, blank=True, max_length=100, verbose_name=_('域名'))
    referer = models.CharField(null=True, blank=True, max_length=100, verbose_name=_('Referer'))
    url = models.CharField(unique=True, max_length=100, verbose_name=_('地址'))
    added_time = models.DateTimeField(auto_now_add=True, verbose_name=_('添加时间'))
    is_link = models.BooleanField(null=True, blank=True, verbose_name=_('可连接性'))
    link_time = models.DateTimeField(auto_now=True, verbose_name=_('连接时间'))

    def __str__(self):
        return self.name

    def update_link_state(self):
        """
        更新站点的连接状态
        :return:
        """
        host = self.host
        referer = self.referer
        url = self.url
        domain = {'host': host, 'referer': referer, 'url': url}
        link_state = DomainLinkTest.is_link(domain)
        self.is_link = link_state
        try:
            self.save()
            return True
        except ValueError:
            return False

    objects = models.Manager()
    extra_objects = ExtraDomainManager()


def create_menu_node(id, name, slug, child_menus, link_address=None, ispermitted=False):
    """
    创建菜单节点
    :param id:
    :param name:
    :param slug:
    :param link_address:
    :param child_menus:
    :return:
    """
    return {
        'id': id,
        'name': name,
        'slug': slug,
        'link_address': link_address,
        'child_menus': child_menus,
        'ispermitted': ispermitted
    }


class ExtraMenuManager(models.Manager):

    def get_menu_tree_by_root(self, parent_menu, user=None):
        """
        生成一个根菜单的树
        :param parent_menu:
        :return:
        """
        child_menus = parent_menu.menu_set.all().order_by('slug')
        menu_tree_by_root = []
        for child_menu in child_menus:
            if child_menu.has_child_menu():
                if child_menu.is_belong_to_user(user):
                    menu_node = create_menu_node(
                        id=child_menu.id,
                        name=child_menu.name,
                        slug=child_menu.slug,
                        child_menus=self.get_menu_tree_by_root(child_menu, user=user),
                        link_address=child_menu.link_address,
                        ispermitted=True,
                    )
                else:
                    menu_node = create_menu_node(
                        id=child_menu.id,
                        name=child_menu.name,
                        slug=child_menu.slug,
                        child_menus=self.get_menu_tree_by_root(child_menu, user=user),
                    )
            else:
                if child_menu.is_belong_to_user(user):
                    menu_node = create_menu_node(
                        id=child_menu.id,
                        name=child_menu.name,
                        slug=child_menu.slug,
                        child_menus=None,
                        link_address=child_menu.link_address,
                        ispermitted=True,
                    )
                else:
                    menu_node = create_menu_node(
                        id=child_menu.id,
                        name=child_menu.name,
                        slug=child_menu.slug,
                        child_menus=None,
                    )
            menu_tree_by_root.append(menu_node)
        return menu_tree_by_root

    def get_tree_menu(self, user=None):
        """
        生成菜单树
        :return:
        """
        root_menus = self.filter(parent_menu=None).order_by('slug')

        menu_tree = []
        for root_menu in root_menus:
            if root_menu.has_child_menu():  # 根菜单存在子菜单
                if root_menu.is_belong_to_user(user):  # 菜单被该用户定制
                    menu_node = create_menu_node(
                        id=root_menu.id,
                        name=root_menu.name,
                        slug=root_menu.slug,
                        child_menus=self.get_menu_tree_by_root(root_menu, user=user),
                        link_address=root_menu.link_address,
                        ispermitted=True,
                    )
                else:
                    menu_node = create_menu_node(
                        id=root_menu.id,
                        name=root_menu.name,
                        slug=root_menu.slug,
                        child_menus=self.get_menu_tree_by_root(root_menu, user=user),
                    )
            else:  # 根菜单不存在子菜单
                if root_menu.is_belong_to_user(user):
                    menu_node = create_menu_node(
                        id=root_menu.id,
                        name=root_menu.name,
                        slug=root_menu.slug,
                        child_menus=None,
                        link_address=root_menu.link_address,
                        ispermitted=True,
                    )
                else:
                    menu_node = create_menu_node(
                        id=root_menu.id,
                        name=root_menu.name,
                        slug=root_menu.slug,
                        child_menus=None,
                    )
            menu_tree.append(menu_node)
        return menu_tree

    def get_menu_choices_by_root(self, parent_menu):
        """
        生成一个根菜单的choices
        :param parent_menu:
        :return:
        """
        child_menus = parent_menu.menu_set.all().order_by('slug')
        menu_choices_by_root = []
        for child_menu in child_menus:
            menu_choices_by_root.append(
                ((child_menu.id),
                 (child_menu.name),
                 (child_menu.get_menu_step()))
            )
            if child_menu.has_child_menu():
                menu_choices_by_root.extend(self.get_menu_choices_by_root(child_menu))
        return menu_choices_by_root

    def get_tree_choices(self):
        """
        生成菜单树的choices
        :return:
        """
        root_menus = self.filter(parent_menu=None).order_by('slug')

        menu_choices = [('', '---------', 0)]
        for root_menu in root_menus:
            menu_choices.append(
                ((root_menu.id),
                 (root_menu.name),
                 (root_menu.get_menu_step()))
            )
            if root_menu.has_child_menu():
                menu_choices.extend(self.get_menu_choices_by_root(root_menu))
        return menu_choices

    def generate_menu_slug(self, obj):
        """
        生成指定菜单的slug
        :param obj:
        :return:
        """
        if obj.parent_menu is None:
            if not self.all().exists():
                return '001'
            else:
                pattern_str = '[0-9]{3}'
                max_slug = self.filter(parent_menu__exact=None).filter(slug__regex=pattern_str).latest('slug').slug
                return str(int(max_slug) + 1).zfill(3)
        else:
            if not obj.parent_menu.menu_set.all().exists():
                return obj.parent_menu.slug + '001'
            else:
                pattern_str = '[0-9]{3}' * (obj.parent_menu.get_menu_step() + 1)
                max_slug = obj.parent_menu.menu_set.filter(slug__regex=pattern_str).latest('slug').slug
                end_slug = max_slug[-3:]
                end_slug = str(int(end_slug) + 1).zfill(3)
                return obj.parent_menu.slug + end_slug


def menu_slug_validator(value):
    if not value.isdigit():
        raise ValidationError(
            _('必须由数字字符组成！')
        )
    if len(value) % 3 != 0:
        raise ValidationError(
            _('必须成三位倍数组成！')
        )


class Menu(models.Model):
    """
    菜单信息
    """
    class Meta:
        verbose_name = _('菜单信息')
        verbose_name_plural = _('菜单信息')

    parent_menu = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name=_('父菜单'))
    name = models.CharField(max_length=200, verbose_name=_('名称'))
    slug = models.SlugField(null=True, blank=True, editable=False, verbose_name=_('Slug'), validators=[menu_slug_validator])
    link_app = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('被链接应用'))
    link_app_view = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('被链接应用视图'))
    link_address = models.CharField(max_length=200, null=True, blank=True, editable=False, verbose_name=_('被链接地址'))
    users = models.ManyToManyField(User, blank=True, through='UsersOfMenu', verbose_name=_('定制用户'))

    objects = models.Manager()
    extra_objects = ExtraMenuManager()

    def __str__(self):
        return self.name

    def generate_link_address(self):
        """
        生成链接地址字符串
        :return:
        """
        if (self.link_app is None) or (self.link_app_view is None):
            return None
        else:
            try:
                return reverse(self.link_app + ":" + self.link_app_view)
            except NoReverseMatch:
                return None

    def get_link_address(self):
        """
        返回链接地址
        :return:
        """
        if not self.link_address:
            return self.link_address
        else:
            return '#'

    def get_menu_step(self):
        """
        获取菜单的层级
        :return:
        """
        step = 0
        parent_menu = self.parent_menu
        while parent_menu is not None:
            step += 1
            parent_menu = parent_menu.parent_menu
        return step

    def has_child_menu(self):
        """
        判断是否有子目录
        :param menu:
        :return:
        """
        return self.menu_set.all().exists()

    def is_belong_to_user(self, user):
        """
        判断一个菜单是否被用户使用
        :param user:
        :return:
        """
        if user is None:
            return False
        else:
            return self.usersofmenu_set.filter(user=user).exists()

    def update_child_menu_slug(self):
        """
        更新所有子菜单的slug
        """
        child_menus = self.menu_set.all()
        if child_menus.exists():
            for child_menu in child_menus:
                new_slug = self.slug + child_menu.slug[-3:]
                child_menu.slug = new_slug
                child_menu.save()
                child_menu.update_child_menu_slug()


class UsersOfMenu(models.Model):
    """
    用户和菜单的关系
    """
    class Meta:
        verbose_name = _('菜单-用户')
        verbose_name_plural = _('菜单-用户')

    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, verbose_name=_('菜单'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('用户'))
    date_joined = models.DateField(auto_now_add=True, verbose_name=_('添加时间'))

    def __str__(self):
        return str(self.user) + '-' + str(self.menu)