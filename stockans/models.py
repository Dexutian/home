from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class StockProfile(models.Model):
    """
    股票概要信息
    """
    class Meta:
        verbose_name = _('股票概要信息')
        verbose_name_plural = _('股票概要信息')

    company_code = models.CharField(unique=True, max_length=7, verbose_name=_('公司简称'))
    company_abb = models.CharField(null=True, max_length=100, verbose_name=_('公司代码'))
    exchange_no = models.CharField(null=True, max_length=100, verbose_name=_('交易所代码'),
                                   help_text=_('上交所：SS，深交所：SZ'))
    stock_style = models.CharField(null=True, max_length=100, verbose_name=_('股票类型'),
                                   help_text=_('A/B/H等'))
    stock_code = models.CharField(unique=True, max_length=7, verbose_name=_('股票代码'))
    stock_abb = models.CharField(null=True, max_length=100, verbose_name=_('股票简称'))
    listing_date = models.DateField(null=True, verbose_name=_('挂牌日期'))
    general_capital = models.FloatField(null=True, verbose_name=_('总股本/股'))
    circulating_capital = models.FloatField(null=True, verbose_name=_('流通股本/股'))
    by_sector = models.CharField(null=True, blank=True, max_length=100, verbose_name=_('所属行业'))

    def __str__(self):
        return self.company_abb

    def get_value_in_list(self):
        return [self.company_code, self.company_abb, self.exchange_no]


class StockPriceHis(models.Model):
    """
    股票历史价格
    """
    class Meta:
        verbose_name = _('股票历史价格')
        verbose_name_plural = _('股票历史价格')

    stock = models.ForeignKey(StockProfile, on_delete=models.CASCADE, verbose_name=_('股票'))
    date = models.DateField(null=True, verbose_name=_('日期'))
    tclose = models.FloatField(null=True, verbose_name=_('收盘价/元'))
    high = models.FloatField(null=True, verbose_name=_('最高价/元'))
    low = models.FloatField(null=True, verbose_name=_('最低价/元'))
    topen = models.FloatField(null=True, verbose_name=_('开盘价/元'))
    lclose = models.FloatField(null=True, verbose_name=_('前收盘/元'))
    chg = models.FloatField(null=True, verbose_name=_('涨跌额/元'))
    pchg = models.FloatField(null=True, verbose_name=_('涨跌幅/%'))
    voturnover = models.FloatField(null=True, verbose_name=_('成交量/手'))
    vaturnover = models.FloatField(null=True, verbose_name=_('成交额/元'))

    def __str__(self):
        return self.stock.stock_abb + ' : ' + self.date.strftime('%Y-%m-%d')


class StockBigExchange(models.Model):
    """
    股票大单交易信息
    """
    class Meta:
        verbose_name = _('股票大单交易信息')
        verbose_name_plural = _('股票大单交易信息')

    stock = models.ForeignKey(StockProfile, on_delete=models.CASCADE, verbose_name=_('股票'))
    date = models.DateField(null=True, verbose_name=_('日期'))
    zhulj = models.FloatField(null=True, verbose_name=_('主力净流入额/元'),
                              help_text=_('超大单加大单卖出成交额之和, 净额：流入-流出'))
    per_zhuli = models.FloatField(null=True, verbose_name=_('主力净流入占比/%'),
                                  help_text=_('净比：(流入-流出)/总成交额'))
    chaodd = models.FloatField(null=True, verbose_name=_('超大单净流入额/元'),
                               help_text=_('大于等于50万股或者100万元的成交单, 净额：流入-流出'))
    per_chaodd = models.FloatField(null=True, verbose_name=_('超大单净流入占比/%'),
                                   help_text=_('净比：(流入-流出)/总成交额'))
    dd = models.FloatField(null=True, verbose_name=_('大单净流入额/元'),
                           help_text=_('大于等于10万股或者20万元且小于50万股和100万元的成交单, 净额：流入-流出'))
    per_dd = models.FloatField(null=True, verbose_name=_('大单流入占比/%'),
                               help_text=_('净比：(流入-流出)/总成交额'))
    zd = models.FloatField(null=True, verbose_name=_('中单净流入额/元'),
                           help_text=_('大于等于2万股或者4万元且小于10万股和20万元的成交单, 净额：流入-流出'))
    per_zd = models.FloatField(null=True, verbose_name=_('中单净流入占比/%'),
                               help_text=_('净比：(流入-流出)/总成交额'))
    xd = models.FloatField(null=True, verbose_name=_('小单净流入额/元'),
                           help_text=_('小于2万股和4万元的成交单, 净额：流入-流出'))
    per_xd = models.FloatField(null=True, verbose_name=_('小单净流入占比/%'),
                               help_text=_('净比：(流入-流出)/总成交额'))

    def __str__(self):
        return self.stock.stock_abb + ' : ' + self.date.strftime('%Y-%m-%d')


