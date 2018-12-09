from django.test import TestCase
from django.test import Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
import os


# Create your tests here.
class ProfileTestCase(TestCase):
    """
    概要信息页测试
    """
    def setUp(self):
        pass

    def test_index(self):
        """
        测试首页
        :return:
        """
        c = Client()
        res = c.get('/stockans/profile_list/')
        self.assertEqual(res.status_code, 200)


class MySeleniumTests(StaticLiveServerTestCase):
    fixtures = ['auth.json', 'contenttypes.json', 'mainpage.json', 'stockans.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        base_path = os.path.dirname(os.path.dirname(__file__))
        executable_path = os.path.join(base_path, 'webdriver/chromedriver.exe')
        cls.selenium = webdriver.Chrome(executable_path=executable_path)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('admin')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('admin')
        self.selenium.find_element_by_class_name("btn").click()