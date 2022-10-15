import datetime
from turtle import home
from django.shortcuts import render,redirect
from cart.models import *
from .models import *
from .forms import OrderForm
from products.models import *
import json
from django.http import JsonResponse
from shoeieeproj.views import home
import razorpay
from django.views.decorators.cache import cache_control
from django.conf import settings

# Create your views here.

def payments(request,reduced_price=None):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()
    
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    cart_item = Cartitem.objects.filter(user=request.user)
    for item in cart_item:
        print('39999')
        orderproduct = OrderProduct()
        orderproduct.order_id= order.id
        orderproduct.payment = payment 
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        if reduced_price != None:
            orderproduct.product_price = reduced_price
        else:
            orderproduct.product_price = item.product.price
        orderproduct.ordered = True 
        orderproduct.save()
        
        cart_item = Cartitem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()
        
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
        # if 'coupon' in request.session:
        #     coupon=request.session['coupon']
        #     try:
        #         coupon_used = CouponUsedUser(coupon= coupon, user = request.user)
        #         coupon_used.save()
        #     except Exception as e:
        #         print(e, "In except for deleting coupon")
        # if 'coupon' in request.session:
        #     del request.session['coupon']
    
    Cartitem.objects.filter(user=request.user).delete()
    
    data = {
        'order_number': order.order_number,
        'transID' : payment.payment_id,
    }
    return JsonResponse(data)
        
    
    return render(request,'payments.html')


def paymentsrazor(request,reduced_price=None):
    
    response = request.POST
    # order_number = request.GET.get('razorpay_order_id')
    order_number = request.POST['order_number']
    print(order_number,'errorrrrrrrrrrrrr')
    params_dict = {
        'razorpay_order_id' : response['razorpay_order_id'],
        'razorpay_payment_id' : response['razorpay_payment_id'],
        'razorpay_signature' : response['razorpay_signature']
    }
    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
    status = client.utility.verify_payment_signature(params_dict)
    payment = Payment.objects.get(payment_id = response['razorpay_order_id'])
    payment.status = 'COMPLETED'
    payment.save()
    
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    cart_item = Cartitem.objects.filter(user=request.user)
    for item in cart_item:
        print('39999')
        orderproduct = OrderProduct()
        orderproduct.order_id= order.id
        orderproduct.payment = payment 
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        if reduced_price != None:
            orderproduct.product_price = reduced_price
        else:
            orderproduct.product_price = item.product.price
        orderproduct.ordered = True 
        orderproduct.save()
        
        cart_item = Cartitem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()
        
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
        # if 'coupon' in request.session:
        #     coupon=request.session['coupon']
        #     try:
        #         coupon_used = CouponUsedUser(coupon= coupon, user = request.user)
        #         coupon_used.save()
        #     except Exception as e:
        #         print(e, "In except for deleting coupon")
        # if 'coupon' in request.session:
        #     del request.session['coupon']
    
        Cartitem.objects.filter(user=request.user).delete()
    
        try:
            order = Order.objects.get(order_number=order_number, is_ordered=True)
            ordered_products = OrderProduct.objects.filter(order_id=order.id)

            subtotal = 0
            for i in ordered_products:
                subtotal += i.product_price * i.quantity
        
            context = {
                'order': order,
                'order_number': order.order_number,
                'transID' : payment.payment_id,
                'payment': payment, 
                'subtotal': subtotal,
            }
        except:
            pass


        return render(request, 'ordercomplete.html' ,context )
        


