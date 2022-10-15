from django.db import models
from products.models import *
from accounts.models import accounts

# Create your models here.
class Cart (models.Model):
    # user =  models.ForeignKey(accounts, on_delete=models.CASCADE,null=True)
    cart_id = models.CharField(max_length = 250,blank = True)
    date_added = models.DateField(auto_now_add = True)
    
    def _str_(self):
        return self.cart_id
    
    
class Cartitem (models.Model):
    user =  models.ForeignKey(accounts, on_delete=models.CASCADE,null=True)
    variations = models.ManyToManyField(Variation,blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,null=True)
    coupon = models.CharField(max_length=10, null= True, blank= True)
    quantity = models.IntegerField()
    is_active = models.BooleanField (default=True)
    
    def sub_total(self):
        return self.product.price * self.quantity
    
    def _unicode_(self):
        return self.product 
    