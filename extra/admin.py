from django.contrib import admin
from .models import *

# Register your models here.
class CouponAdmin(admin.ModelAdmin):
    list_display = ['coupon_code','discount','is_active']
    list_filter = ['is_active']
    search_fields = ['coupon_code']
    
    
admin.site.register(Coupon,CouponAdmin)
admin.site.register(CouponUsedUser)
admin.site.register(OfferCategory)
admin.site.register(OfferProduct)