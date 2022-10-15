from tkinter import CASCADE
from unicodedata import category
from django.urls import reverse
import code
from django.db import models
from pickle import TRUE
from categories.models import Categories
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
    
class Product(models.Model):
    product_name = models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500,blank=True)
    price = models.FloatField(validators=[MinValueValidator(0)])
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    discount = models.IntegerField(null= True, default= 0 )
    category = models.ForeignKey(Categories,on_delete=models.CASCADE)
    # subcat = models.ForeignKey(Subcategories,on_delete=models.CASCADE,null="false")
    image = models.ImageField(upload_to='photos/products')
    image1 = models.ImageField(upload_to='photos/products')
    image2 = models.ImageField(upload_to='photos/products') 
    image3 = models.ImageField(upload_to='photos/products')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])
    
    def __str__(self):
        return self.product_name

class Brand(models.Model):
    name= models.CharField(max_length=200,unique=True)
    # category = models.ForeignKey(Categories,on_delete=models.CASCADE)

class VariationManager(models.Manager):
    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size',is_active=True)
    
variation_category_choice = (
    ('size','size'),
)
    
class Variation(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField(max_length = 100 ,choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    
    objects = VariationManager()
    
    def __unicode__(self) :
        return self.product
    
    