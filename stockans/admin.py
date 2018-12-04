from django.contrib import admin
from . import models as stockans_models


# Register your models here.
class StockProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'stock_code', 'stock_abb', 'exchange_no', 'stock_style', 'general_capital', 'circulating_capital', 'listing_date', 'by_sector']
    search_fields = ['stock_code', 'stock_abb']

    list_per_page = 15


class AttentionedStockAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'stock', 'stock_code', 'attention_time']
    search_fields = ['user__username', 'stock__stock_code']
    raw_id_fields = ('stock', )

    def stock_code(self, obj):
        return obj.stock.stock_code
    stock_code.short_description = '关注的股票代码'


admin.site.register(stockans_models.StockProfile, StockProfileAdmin)
admin.site.register(stockans_models.StockPriceHis)
admin.site.register(stockans_models.StockBigExchange)
admin.site.register(stockans_models.StockPriceOnLine)
admin.site.register(stockans_models.AttentionedStock, AttentionedStockAdmin)
