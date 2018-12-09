from django.test import TestCase, Client
from .models import Domain, Menu, UsersOfMenu
from django.contrib.auth.models import User

# Create your tests here.
class DomainTestCase(TestCase):
    """
    站点模型测试
    """
    def setUp(self):
        ss_host = 'query.sse.com.cn'
        ss_referer = 'http://www.sse.com.cn/assortment/stock/list/share/'
        ss_url = 'http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1'
        Domain.objects.create(
            name='上交所',
            host=ss_host,
            referer=ss_referer,
            url=ss_url,
        )
        sz_host = 'www.szse.cn'
        sz_referer = 'http://www.szse.cn/market/stock/list/index.html'
        sz_url = 'http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1&random=0.4261879772679307'
        Domain.objects.create(
            name='深交所',
            host=sz_host,
            referer=sz_referer,
            url=sz_url,
        )

    def test_is_exists_ss(self):
        """
        测试站点是否存在
        :return:
        """
        ss_domain = Domain.objects.get(name='上交所')
        sz_domain = Domain.objects.get(name='深交所')
        self.assertIsInstance(ss_domain, Domain)
        self.assertIsInstance(sz_domain, Domain)

    def test_model_link_func(self):
        """
        测试连接函数
        :return:
        """
        ss_domain = Domain.objects.get(name='上交所')
        sz_domain = Domain.objects.get(name='深交所')
        ss_link_state = ss_domain.update_link_state()
        sz_link_state = sz_domain.update_link_state()
        self.assertEqual(ss_link_state, True)
        self.assertEqual(sz_link_state, True)

    def test_get_domain_dict(self):
        """
        测试获得站点字典
        :return:
        """
        ss_host = 'query.sse.com.cn'
        ss_referer = 'http://www.sse.com.cn/assortment/stock/list/share/'
        ss_url = 'http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1'
        origin_ss_domain = {'host': ss_host, 'referer': ss_referer, 'url': ss_url}
        ss_domain = Domain.extra_objects.get_stock_profile_spider_url('上交所')
        self.assertDictEqual(ss_domain, origin_ss_domain)


class LoginTestCase(TestCase):
    """
    用户系统测试
    """
    def setUp(self):
        user = User.objects.create_user('testUser', 'testUser@django.com', 'testUser')
        menu = Menu.objects.create(name='菜单1', slug='001')
        UsersOfMenu.objects.create(user=user, menu=menu)

    def test_index_view(self):
        """
        测试登录视图
        :return:
        """
        c = Client()
        response = c.login(username='testUser', password='testUser')
        self.assertEqual(response, True)

    def test_index_menu(self):
        """
        测试生成的菜单
        :return:
        """
        c = Client()
        c.login(username='testUser', password='testUser')
        res = c.get('')
        self.assertIsInstance(res.context['menus'], list)
        print(res.context['menus'])