class StockPriceOnLine(models.Model):
    """
    股票实时价格
    """
    class Meta:
        verbose_name = _('股票实时价格')
        verbose_name_plural = _('股票实时价格')

    stock = models.ForeignKey(StockProfile, on_delete=models.CASCADE, verbose_name=_('股票'))
    date = models.DateField(null=True, verbose_name=_('日期'))
    time = models.TimeField(null=True, verbose_name=_('时间'))
    topen = models.FloatField(null=True, verbose_name=_('开盘价/元'))
    lclose = models.FloatField(null=True, verbose_name=_('前收盘/元'))
    now = models.FloatField(null=True, verbose_name=_('当前价/元'))
    high = models.FloatField(null=True, verbose_name=_('最高价/元'))
    low = models.FloatField(null=True, verbose_name=_('最低价/元'))
    buy_vs = models.FloatField(null=True, verbose_name=_('竞买价/元'))
    sale_vs = models.FloatField(null=True, verbose_name=_('竞卖价/元'))
    voturnover = models.FloatField(null=True, verbose_name=_('成交量/手'))
    vaturnover = models.FloatField(null=True, verbose_name=_('成交金额/元'))
    buy1_num = models.FloatField(null=True, verbose_name=_('买一数/手'))
    buy1_price = models.FloatField(null=True, verbose_name=_('买一价/元'))
    buy2_num = models.FloatField(null=True, verbose_name=_('买二数/手'))
    buy2_price = models.FloatField(null=True, verbose_name=_('买二价/元'))
    buy3_num = models.FloatField(null=True, verbose_name=_('买三数/手'))
    buy3_price = models.FloatField(null=True, verbose_name=_('买三价/元'))
    buy4_num = models.FloatField(null=True, verbose_name=_('买四数/手'))
    buy4_price = models.FloatField(null=True, verbose_name=_('买四价/元'))
    buy5_num = models.FloatField(null=True, verbose_name=_('买五数/手'))
    buy5_price = models.FloatField(null=True, verbose_name=_('买五价/元'))
    sale1_num = models.FloatField(null=True, verbose_name=_('卖一数/手'))
    sale1_price = models.FloatField(null=True, verbose_name=_('卖一价/元'))
    sale2_num = models.FloatField(null=True, verbose_name=_('卖二数/手'))
    sale2_price = models.FloatField(null=True, verbose_name=_('卖二价/元'))
    sale3_num = models.FloatField(null=True, verbose_name=_('卖三数/手'))
    sale3_price = models.FloatField(null=True, verbose_name=_('卖三价/元'))
    sale4_num = models.FloatField(null=True, verbose_name=_('卖四数/手'))
    sale4_price = models.FloatField(null=True, verbose_name=_('卖四价/元'))
    sale5_num = models.FloatField(null=True, verbose_name=_('卖五数/手'))
    sale5_price = models.FloatField(null=True, verbose_name=_('卖五价/元'))

    def __str__(self):
        return self.stock.stock_abb + ' : ' + self.date.strftime('%Y-%m-%d') + ' ' + self.time.strftime('%H:%M:%S %f')


class AttentionedStock(models.Model):
    """
    关注的股票
    """
    class Meta:
        verbose_name = _('关注的股票')
        verbose_name_plural = _('关注的股票')

    attention_time = models.DateTimeField(auto_now_add=True, verbose_name=_('关注时间'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('用户'))
    stock = models.ManyToManyField(StockProfile, verbose_name=_('关注的股票'))
