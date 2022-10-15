from datetime import date
from pickle import GLOBAL
from sre_constants import SUCCESS
from django.http import HttpResponse

import json
from django.http import JsonResponse
from multiprocessing import context, reduction
from turtle import home
from django.contrib import messages
from urllib import request
from django.shortcuts import render,redirect,get_object_or_404
from products.models import *
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from userprofile.models import *
from order.models import *
from django.db.models import Q


# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart: 
        cart = request.session.create()
    return cart 

def add_cart (request,product_id):
    
    
    current_user=request.user
    
    print('now i workingiiiiiiiiiiiiii')
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variation = []
    
        if request.method =='POST':
            for item in request.POST:
                key = item 
                value = request.POST[key]
                print('frrtggt',key)
                print('frrtggt',value)
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                    
                except:
                    pass 
        is_cart_item_exists = Cartitem.objects.filter(product=product,user=current_user).exists()
        
        if is_cart_item_exists: 
            
            cart_item = Cartitem.objects.filter(product=product,user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id =  id[index]
                item = Cartitem.objects.get(product=product, id = item_id)
                item.quantity += 1
                item.save()
            else:
                item = Cartitem.objects.create(product = product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation) # cart_item.quantity = cart_tem.quantity +1
                item.save()
        else:
            print ('hahahah')
            cart_item = Cartitem.objects.create (
                product = product,
                quantity = 1,
                user=current_user           
            )
            if len(product_variation)>0:
                print ('lennn',len(product_variation))
                
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    
    #   if user is not auth
    
    else:
        product_variation = []
    
        if request.method =='POST':
            for item in request.POST:
                key = item 
                value = request.POST[key]
                print('frrtggt',key)
                print('frrtggt',value)
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass 
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id= _cart_id(request)
            )
        cart.save()
        
        
        is_cart_item_exists = Cartitem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exists:
            
            cart_item = Cartitem.objects.filter(product=product,cart=cart)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id =  id[index]
                item = Cartitem.objects.get(product=product, id = item_id)
                item.quantity +=1
                item.save()
            else:
                item = Cartitem.objects.create(product = product,quantity=1,cart=cart)
                if len(product_variation)>0:
                    item.variations.clear()
                    
                    item.variations.add(*product_variation) # cart_item.quantity = cart_tem.quantity +1
                item.save()
        else:
            print ('hahahah')
            cart_item = Cartitem.objects.create (
                product = product,
                quantity = 1,
                cart = cart           
            )
            if len(product_variation)>0:
                print ('lennn',len(product_variation))
                
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
    messages.success(request, "Added to cart Successfully")
    return redirect ('cart')


def cart(request,total=0,quantity=0,cart_items=None):
    try:
        tax=0
        cart_items=0
        grand_total=0
        discount = 0 
        coupon_id = request.session.get('coupon_id')
        if request.user.is_authenticated:
            cart_items = Cartitem.objects.filter(user=request.user , is_active = True)
        else:
            cart=Cart.objects.get(cart_id= _cart_id(request))
            cart_items = Cartitem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            if cart_item.product.discount==None:
                cart_discount=0
            else:
                cart_discount=cart_item.product.discount
                
            if cart_discount > cart_item.product.category.discount:
                # total += (int(cart_item.product.price-(cart_item.product.price*cart_item.product.discount * 0.01))* cart_item.quantity)
                total += cart_item.product.discount * cart_item.quantity
                
            else:
                total += cart_item.product.price * cart_item.quantity
                # total+= (int(cart_item.product.price -(cart_item.product.price* cart_item.product.category.discount * 0.01))*cart_item.quantity)
                
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = int(total + tax)
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total' : total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax' : tax,
        'grand_total':grand_total,
        'coupon_id' : coupon_id
    }
        
    return render (request,'cart.html',context)

