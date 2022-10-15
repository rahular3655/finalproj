from django.db import models
from accounts.models import *
from products.models import *

# Create your models here.


class shippingaddress(models.Model):
    
    user = models.ForeignKey(accounts,on_delete=models.CASCADE,null=True)
    first_name=models.CharField(max_length=50,null=True)
    last_name = models.CharField(max_length=50,null=True)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, blank=True)
    phonenumber = models.CharField(max_length=15,blank=True,null=True)
    email = models.EmailField(max_length=100,blank=True,null=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.id)
    
    
class Wishlist(models.Model):
    user=models.ForeignKey(accounts,on_delete=models.CASCADE)
    wished_product=models.ForeignKey(Product,on_delete = models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)