def place_order(request,total=0,quantity=0):
    
    current_user = request.user
    
    
    cart_items=Cartitem.objects.filter(user=current_user)
    cart_count = cart_items.count()
   
    if cart_count <= 0:
        return redirect('store')
    grand_total = 0
    tax = 0
    if request.user.is_authenticated:
            if "coupon_code" in request.session:
                coupon_code = request.session['coupon_code']
                coupon= Coupon.objects.get(coupon_code=coupon_code)
                request.session['coupon']
                reduction=coupon.discount
            else:
                reduction = 0
   
    for cart_item in cart_items:
        if cart_item.product.discount :
            total += (cart_item.product.discount * cart_item.quantity)
        else:
            total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2*total)/100
    grand_total = total-reduction*total/100
    
        
        
    if request.method == 'POST':
        payment_method=request.POST['payment_method']
        
        if payment_method=="Paypal":
            form = OrderForm(request.POST)
        
            if form.is_valid():
                data = Order()
                data.user = current_user
                
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.phone = form.cleaned_data['phone']
                data.email = form.cleaned_data['email']
            
                data.address_line_1 = form.cleaned_data['address_line_1']
                data.address_line_2 = form.cleaned_data['address_line_2']
                data.country = form.cleaned_data['country']
                data.state = form.cleaned_data['state']
                data.city = form.cleaned_data['city']
            

                data.pincode = form.cleaned_data['pincode']
                data.order_total = grand_total
                data.tax = tax
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()
                
                #for order number
                yr = int(datetime.date.today().strftime('%Y'))
                dt = int(datetime.date.today().strftime('%d'))
                mt = int(datetime.date.today().strftime('%m'))
                d = datetime.date(yr,mt,dt)
                current_date = d.strftime("%Y%m%d")
                order_number = current_date + str(data.id)
                data.order_number = order_number
                data.save()
                
                order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
                context = {
                    'order': order,
                    'cart_items':cart_items,
                    'total':total,
                    'tax':tax,
                    'grand_total':grand_total,
                }
                return render(request,'paymentspaypal.html',context)
            
            
        elif payment_method=="Cod":
            form = OrderForm(request.POST)
            cart_items=Cartitem.objects.filter(user=current_user)
    
            if form.is_valid():
                data = Order()
                data.user = current_user
                
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.phone = form.cleaned_data['phone']
                data.email = form.cleaned_data['email']
            
                data.address_line_1 = form.cleaned_data['address_line_1']
                data.address_line_2 = form.cleaned_data['address_line_2']
                data.country = form.cleaned_data['country']
                data.state = form.cleaned_data['state']
                data.city = form.cleaned_data['city']
            

                data.pincode = form.cleaned_data['pincode']
                data.order_total = grand_total
                data.tax = tax
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()
                
                #for order number
                yr = int(datetime.date.today().strftime('%Y'))
                dt = int(datetime.date.today().strftime('%d'))
                mt = int(datetime.date.today().strftime('%m'))
                d = datetime.date(yr,mt,dt)
                current_date = d.strftime("%Y%m%d")
                order_number = current_date + str(data.id)
                data.order_number = order_number
                data.save()
                
                order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
                context = {
                    'order': order,
                    'cart_items':cart_items,
                    'total':total,
                    'tax':tax,
                    'grand_total':grand_total,
                }
                print(context)
                return render(request,'paymentscod.html',context)
            else:
                return redirect(home)
        
        elif payment_method=="Razorpay":
            form = OrderForm(request.POST)
            # order_number = request.GET.get('')
            cart_items=Cartitem.objects.filter(user=current_user)
            currency = 'INR'
            amount = int(grand_total) * 100 # Rs. 200

            razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            # Create a Razorpay Order
            razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                            currency=currency,
                                                            payment_capture='0'))
             # order id of newly created order.
            razorpay_order_id = razorpay_order['id']
            razorpay_order_status = razorpay_order['status']

            if razorpay_order_status == 'created':
                user = current_user
                payment = Payment(
                    user_id = user.id,
                    payment_id = razorpay_order_id,
                    amount_paid = amount/100,
                    payment_method = 'Razorpay'


                )
                payment.save()
                
            callback_url = 'paymenthandler/'
            
                # we need to pass these details to frontend.

    
            if form.is_valid():
                data = Order()
                data.user = current_user
                
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.phone = form.cleaned_data['phone']
                data.email = form.cleaned_data['email']
            
                data.address_line_1 = form.cleaned_data['address_line_1']
                data.address_line_2 = form.cleaned_data['address_line_2']
                data.country = form.cleaned_data['country']
                data.state = form.cleaned_data['state']
                data.city = form.cleaned_data['city']
            

                data.pincode = form.cleaned_data['pincode']
                data.order_total = grand_total
                data.tax = tax
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()
                
                #for order number
                yr = int(datetime.date.today().strftime('%Y'))
                dt = int(datetime.date.today().strftime('%d'))
                mt = int(datetime.date.today().strftime('%m'))
                d = datetime.date(yr,mt,dt)
                current_date = d.strftime("%Y%m%d")
                order_number = current_date + str(data.id)
                print(order_number,'eorkinggggggggggggggggggggg')
                data.order_number = order_number
                data.save()
                
                
                order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
                context = {
                    'order_number' : order_number,
                    'order': order,
                    'cart_items':cart_items,
                    'total':total,
                    'tax':tax,
                    'grand_total':grand_total,
                    'razorpay_order_id' : razorpay_order_id,
                    'razorpay_merchant_key' : settings.RAZOR_KEY_ID,
                    'razorpay_amount' : amount,
                    'currency' : currency,
                    'callback_url' : callback_url
                }
                print(context)
                return render(request,'paymentsrazorpay.html',context)
            
            else:
                return render(request,'payment.html',context)
    else:
        return redirect('checkout')   
     
     
   
