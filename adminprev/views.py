import datetime

import xlwt
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.views.decorators.cache import cache_control
from xhtml2pdf import pisa

from accounts.models import accounts
from categories.models import Categories
from extra.models import Coupon, OfferCategory, OfferProduct
from order.models import Order, OrderProduct, Payment
from products.models import Product, Variation

# Create your views here.


@cache_control(no_cache =True, must_revalidate =True, no_store =True)
def adminsignin(request):
        if 'username' in request.session:
            return redirect(adminhome)

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            print(user)
            if user is not None and user.is_superuser==True:
                request.session['username'] = username
                login(request, user)
                return redirect(adminhome)
            else:
                messages.error(request, "enter correct details")
                return redirect(adminsignin)
        return render(request, 'adminss/signin1.html')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminhome(request):
    if 'username' in request.session:
        # values=accounts.objects.all()
        order = Payment.objects.filter(payment_method = 'COD')
        codtotal = 0
        cod = 0
        for ord in order:
            codtotal = codtotal + float(ord.amount_paid)
            cod+= 1
            
        
        order = Payment.objects.filter(payment_method = 'Paypal')
        paytotal = 0
        pay = 0
        for ord in order:
            paytotal = paytotal+float(ord.amount_paid)
            pay += 1
            
        order = Payment.objects.filter(payment_method = 'Razorpay')
        raztotal = 0
        raz = 0
        for ord in order:
            raztotal = raztotal+float(ord.amount_paid)
            raz += 1
            
        total = raztotal + codtotal + paytotal
        
        context = {
            'codtotal': codtotal,
            'paytotal':paytotal,
            'total':total,
            'cod': cod,
            'pay': pay,
            'raztotal':raztotal,
        }
        return render(request, 'adminss/dashboard.html', context)


def deleteuser(request,id):
    #  if request.method =='POST': 
        deluser=accounts.objects.get(id=id)
        deluser.delete()

        return redirect(adminhome)

def updateuser(request,id):
    myuser = accounts.objects.get(id=id)

    if request.method =='POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email  = request.POST.get('email')
        # myuser = User.objects.get(id=id)
        myuser.first_name=first_name
        myuser.last_name=last_name
        myuser.email=email
        myuser.save()
        return redirect(adminhome)

    return render(request,'updateuser.html',{"values":myuser})
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutadmin(request):
    if 'username' in request.session:
        request.session.flush()
    logout(request)
    return redirect(adminsignin)         
def search(request):

    if request.method == 'POST':
        searchvalue = request.POST.get('search')
        searchdata = accounts.objects.filter(username__icontains = searchvalue)

    values = {
            'searchresult':searchdata
        }
    return render(request,'search.html',values)

def product(request):
    theproduct = Product.objects.all()
    paginator = Paginator(theproduct, 5)
    page = request.GET.get('page')
    paged_product = paginator.get_page(page)
    return render(request,'adminss/products.html',{'theproduct':paged_product})

def deleteproduct(request, id):
    deleteproduct = Product.objects.get(id=id)
    deleteproduct.delete()
    return redirect(product)

def addproduct(request):
    values = Categories.objects.all()
    if request.method =='POST':
        name = request.POST.get('name')
        catslug = name.replace(" ","-").lower()
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category = request.POST.get('category')
        image = request.FILES.get('image')
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        x = Categories.objects.get(id=category)
        prod=Product(product_name=name,slug=catslug,description=description,price=price,stock=stock,category=x,image=image,image1=image1,image2=image2,image3=image3)
        
        prod.save()
        
        
        return redirect(product)
    context = {
            'values':values,
        } 
    
    return render(request,'adminss/addproduct.html',context)

def editproduct(request,id):
    productedit = Product.objects.get(id=id)
    if request.method == 'POST':
        if len(request.FILES) != 0: 
            if productedit.image : productedit.image = request.FILES.get('image')
            if productedit.image1 :productedit.image1 = request.FILES.get('image1')
            if productedit.image2 :productedit.image2 = request.FILES.get('image2')
            if productedit.image3 :productedit.image3 = request.FILES.get('image3')
        productedit.product_name=request.POST.get('name')
        productedit.description=request.POST.get('description')
        productedit.category=request.POST.get('category')
        productedit.price=request.POST.get('price')
        productedit.stock=request.POST.get('stock')
        if productedit.price <"0" or productedit.stock <'0':
            messages.error(request,'Please fill with correct value')
            return redirect('editproduct',id)
        productedit.save()
        return redirect('editproduct')
    
    product = Product.objects.get(id=id)
    categoryy = Categories.objects.all()
    context = {
        'product': product,
        'values':categoryy
    }
    return render(request,'adminss/editproduct.html',context)

