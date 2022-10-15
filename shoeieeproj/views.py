from urllib import request
from django .shortcuts import render, redirect
from products.models import *
from django.views.decorators.cache import cache_control

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    if request.user.is_authenticated or 'username' in request.session:
        products = Product.objects.all().filter(is_available=True)
        category = Categories.objects.all()
        context = {
            'products': products,
            'category': category,
        }
    else:
        products = Product.objects.all().filter(is_available=True)
        category = Categories.objects.all()
        context = {
            'products': products,
            'category': category,
        }
    return render(request, 'landingpage.html', context)