def cash_on_delivery(request,reduced_price=None):
    user = request.user
    cart_items = Cartitem.objects.filter(user=user)
    # carrt = Cart.objects.get(user=request.user)
    profile = Order.objects.filter(user=user).last()
    print(profile,'jyggjyggjbjbb')

    user = request.user
    first_name = profile.first_name
    last_name = profile.last_name
    phone_number = profile.phone
    email = user.email
    country = profile.country
    state = profile.state
    pincode = profile.pincode
    order_total =profile.order_total
    tax =profile.tax
    ip = request.META.get('REMOTE_ADDR')
    order=Order.objects.create(user=user,first_name=first_name,last_name=last_name,phone=phone_number,country=country,state=state,pincode=pincode,ip=ip, order_total = order_total, email=email,tax=tax)
    order.save()        

    order_id_generated = str(int(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
    order.order_number = order_id_generated
    order.save()
    order_id_generated = str(int(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
    order.order_number = order_id_generated

    request.session['order_id'] = order.order_number
    order.save()
    order_id = order.order_number          
    orders = Order.objects.get(user=user,order_number=order_id)
            
    request.session['order_id'] = order.order_number
        
    payment = Payment()
    payment.user = user
    payment.payment_id = order_id
    payment.payment_method = 'COD'
    payment.amount_paid=order.order_total

    payment.status = 'Pending'
    payment.save()
    order.payment=payment
    order.is_ordered =True
    order.save()
    cart_itm = cart_items

    for item in cart_items:
        order_product = OrderProduct()
        order_product.order = order
        order_product.payment = payment
        order_product.user = item.user
        order_product.product = item.product
        order_product.quantity =  item.quantity
        if reduced_price != None:
            order_product.product_price = reduced_price
        else:
            order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        product =  Product.objects.get(id = item.product.id)
        product.stock = product.stock - item.quantity

        if product.stock <= 0:
            product.Is_available = False
        product.save()
        item.delete()
        # if 'coupon' in request.session:
        #     coupon=request.session['coupon']
        #     try:
        #         coupon_used = CouponUsedUser(coupon= coupon, user = request.user)
        #         coupon_used.save()
        #     except Exception as e:
        #         print(e, "In except for deleting coupon")
        # if 'coupon' in request.session:
        #     del request.session['coupon']
    order_product = OrderProduct.objects.filter(user=user,payment = payment )

    total = order.order_total


    context ={ 
        'order_product':order_product,
        'cart_itm':cart_itm,
        'order':order,
        'total': total,    
    }
    return render(request,'ordercomplete.html',context)
            

def paymentpage(request):
    return render(request,'payments.html')



@cache_control(no_cache =True, must_revalidate =True, no_store =True)         
def order_complete (request):
    
    try:
   
        order_number = request.GET.get('order_number')
        transID = request.GET.get('payment_id')
        try:
            order = Order.objects.get(order_number = order_number, is_ordered= True)
            ordered_products = OrderProduct.objects.filter(order_id = order.id)
            
            subtotal = 0 
            for i in ordered_products:
                subtotal += i.product * i.quantity
                payment = Payment.objects.get(payment_id = transID)
            
            context = {
                'order':order,
                'ordered_products': ordered_products,
                'order_number': order.order_number,
                'transID':payment.payment_id,
                'payment':payment,
                'subtotal':subtotal,
            }
            print(context)
            return render(request,'ordercomplete.html',context)
        except (Payment.DoesNotExist, Order.DoesNotExist):
            return redirect('home')
    except: 
        return redirect('cart')