def variationlist(request):
    products = Product.objects.all().order_by('id')
    variations = Variation.objects.all().order_by('id')
    print(variations)

    
    paginator = Paginator(variations, 10)
    page = request.GET.get('page')
    paged_variations = paginator.get_page(page)

    context = {
        'variations': paged_variations,
        'products' : products,
        'variation':variations
    }

    return render(request, 'adminss/variationlist.html', context )

def addvariation(request):

    prod = Product.objects.all()
    variations = Variation()

    print(request.POST)
    if request.method == "POST":


        variations.product_id = request.POST['proucts']
        variations.variation_category = 'size'
        variations.variation_value = request.POST['variation_value']

        if len(variations.variation_value.strip()) == 0 :
            return redirect('addvariation')
        
        else:   
            variations.save()
            return redirect ('variationlist')

    return render(request,'adminss/addvariation.html',{'products':prod})

def editvariation(request,id):
    variations = Variation.objects.get(id=id)
    print(request.POST)
    if request.method=='POST':
        prod=request.POST.get('proucts')
        value=request.POST.get('variation_value')
        var=Variation.objects.get(id=id)
        var.product_id=prod 
        var.variation_category='size'
        var.variation_value = value
        if len(var.variation_value.strip()) == 0 :
            messages.error(request,'error occured')
            return redirect('editvariation')
        else:   
            var.save()
            return redirect('variationlist')
    context = { 'variations' : variations,
                }
    print(context)
    return render(request, "adminss/editvariation.html", context)


def deletevariation(request, id):
        variations = Variation.objects.filter(id = id)
        variations.delete()
        return redirect('variationlist')

def addcategory(request):
    values =Categories.objects.all()
    if request.method =='POST':
        gender = request.POST.get('gender')
        slug = gender.replace(" ","-").lower()
        description = request.POST.get('description')
        variables = Categories(category_name=gender,slug=slug,description=description)
        
        variables.save()
        return redirect(categoryList)
    return render(request,'adminss/addcategory.html',{'values':values})


def addsubcategory(request):
    values =Categories.objects.all()
    if request.method =='POST':
        maincat = request.POST.get('category')
        subcat = request.POST.get('newsub')
        slug = str(subcat+subcat).replace(" ","-").lower()
        description = request.POST.get('description')
        variables = Categories(parent_id=maincat,category_name=subcat,slug=slug,description=description)
        print(slug)
        variables.save()
        return redirect(categoryList)
    return render(request,'adminss/addsubcategory.html',{'values':values})


def user_list(request):
    theuser = accounts.objects.all()
    print(theuser)
    return render (request,'adminss/usertable.html',{'theuser':theuser})

def block_user(request,id):
    x=accounts.objects.get(id=id)
    if x.is_active:
        x.is_active = False
    else:
        x.is_active = True
    x.save()
    return redirect(user_list)

def categoryList(request):
    # if 'username'in request.session:
        values = Categories.objects.all()
        return render(request,'adminss/category.html',{'values':values})
    

def editcategory(request,id):
    values = Categories.objects.get(id=id)
    if request.method =='POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        cat = Categories.objects.get(id=id)
        cat.name = name
        cat.description=description
        cat.save()
        
    return render(request,'adminss/editcategory.html',{'values':values})

def deletecategory(request,id):
    my_cat = Categories.objects.get(id=id)
    my_cat.delete()
    return redirect(categoryList)
        
def orderlist(request):
    if 'username' in request.session:
        values = OrderProduct.objects.all()
        print(values)
        payment = Payment.objects.all()
        paginator = Paginator(values, 8)
        page = request.GET.get('page')
        paged_order = paginator.get_page(page)
        context={
            'values':paged_order,
            'payment':payment,
        }
        return render(request,'adminss/orderlist.html',context)
    return redirect('adminsignin')

def orderdetail (request,id):
     if 'username' in request.session:
            values = OrderProduct.objects.get(id=id)
            print(values)
            context={
                'values':values
            }
            return render (request,'adminss/orderdetail.html', context)


def change_status(request,id):
    if "username" in request.session:
        if request.method == "POST":
            status = request.POST.get("status")
            orders = Order.objects.get(id=id)
            orders.status= status
            print(status)
            orders.save()
            return redirect(orderlist)
 
        
def product_change_status(request,id):
    if "username" in request.session:
        if request.method == "POST":
            status = request.POST.get("status")
            orderproduct = Order.objects.get(id=id)
            orderproduct.status= status
            print(status)
            orderproduct.save()
        return redirect('orderlist')  

        
def view_coupon(request):
    coupons =Coupon.objects.all().order_by("id")
    return render(request,"adminss/coupon.html",{'coupons':coupons})

def addcopnredirect(request):
    coupon = Coupon.objects.all()
    return render (request ,'adminss/addcoupon.html',{'coupon':coupon})


def AddCoupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        discount    = request.POST.get('discount')
        print(coupon_code,"Coupon Code ---------------")
        print(discount, "Discount percentage")
        if coupon_code == '':
            messages.error(request, 'You have not entered a coupon code')
        else:
            coupon = Coupon(coupon_code= coupon_code, discount = discount)
            coupon.save()
            return redirect('couponlist')
    return render(request, 'adminss/addcoupon.html')
    
    
def DeleteCoupon(request, id):
    coupon = Coupon.objects.get(id=id)
    coupon.delete()
    return redirect(view_coupon)


def ListOffer(request):
    CategOffer = OfferCategory.objects.all()
    ProdOffer  = OfferProduct.objects.all()
    context = {
        'OfferC' : CategOffer,
        'OfferP' : ProdOffer,
    }
    return render(request, 'adminss/offerlist.html', context)

def cateofferdelete(request,id):
    coffer=OfferCategory.objects.get(id=id)
    coffer.delete()
    return redirect('ListOffer')

def prodofferdelete(request,id):
    poffer=OfferProduct.objects.get(id=id)
    poffer.delete()
    return redirect('ListOffer')

def addcatoffer (request):
    values = Categories.objects.all()
    if 'username' in request.session:
        
        coffer = OfferCategory.objects.all()
        print(request.POST,'frcvgbhnjmk654616')
        if request.method== 'POST':
            category = request.POST['category_id']
            print(category)
            discount = request.POST['discount']
            discount=int(discount)
            
            if OfferCategory.objects.filter(category=category).exists():
                messages.error(request,'offer already exist for this category')
                return redirect ('addcatoffer')
            if discount>0:
                if discount<90:
                    catobj=Categories.objects.get(id=category)
                    newcatoff=OfferCategory()
                    newcatoff.discount=discount
                    newcatoff.category=catobj
                    newcatoff.save()
                    return redirect('addcatoffer')
                else:
                    messages.error(request,"Discount ,ust be less than 90%")
                    return redirect('addcatoffer')
            else:
                messages.error(request,"Discount must be greater than 0%")
                return redirect('addcatoffer') 
        return render (request,'adminss/addcatoffer.html',{'values':values})
                    
    context = {
        'values':values 
    }
    return render (request,'adminss/addcatoffer.html',context) 



def addprooffer(request):
    products=Product.objects.all()
    if request.method=="POST":
        discount=request.POST.get("discount")
        choosed_product=request.POST.get("product_name")
        if discount =='':
            messages.error(request,"discount field should not be empty")
            return redirect(addprooffer)
        discount=int(discount)
        if OfferProduct.objects.filter(product=choosed_product).exists():
            messages.info(request,"Offer already exists for this Product")
            return redirect(ListOffer)
        discount=int(discount)
        if discount>0:
            if discount<90:
                newProductOffer=OfferProduct()
                newProductOffer.discount=discount
                # newProductOffer.product=Product.objects.get(id=choosed_product)
                product=Product.objects.get(id=choosed_product)
                product.discount=(product.price-(product.price*discount/100))
                print('product',product.discount)
                product.save()
                print('product',product.discount)
                newProductOffer.product=Product.objects.get(id=choosed_product)
                newProductOffer.save()
                return redirect(ListOffer)
            else:
                messages.error(request,"Discount must be less than 90%")
                return redirect(addprooffer)
        else:
                messages.error(request,"Discount must be greater than 0%")
                return redirect(ListOffer)
    return render(request,'adminss/addprooffer.html',{'Products':products})    


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
  
            
            
def salesreport(request):
    salesreport = OrderProduct.objects.all().order_by('id')
    paginator = Paginator(salesreport,15)
    page = request.GET.get('page')
    paged_sales = paginator.get_page(page)
    if request.method  == 'POST':
        search = request.POST["salesreport_search"]
        salesreports = OrderProduct.objects.filter(order_id__contains = search)
        context = {
            'salesreport':salesreports
        }
        return render (request,"adminss/salesreport.html",context)
   
    context = {
            'salesreport':paged_sales
        }
    return render (request,"adminss/salesreport.html",context)



def date_range(request):
    if request.method == "POST":
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        if len(fromdate)>0 and len(todate)> 0 :
            frm = fromdate.split("-")
            tod = todate.split("-")

            fm = [int(x) for x in frm]
            todt = [int(x) for x in tod]

            salesreport = OrderProduct.objects.filter(created_at__date__gte = datetime.date(fm[0],fm[1],fm[2]),created_at__date__lte=datetime.date(todt[0],todt[1],todt[2]) )

            context = {
                'salesreport':salesreport,
            }

            return render(request,'adminss/salesreport.html',context)

        else:
            salesreport = OrderProduct.objects.all()
            context = {
                'salesreport': salesreport ,

             }
            


    return render (request,"adminss/salesreport.html",context)



