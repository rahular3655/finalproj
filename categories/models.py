from django.urls import reverse
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

# Create your models here.
class Categories(MPTTModel):
    parent = TreeForeignKey('self',blank=True,null=True,related_name='children',on_delete=models.CASCADE)
    category_name = models.CharField(max_length = 50,unique=True)
    slug = models.SlugField(max_length=100,unique=True)
    discount = models.IntegerField(null= True, default= 0 )
    description = models.CharField(max_length=200, blank=True)
    images = models.ImageField(upload_to='photos/categories', blank=True)
    
    def get_url(self):
        return reverse('products_by_category',args=[self.slug])
    
    def __str__(self):
        return self.category_name
    
    class MPTTMeta:
        order_insertion_by = ['category_name']
    
    def __str__(self):
        full_path = [self.category_name]
        k = self.parent 
        while k is not None:
            full_path.append(k.category_name)
            k = k.parent 
        return ' / '.join(full_path[::-1])


# class Subcategories(models.Model):
#     sub_category_name = models.CharField(max_length=50,unique=True)
#     category=models.ForeignKey(Categories,on_delete=models.CASCADE,null=True)
#     slug = models.SlugField(max_length=100,unique=True)
    
    
#     def get_url(self):
#         return reverse('products_by_subcategory',args=[self.category.slug,self.slug])
    
#     def __str__(self):
#         return self.sub_category_name



