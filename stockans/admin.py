from django.contrib import admin
from . import models as stockans_models


# Register your models here.
class StockProfileAdmin(admin.ModelAdmin):
    list_display = ['stock_code', 'stock_abb', 'exchange_no', 'stock_style', 'general_capital', 'circulating_capital', 'listing_date']
    search_fields = ['stock_code', 'stock_abb']


admin.site.register(stockans_models.StockProfile, StockProfileAdmin)
admin.site.register(stockans_models.StockPriceHis)
admin.site.register(stockans_models.StockBigExchange)
admin.site.register(stockans_models.StockPriceOnLine)
admin.site.register(stockans_models.AttentionedStock)