def remove_cart(request,product_id,cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    q=0
    try:
        if request.user.is_authenticated:
            cart_item = Cartitem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = Cartitem.objects.get(product=product, cart=cart, id=cart_item_id)
            
        if cart_item.quantity >1:
            cart_item.quantity -= 1
            
            cart_item.save()
            q= cart_item.quantity  
        else :
            
            cart_item.delete()   
    except:
        pass
    return HttpResponse(q)


def up_cart(request,product_id,cart_item_id):
    print(product_id,cart_item_id)
    
    product = get_object_or_404(Product, id=product_id)
    q=0
    try:
        if request.user.is_authenticated:
            cart_items = Cartitem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = Cartitem.objects.get(product=product, cart=cart, id=cart_item_id)
            
    
        cart_items.quantity += 1
        if cart_items.quantity>=product.stock:
            messages.error (request,"Quantity must be less than 10")
            return HttpResponse('limit')
        else:
            cart_items.save()
        q= cart_items.quantity
    except:
        pass

    # cart_items = Cartitem.objects.get(product=product, user=request.user, id=cart_item_id)
    prod = Product.objects.get(id=product_id)
    if cart_items.product.discount==None and cart_items.product.category.discount==0:
        
        cart_items.product.discount=0
    elif cart_items.product.discount==0 and cart_items.product.category.discount==None:
        cart_items.product.category.discount=0
        
    if cart_items.product.discount ==0 and cart_items.product.category.discount==0:
        
        total=cart_items.quantity*prod.price
    elif cart_items.product.discount > cart_items.product.category.discount:
        total = cart_items.quantity*prod.discount
    else :
        total = cart_items.quantity* prod.category.discount
    
    print(cart_items.quantity)
    print(int(total))
    print (type(q))
    qty=q
    q=str(q)+"/"+str(total)
    return HttpResponse(q)


def remove_cart_item(request,product_id,cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = Cartitem.objects.get(product=product,user=request.user,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = Cartitem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')
    # return JsonResponse({"success":True},safe= False)

@login_required(login_url='login')
def checkout(request,total=0,quantity=0,cart_items=None):
    #  try:
        address=None
        reduction=0
        coupon_code=None
        total =0
        tax=0
        grand_total =0
        coupon_discount_total=0
        cart_item_id=0
    
        if request.user.is_authenticated:
            if "coupon_code" in request.session:
                coupon_code = request.session['coupon_code']
                coupon= Coupon.objects.get(coupon_code=coupon_code)
                reduction=coupon.discount
            else:
                reduction = 0
            cart_items = Cartitem.objects.filter(user=request.user, is_active=True)
            address = shippingaddress.objects.filter(user=request.user)
            print(address)
            
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = Cartitem.objects.filter(cart=cart, is_active=True)
            
        for cart_item in cart_items:
            if cart_item.product.discount==None:
                cart_discount=0
            else:
                cart_discount=cart_item.product.discount
            if cart_discount > cart_item.product.category.discount:
                total += cart_item.product.discount * cart_item.quantity
            else:
                total+= (int(cart_item.product.price -(cart_item.product.price* cart_item.product.category.discount * 0.01))*cart_item.quantity)
            quantity += cart_item.quantity
            grand_total = total-reduction*total/100
            reduced_price = reduction*total/100
            
        try:
            user_details = accounts.objects.get(id=request.user)
            print("try user_details")
            print(user_details)
        except:
            print("except user details")
            user_details = " "
        try:
            user_address = shippingaddress.objects.get(user_id=request.user)
            print("try useraddress")
            user_address_status = True
            print(user_address)
        except:
            user_address=""
            print("except useraddress")
            user_address_status = False
            
            
        context = {
            'total' : total,
            'quantity': quantity,
            'cart_items': cart_items,
            'tax' : tax,
            'grand_total':grand_total,
            'address':address,
            'user_address':user_address,
            'user_address_status':user_address_status,
            'coupon_code':coupon_code,
            'reduction':reduction,
            'reduced_price' :reduced_price
        }
        return render(request,'404.html',context)
    
