import urllib3
from urllib3.exceptions import MaxRetryError
from .models import StockPriceOnLine, AttentionedStock
import json
from datetime import datetime, date, time
from concurrent.futures import ThreadPoolExecutor
import time as T


def clean_price_online(price_str):
    """
    清洗实时价格数据
    :param price_str: 
    :return: 
    """""
    price_data = price_str.split(',')[1:-1]
    chg_value = str((float(price_data[2]) - float(price_data[0])))
    chg_percent = str((float(price_data[2])-float(price_data[0]))/float(price_data[0]))
    price_data.append(chg_value)
    price_data.append(chg_percent)
    return price_data


def get_stock_attentioned_price_online():
    """
    更新关注的股票的实时价格
    http://hq.sinajs.cn/api/list=sh601006,sz002139
    :return:
    """
    http = urllib3.PoolManager(num_pools=20)
    send_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }

    base_url = 'http://hq.sinajs.cn/api/list='
    attentioned_stock_code_list = AttentionedStock.objects.order_by('stock__exchange_no', 'stock__stock_code'). \
        values_list('stock__exchange_no', 'stock__stock_code').distinct()

    def network_programming(stock):
        url = base_url + stock[0] + stock[1]
        try:
            res = http.request(
                'GET',
                url=url,
                headers=send_headers,
            )
            price_data = [stock[0], stock[1]] + clean_price_online(res.data.decode('gb2312'))
            return price_data
        except MaxRetryError:
            return None

    # 多线程
    def multithreading():
        stocks = attentioned_stock_code_list     # 关注的股票列表
        event = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            for result in executor.map(network_programming, stocks):
                event.append(result)
        return event

    event = multithreading()

    for price_data in event:
        StockPriceOnLine.extra_objects.create_obj_by_list(price_data)


class CJsonEncoder(json.JSONEncoder):
    """
    自定义时间json序列化格式
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


def pull_price_online(stock_queryset):
    """
    获取股票的实时价格
    :return:
    """
    price_online = []
    if stock_queryset:
        for stock in stock_queryset:
            price_online_per_stock = {}
            price_online_per_stock['code'] = stock['stock__stock_code']
            price_online_per_stock['abb'] = stock['stock__stock_abb']
            price = json.dumps(list(StockPriceOnLine.objects.
                                    filter(stock__stock_code=stock['stock__stock_code'], stock__stock_abb=stock['stock__stock_abb']).
                                    order_by('date', 'time').values_list('date', 'time', 'topen', 'lclose', 'now', 'chg_value', 'chg_percent', 'high', 'low')), cls=CJsonEncoder)
            price_online_per_stock['price'] = price
            price_online.append(price_online_per_stock)
    # print(price_online)
    return price_online