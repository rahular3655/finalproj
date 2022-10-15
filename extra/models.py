from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from categories.models import *
from accounts.models import accounts
from products.models import*

# Create your models here.

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=30,unique=True)
    discount = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.coupon_code 
    
    
    
class CouponUsedUser(models.Model):
    user = models.ForeignKey(accounts, on_delete=models.CASCADE,null=True)
    coupon =models.ForeignKey(Coupon,on_delete=models.CASCADE,null = True)
    status = models.BooleanField(default=False)
    
    
    
class OfferProduct(models.Model):
    product = models.OneToOneField(Product, related_name='category_offers', on_delete=models.CASCADE)
    discount = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(30)],null=True,default = 0)
    is_active = models.BooleanField(default =True)
    class Meta:
        verbose_name = 'Offer Product'
        verbose_name_plural = 'Offer Products'

    def __str__(self):
        return self.product.product_name



class OfferCategory(models.Model):
    category = models.OneToOneField(Categories, related_name='category_offers', on_delete=models.CASCADE)
    discount = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(30)],null=False,default = 0)
    is_active = models.BooleanField(default =True)
    class Meta:
        verbose_name = 'OfferCategory'
        verbose_name_plural = 'Offer Categories'

    def __str__(self):
        return self.category.category_name
    