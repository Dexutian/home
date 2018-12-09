from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError


class ExtraStockProfileManager(models.Manager):
    def update_by_bulk(self, list):
        """
        捆绑更新记录
        :return:
        """
        if list is not None:
            for instance in list:
                self.update_or_create(
                    stock_code=instance[4],
                    defaults={
                    'company_code': instance[0],
                    'company_abb': instance[1],
                    'exchange_no': instance[2],
                    'stock_style': instance[3],
                    'stock_abb': instance[5],
                    'listing_date': instance[6],
                    'general_capital': instance[7],
                    'circulating_capital': instance[8],
                    'by_sector': instance[9],
                }
                )
            return len(list)
        else:
            return 0


class ExtraAttentionedStockManager(models.Manager):
    def get_attentioned_stock_by_user(self, request):
        """
        通过登录的用户获取关注的股票
        :param request:
        :return:
        """
        stock_queryset = self.filter(user=request.user).values('stock__stock_code', 'stock__stock_abb')
        return stock_queryset


class ExtraStockPriceOnLineManager(models.Manager):
    def create_obj_by_list(self, list):
        """
        用价格列表更新记录
        :return:
        """
        if list is not None:
            stock = StockProfile.objects.get(exchange_no=list[0], stock_code=list[1])
            obj = self.create(
                stock=stock,
                topen=list[2],
                lclose=list[3],
                now=list[4],
                high=list[5],
                low=list[6],
                buy_vs=list[7],
                sale_vs=list[8],
                voturnover=list[9],
                vaturnover=list[10],
                buy1_num=list[11],
                buy1_price=list[12],
                buy2_num=list[13],
                buy2_price=list[14],
                buy3_num=list[15],
                buy3_price=list[16],
                buy4_num=list[17],
                buy4_price=list[18],
                buy5_num=list[19],
                buy5_price=list[20],
                sale1_num=list[21],
                sale1_price=list[22],
                sale2_num=list[23],
                sale2_price=list[24],
                sale3_num=list[25],
                sale3_price=list[26],
                sale4_num=list[27],
                sale4_price=list[28],
                sale5_num=list[29],
                sale5_price=list[30],
                date=list[31],
                time=list[32],
                chg_value=list[33],
                chg_percent=list[34],
            )
            if obj:
                return True
            else:
                return False

# Create your models here.
class StockProfile(models.Model):
    """
    股票概要信息
    """
    class Meta:
        verbose_name = _('股票概要信息')
        verbose_name_plural = _('股票概要信息')

    company_code = models.CharField(unique=True, max_length=7, verbose_name=_('公司代码'))
    company_abb = models.CharField(null=True, max_length=100, verbose_name=_('公司简称'))
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

    objects = models.Manager()
    extra_objects = ExtraStockProfileManager()

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
    date = models.DateField(null=True, verbose_name=_('日期'))
    time = models.TimeField(null=True, verbose_name=_('时间'))
    chg_value = models.FloatField(null=True, verbose_name=_('涨跌额/元'))
    chg_percent = models.FloatField(null=True, verbose_name=_('涨跌幅'))

    objects = models.Manager()
    extra_objects = ExtraStockPriceOnLineManager()

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
    stock = models.ForeignKey(StockProfile, on_delete=models.CASCADE, verbose_name=_('关注的股票'))

    objects = models.Manager()
    extra_objects = ExtraAttentionedStockManager()

    def clean(self):
        try:
            AttentionedStock.objects.get(user=self.user, stock=self.stock)
            raise ValidationError(
                _('该用户已经关注此股票！')
            )
        except ObjectDoesNotExist:
            super().clean()