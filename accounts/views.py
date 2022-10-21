import os
import random

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from twilio.rest import Client

from accounts.models import accounts
from cart.models import Cart, Cartitem
from cart.views import _cart_id
from products.views import *
from shoeieeproj.views import home


# Create your views here.
def signin(request):
    if 'username' in request.session:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')    

        user = authenticate(email = email,password = password)
        
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = Cartitem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = Cartitem.objects.filter(cart=cart)
                    
                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass
            
            request.session['username'] = email
            auth.login(request,user)
            return redirect(home)

            # return redirect()
        else:
            messages.error(request,'Enter correct details')
            return redirect(signin)
    return render(request,'login.html')


def signup(request):
    if 'username' in request.session:
        return redirect('home')
    if request.method =='POST':
            username=request.POST['username']
            phone_number = request.POST.get('phone_number')
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if password1 == password2:
                if username== "":
                    messages.error(request,"username is empty")
                    return render(request,'signup.html')
                elif len(username)<2:
                    messages.error(request,"username is too short")
                    return render(request,'signup.html')
                elif not username.isalpha():
                    messages.error(request,"username must contain alphabets")
                    return render(request,'signup.html')
                elif not username.isidentifier():
                    messages.error(request,"username must start with alphabet")
                    return render(request,'signup.html')
                elif email=="":
                    messages.error(request,"email field is empty")
                    return render(request,'signup.html')
                elif len(email)<2:
                    messages.error(request,"emailid is too short")
                elif accounts.objects.filter(email=email):
                    messages.error(request,"email is already exist,try another")
                    return render(request,'signup.html')
                else:
                    user1=accounts.objects.create_user(username=username,first_name=first_name,last_name=last_name,password=password1,email=email,phone_number=phone_number)
                    user1.is_staff = False
                    user1.is_admin = False
                    user1.save()
                    username = user1
                    global otps 
                    otps = str(random.randint(1000,9999))
                    print(otps,"-----------------------------------------------otp")
                    
                    
                    
                    account_sid = settings.ACCOUNT_SID
                    auth_token = settings.AUTH_TOKEN
                    client=Client(account_sid,auth_token)
                    verification = client.verify \
                        .services(settings.SERVICE) \
                        .verifications \
                        .create(to='+91'+phone_number,channel='sms')
                    
                    context = {'username':username,'phone_number':phone_number}
                    return render(request,'otp.html',context)
            else:
                messages.success(request,"password does not match")
                return redirect(request,'signup.html')
    else:
        return render(request,'signup.html')


def otpcheck (request,phone_number):
    
    if request.method == "POST":
        phone_num = "+91"+ str(phone_number)
        otp_input = request.POST['first']

        try:
            if len(otp_input)  >0:


                    account_sid = settings.ACCOUNT_SID
                    auth_token = settings.AUTH_TOKEN
                    
                    client = Client(account_sid, auth_token)

                    otp_check = client.verify \
                                        .services(settings.SERVICE) \
                                        .verification_checks \
                                        .create(to= phone_num, code= otp_input)


                    if otp_check.status == "approved":
                        user = accounts.objects.get(phone_number =phone_number )
                        user.is_active = True   
                        user.Phonenumber = phone_number        
                        user.save()          
                        auth.login(request,user)
                        return redirect(signin)
        except:
                return redirect(signin)

    else:
        return render(request, 'otp.html', {'phone_number': phone_number} )
        
        
        if otp is not None:
            if first==otp:
                messages.success(request,"Your account is registered")
                return redirect(signin)
            else:
                return redirect(signup)
        else:
            messages.error(request,"Otp error.Please check the otp or try again")
            return render (request,'otp.html')
        
        
def otp_view(request):
       

        if request.method == 'POST':
            phone_number = request.POST.get('phone_number')
         
            if accounts.objects.filter(phonenumber = phone_number).exists():
                users = accounts.objects.get(phonenumber = phone_number)
                phone_num = "+91"+ phone_number
                account_sid = settings.ACCOUNT_SID
                auth_token = settings.AUTH_TOKEN
               
                request.session['email'] = users.email

                client=Client(account_sid,auth_token)
                verification = client.verify \
                    .services(settings.SERVICE) \
                    .verifications \
                    .create(to=phone_num,channel='sms')
                
                #messages.success(request,'OTP has been sent to ' + str(phone_num))
               
                return JsonResponse({'phone': True,  'phone_number':phone_number}, safe=False)

            elif  len(phone_number) < 10 or len(phone_number) > 10 :
                 
                #messages.error(request, '10 digits number required')
                return JsonResponse({'success': True}, safe=False)

            else:
                #messages.error(request, 'Invalid Phone Number')
                return JsonResponse({'success': False}, safe=False)




        
        return render(request, 'otp_view.html ')
       

def otp_login(request, phone_number):


    if request.method == 'POST':
        if accounts.objects.filter(phonenumber= phone_number).exists():
            user = accounts.objects.get(phonenumber= phone_number)


            phone_num = "+91"+ str(phone_number)
            otp_input = request.POST['otp']

            if len(otp_input)  >0:

                
                account_sid = settings.ACCOUNT_SID
                auth_token = settings.AUTH_TOKEN
                
                client = Client(account_sid, auth_token)

                otp_check = client.verify \
                                    .services(settings.SERVICE) \
                                    .verification_checks \
                                    .create(to= phone_num, code= otp_input)


                if otp_check.status == "approved":
                    request.session['username'] = user.email
                    auth.login(request, user)
                    return JsonResponse({"phone" :True }, safe= False)

                else:
                    return JsonResponse({"phone" :False }, safe= False)
            else:
                
                return JsonResponse({"success" : True }, safe= False)

        else:
            return JsonResponse({"success" : False }, safe= False)

    return render(request, 'otp_login.html',{'phone_number':phone_number})
        
    
def signout(request):
    if 'username'in request.session:
        request.session.flush()
    logout(request)
    return redirect(signin)

def otp_ver(request):
    user_name = request.GET.get('username')
    phonenumber = request.GET.get('phonenumber')
    
    
    if request.method == "POST":
        
        otp_input = request.POST['first']+request.POST['second']+request.POST['third']+request.POST['fourth']
        if otps ==otp_input:
            user = accounts.objects.get(email=user_name)
            user.is_active = True
            user.phonenumber = phonenumber
            user.save()
            auth.login(request,user)
            return redirect('login')
        else :
            messages.error(request,"Invalid OTP.Try again with correct OTP")
            return render(request,'phoneverification.html',{'phonenumber':phonenumber,'user_name':user_name})
    
    else:
        return render (request,'otp.html',{'username':user_name,'phonenumber':phonenumber})
            
                 
    