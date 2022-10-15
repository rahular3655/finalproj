from datetime import timezone
from django.shortcuts import render,redirect
from cart.views import cart
from django.core.exceptions import ObjectDoesNotExist
from extra.forms import CoupnApplyForm
from order.models import *
from order.views import *
from .models import *
from django.contrib import messages
from cart.views import *

# Create your views here.


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon dows not exists")
        return redirect('checkout')
    
    
def coupon_apply(request):
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        print(coupon_code,'sdghveysdguywufbeurugheirigro')
        try :
            if Coupon.objects.get(coupon_code=coupon_code):
                coupon_exist = Coupon.objects.get(coupon_code=coupon_code)
                try:
                    if CouponUsedUser.objects.get(user= request.user,coupon= coupon_exist):
                        messages.error(request,"coupon already applied")
                        return redirect(checkout)  
                
                except:
                    request.session["coupon_code"] = coupon_code
            else:
                messages.error(request, "coupon aleardy don't exists")
                return redirect (checkout) 
            
        except : 
            messages.error(request,"coupon don't exists")
        return redirect(checkout) 
    
    