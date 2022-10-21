from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from xhtml2pdf import pisa

from accounts.models import *
from accounts.views import *
from accounts.views import home, signin
from order.models import Order, OrderProduct
from shoeieeproj.views import *

from .models import *

# Create your views here


def userhome(request):
    if request.user is not None:
    
        userinfo = shippingaddress.objects.filter(user=request.user)
        print(shippingaddress)
        return render(request,'userprofile/base.html',{'userinfo':userinfo})
    
    
# theproduct = Product.objects.all()
#     paginator = Paginator(theproduct, 5)
#     page = request.GET.get('page')
#     paged_product = paginator.get_page(page)
#     return render(request,'adminss/products.html',{'theproduct':paged_product})

def orderedlist(request):
    if request.user is not None:
        orderlist = OrderProduct.objects.filter(user=request.user)
        paginator = Paginator(orderlist, 5)
        page = request.GET.get('page')
        paged_order = paginator.get_page(page)
        
        return render(request,'userprofile/orderlist.html',{'values':paged_order})
    

def cancelorder(request,id):
    if request.user is not None:
        order=Order.objects.get(id=id)
        if order.status=="Out For Delivery":
            order.status = 'Out For Delivery'
            order.save()
            return redirect(orderedlist)
        else:
            order.status = 'Cancelled'
            order.save()
            return redirect(orderedlist)
        
def returnord (request,id):
    if request.user is not None:
        order=Order.objects.get(id=id)
        if order.status=="Delivered":
            order.status = 'Returned'
            order.save()
            return redirect(orderedlist)
        else:
            order.status = 'Returned'
            order.save()
            return redirect(orderedlist)
    
        
def add_address(request):
    if request.user is not None:
        if request.method=="POST":
            first = request.POST['first_name']
            second = request.POST['last_name']
            addone = request.POST['address_line_1']
            addtwo = request.POST['address_line_2']
            phone = request.POST['phone_number']
            state = request.POST['state']
            country = request.POST['country']
            email = request.POST['email']
            city = request.POST['city']
            pincode=request.POST['pincode']
            
            add = shippingaddress(first_name=first,last_name=second,address_line_1=addone,address_line_2=addtwo,phonenumber=phone,country=country,email=email,city=city,pincode=pincode,state=state,user=request.user)
            add.save()
            return redirect(userhome)
    return render (request,'checkout.html')

def redirect_addressadd(request):
    if request.user is not None:
        return render(request,'checkout.html')
    else:
        return redirect(signin)
            
            
def add_to_wishlist(request,id):
    wish = get_object_or_404(Product,id=id)
    Wishlist.objects.get_or_create(wished_product=wish,user=request.user)
    messages.success(request,'The item is added to your wishlist')
    return redirect(view_wishlist)

def view_wishlist(request):
    wishlist =  Wishlist.objects.filter(user = request.user)
    return render(request, 'userprofile/wishlist.html', {'wishlist' :wishlist })

def remove_wishlist(request, id):
    wishlist = Wishlist.objects.get(user = request.user, id=id)
    wishlist.delete()
    return redirect(view_wishlist)


def changepassword(request):
    if request.method == 'POST':
        current_pass = request.POST.get('current_pass')
        new_pass     = request.POST.get('new_pass')
        confirm_pass     = request.POST.get('confirm_pass')

        account = accounts.objects.get(username = request.user)
        password = account.check_password(current_pass)

        if new_pass == confirm_pass:
            if password : 
                account.set_password(new_pass)
                account.save()
                login(request, account)

                messages.success(request, "Your password has been changed")
                return redirect('userhome')
            else:
                messages.error(request, "Password does not exist")
                return redirect('changepassword')
    return render(request, "userprofile/changepassword.html")

def invoice_download(request):
    if request.method == "POST":
        order_number = request.POST['order_number']
        transID = request.POST['payment_id']
        
        print(order_number, '126')

        # try:
        print('djfnjnf127')
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        print('djfnjnf130')
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        print('djfnjnf134')
        payment = Payment.objects.get(payment_id=transID)
        discount_total = ((subtotal + order.tax)-order.order_total )
        template_path = 'pdf/invoice.html' 
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            'discount_total': discount_total,
        }
        print('djfnjnf147')
        response = HttpResponse(content_type ='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="invoice_report.pdf"'
    
        template = get_template(template_path)

        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
        html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
        
        # except (Payment.DoesNotExist, Order.DoesNotExist):
        
        return redirect('home')