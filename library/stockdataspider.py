import urllib3, xlrd, logging, re, time, datetime
import numpy as np
from urllib3.exceptions import MaxRetryError
import os
from django.conf import settings

# 生成logger
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(os.path.join(settings.MEDIA_ROOT, 'log', 'stockdataspider.log'))
# handler = logging.FileHandler('getstockprofile.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def sz_stock_proflie_clean(pre_clean_data):
    """
    深交所股票信息数据清洗
    :param pre_clean_data:
    :return:
    """
    n_item = 20  # 原始数据项数
    select_col = [0, 1, 2, 3, 7, 8, 9, 10, 11, 20]  # 选择数据项
    nrows = pre_clean_data.nrows
    ncols = pre_clean_data.ncols
    pre_data = []
    for nrow in range(nrows):
        for ncol in range(ncols):
            pre_data.append(pre_clean_data.cell(nrow, ncol).value)
    pre_clean_data = pre_data

    re_html = re.compile(r'<[^>]+>', re.S)
    pre_clean_data = pre_clean_data[n_item:]
    pre_clean_data = [re_html.sub('', data.replace(',', '')) for data in pre_clean_data]
    if len(pre_clean_data) % n_item == 0:
        n_row = int(len(pre_clean_data) / n_item)
        n_col = int(n_item)
        after_clean_data = np.array(pre_clean_data).reshape(n_row, n_col)
        after_clean_data = np.insert(after_clean_data, 2, 'sz', axis=1)
        after_clean_data = np.insert(after_clean_data, 3, 'A', axis=1)
        after_clean_data = after_clean_data[:, select_col]
        after_clean_data[:, 7:9] = after_clean_data[:, 7:9].astype('int64')
        return after_clean_data
    else:
        logger.info('深交所股票概要信息清洗错误')
        return []


def ss_stock_proflie_clean(pre_clean_data):
    """
    上交所股票概要信息数据清洗
    :return:
    """
    n_item = 7  # 原始数据项数
    if isinstance(pre_clean_data, str):
        pre_clean_data = pre_clean_data.split('\t')[n_item:]
        pre_clean_data = [data.rstrip(', ').lstrip(' ').lstrip('\n') for data in pre_clean_data]
        pre_clean_data = pre_clean_data[:len(pre_clean_data) - 1]
        if len(pre_clean_data) % n_item == 0:
            n_row = int(len(pre_clean_data) / n_item)
            n_col = int(n_item)
            after_clean_data = np.array(pre_clean_data).reshape(n_row, n_col)
            after_clean_data[:, 5:7] = (after_clean_data[:, 5:7].astype('float64') * 10000).astype('int64')
            after_clean_data = np.insert(after_clean_data, 2, 'sh', axis=1)
            after_clean_data = np.insert(after_clean_data, 3, 'A', axis=1)
            after_clean_data = np.insert(after_clean_data, 9, '', axis=1)
            for i in range(n_row):
                try:
                    datetime.datetime.strptime(after_clean_data[i, 6], '%Y-%m-%d')
                except:
                    after_clean_data[i, 6] = '1900-01-01'
            return after_clean_data
        else:
            logger.info('上交所股票概要信息清洗错误')
            return []
    else:
        logger.info('上交所股票概要信息清洗前数据类型错误')
        return []


class GetStockProfile:
    """
    获取所有A股的股票的概要信息
    """
    def __init__(self, ss_domain, sz_domain):
        """
        初始化函数
        """
        self.http = urllib3.PoolManager(num_pools=10)
        self.ss_host = ss_domain['host']
        self.ss_referer = ss_domain['referer']
        self.ss_url = ss_domain['url']
        self.sz_host = sz_domain['host']
        self.sz_referer = sz_domain['referer']
        self.sz_url = sz_domain['url']

    def get_res(self, host, referer, url):
        """
        获得response
        :return:
        """
        send_headers = {
            'Host': host,
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': referer,
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        try:
            res = self.http.request(
                'GET',
                url=url,
                headers=send_headers,
                preload_content=False
            )
            return res
        except MaxRetryError:
            return None

    def get_ss_stock_profile(self):
        """
        获取上交所的股票概要信息
        :return:
        """
        res = self.get_res(self.ss_host, self.ss_referer, self.ss_url)
        if (res is not None) and (res.status == 200):
            decode_content = res.getheader('Content-Type').split('=')[1]
            data_str = res.data.decode(decode_content)
            data = ss_stock_proflie_clean(data_str)
            return data
        else:
            logger.info('上交所链接异常')
            return None

    def get_sz_stock_profile(self):
        """
        获取深交所的股票概要信息
        :return:
        """
        res = self.get_res(self.sz_host, self.sz_referer, self.sz_url)
        if (res is not None) and (res.status == 200):
            workbook = xlrd.open_workbook(file_contents=res.data)
            sheet = workbook.sheet_by_index(0)
            data = sz_stock_proflie_clean(sheet)
            return data
        else:
            logger.info('深交所连接异常')
            return None

    def get_all_stock_profile(self):
        """
        获取所有A股的股票的概要信息
        :return:
        """
        ss_stock_profile = self.get_ss_stock_profile()
        sz_stock_profile = self.get_sz_stock_profile()
        if (ss_stock_profile is not None) and (sz_stock_profile is not None):
            stock_profile = np.r_[ss_stock_profile, sz_stock_profile]
        if (ss_stock_profile is None) and (sz_stock_profile is not None):
            stock_profile = sz_stock_profile
        if (ss_stock_profile is not None) and (sz_stock_profile is None):
            stock_profile = ss_stock_profile
        if (ss_stock_profile is None) and (sz_stock_profile is None):
            stock_profile = None
        return stock_profile

    def save_all_to_txt(self, path):
        """
        将所有的A股的股票的概要信息存储为文本文件
        :param path:
        :return:
        """
        data = self.get_all_stock_profile()
        np.savetxt(path, data, fmt='%s,'*data.shape[1], delimiter='\n')

    def get_stock_profile_by_code(self, code):
        """
        通过股票代码获取股票的概要信息
        :param code:
        :return:
        """
        data = self.get_all_stock_profile()
        if data is not None:
            for row in data:
                if row[0] == code:
                    return row
            return None
        else:
            return None


class DomainLinkTest:
    """
    站点连接测试
    """
    http = urllib3.PoolManager(num_pools=10)

    @classmethod
    def is_link(cls, domain):
        """
        是否可以连接站点
        :param domain:
        :return:
        """
        host = domain['host']
        referer = domain['referer']
        url = domain['url']
        try:
            res = cls.http.request(
                'GET',
                url=referer,
            )
            if res.status == 200:
                return True
        except MaxRetryError:
            return False
        return False


if __name__ == "__main__":
    start_time = time.time()
    ss_host = 'query.sse.com.cn'
    ss_referer = 'http://www.sse.com.cn/assortment/stock/list/share/'
    ss_url = 'http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1'
    ss_domain = {'host': ss_host, 'referer': ss_referer, 'url': ss_url}
    sz_host = 'www.szse.cn'
    sz_referer = 'http://www.szse.cn/market/stock/list/index.html'
    sz_url = 'http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1&random=0.4261879772679307'
    sz_domain = {'host': sz_host, 'referer': sz_referer, 'url': sz_url}
    # print(DomainLinkTest.is_link(ss_domain))
    g = GetStockProfile(ss_domain, sz_domain)
    data = g.get_ss_stock_profile()
    # g.save_all_to_txt('a.txt')
    # print([data])
    end_time = time.time()
    print('Time costs: %s' % str(end_time - start_time))