def monthly_report(request,date):
    frmdate = date
    fm = [2022, frmdate, 1]
    todt = [2022,frmdate,28]

    salesreport = OrderProduct.objects.filter(created_at__date__gte = datetime.date(fm[0],fm[1],fm[2]),created_at__date__lte=datetime.date(todt[0],todt[1],todt[2])).order_by("-id")
    if len(salesreport)>0:
        context = {
            'salesreport':salesreport,
        }
        return render(request,'adminss/salesreport.html',context)

    else:
        messages.error(request,"No Orders")
        return render(request,'adminss/salesreport.html')
    
    
def yearly_report(request,date):
    frmdate = date
    fm = [frmdate, 1, 1]
    todt = [frmdate,12,31]

    salesreport = OrderProduct.objects.filter(created_at__date__gte = datetime.date(fm[0],fm[1],fm[2]),created_at__date__lte=datetime.date(todt[0],todt[1],todt[2])).order_by("-id")
    if len(salesreport)>0:
        context = {
            'salesreport':salesreport,
        }
        return render(request,'adminss/salesreport.html',context)

    else:
        messages.error(request,"No Orders")
        return render(request,'adminss/salesreport.html') 
    
    
    
    
    
def export_pdf(request):
    
    total_with_offer = None
    products = Product.objects.all()
    
    
    dates_date =OrderProduct.objects.values('created_at__date').distinct().order_by('created_at__date')
    
   
    dates=[]
    for dd in dates_date:
        
       
        dates.append(dd['created_at__date'].strftime("%Y-%m-%d"))
    
    try:
            
        dates_max=dates[-1]
        salesdate=dates[-1]
    except:
        dates_max=''
        salesdate=''
    current_date =dates_max
    dates_len =len(dates)
    dates_len-=dates_len
  
    try:
        sales = OrderProduct.objects.filter(created_at__date=dates[-1]).values('product_id').annotate(qty=Sum('quantity'))
        grandtotalfind=OrderProduct.objects.filter(created_at__date=dates[-1]).all()
        total_without_discount=0
        for t in grandtotalfind:
            total_without_discount+=(t.product.price)*(t.quantity)
    except:
        sales=[]
    # get total money earned in day qty*productprice
        try:
            total_earn= Payment.objects.filter(created_at=dates[-1]).aggregate(Sum('amount_paid'))
        except:
            pass
    try:
              total_earn= Payment.objects.filter(created_at=salesdate).all()
              total=0
              for t in total_earn:
                total+=float(t.amount_paid)
    except:
            total="calculating"
    if request.method=="POST":
        try:
            salesdate =request.POST['salesdate_pdf_id']
            sales = OrderProduct.objects.filter(created_at__date=salesdate).values('product_id').annotate(qty=Sum('quantity'))
            grandtotalfind=OrderProduct.objects.filter(created_at__date=salesdate).all()
            total_without_discount=0
            total_with_offer=0
            for t in grandtotalfind:
                total_without_discount+=(t.product.price)*(t.quantity)
                total_with_offer+=(t.product_price)*(t.quantity)
            
            for s in sales:
                    pass
            current_date=salesdate
        except KeyError:
            pass
            salesdate=dates_max
      
        try:
              total_payment= Payment.objects.filter(created_at__date=salesdate).all()
              total=0
              for t in total_payment:
                total+=float(t.amount_paid)
        except:
            total="calculating"    

    template_path = 'exports/salesreport.html'  
    context= {
      'dates':dates,
      'dates_max':dates_max,
      'current_date':current_date,
      'sales':sales,
      'products':products,
      'salesdate':salesdate,
      'total':total,
      'total_without_discount':total_without_discount,
      'total_with_offer' : total_with_offer,

    }



    response = HttpResponse(content_type ='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="salesreport.pdf"'
   
    template = get_template(template_path)

    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response



import csv

from django.http import HttpResponse


def download_csv(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename=SalesReport' + str(datetime.datetime.now())+'.csv'
    writer  = csv.writer(response)
    writer.writerow(['order ','name ','amount ','date'])
    salesreport = OrderProduct.objects.all()

    for sale in salesreport:
        writer.writerow([sale.order.order_number, sale.user.username, sale.order.order_total, sale.created_at ])
    return response




def download_excel(request):
    response = HttpResponse(content_type = 'application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=SalesReport' + str(datetime.datetime.now())+'.xls'
    wb       = xlwt.Workbook(encoding = 'utf-8')
    ws       = wb.add_sheet('SalesReport')
    row_num  = 0
    font_style= xlwt.XFStyle()
    font_style.font.bold = True
    columns   = ['order ','name ','amount ','date ']


    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = OrderProduct.objects.all().values_list('order_id','user','payment','created_at')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num,col_num, str(row[col_num]),font_style)

    wb.save(response)

    return response