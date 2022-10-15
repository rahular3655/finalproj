from django.shortcuts import render, get_object_or_404

from cart.views import _cart_id
from django.db.models import Q

from extra.models import OfferProduct

from .models import Product
from categories.models import Categories
from cart.models import *
from cart.views import *
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_control


# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def store (request,category_slug=None):
    category = None
    products = None
    print(category,"TI")
    
    if category_slug !=None:
        print(category,'gthjfxrdt')
        category = get_object_or_404(Categories, slug=category_slug)
        print(category,'57654151')
        products = Product.objects.filter(category=category,is_available = True)
        paginator = Paginator(products,8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
        
        print(category,'ftgyh7894665')
        
         
    elif category_slug != None:
        category = get_object_or_404(Categories, slug =category_slug)
        print(category,'gthjfxrdt')
        products = Product.objects.filter(category=category)
        paginator = Paginator(products,8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
        
        
        
        
    else:
        print('else is working')
        products = Product.objects.all().filter(is_available =True).order_by('id')
        for r in products:
            try:
                Poffer = OfferProduct.objects.get(product=r.id)
                prod = Poffer.discount
                if Poffer:
                    r.discount = int(r.price - (r.price*(prod/100)))
                    r.save()
                if not prod:
                    r.discount=None 
                    r.save()
            except Exception as e :
                r.discount = None 
                r.save() 
        category = Categories.objects.all()
        paginator = Paginator(products,8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    context = {
        'products':paged_products,
        'product_count' :product_count,
        'category':category
    }
    
    return render (request,'productview.html',context)

def product_detail(request, category_slug, product_slug):
    try:
        category =Categories.objects.get(slug= category_slug)
        products= Product.objects.get(slug= product_slug)
        print(products)
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart = Cartitem.objects.filter(cart__cart_id = _cart_id(request),product = single_product).exists()
    except Exception as e:
        raise e
    
    context = {
        'single_product' : single_product,
        'in_cart' : in_cart,
        'products':products,
        'category':category,
    } 
    return render(request,'productdetail.html',context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products':products,
        'product_count':product_count,
    }
    return render(request,'productview.html',context)
                                           