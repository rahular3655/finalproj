from django.shortcuts import render
from products.models import *
from django.http import HttpResponse
from products.views import *
from extra.models import *
# Create your views here.

def category_products(request,id,slug):
    categoriess = Categories.objects.all()
    products = Product.objects.filter(category_id=id)
    product_count = products.count()
    for r in products:
        try:
            Coffer = OfferCategory.objects.get(category= r.category)
            cat    = Coffer.discount
            if Coffer:
                r.discount = int(r.price - (r.price*(cat/100)))
                r.save()
            if not Coffer:
                r.discount = None 
                r.save()
        except Exception as e :
            print(e)
            r.discount = None 
            r.save()
    context = {
        'category':categoriess,
        'product': products,
        'product_count' :product_count,
    }
    return render(request,'categorieslist.html',context)