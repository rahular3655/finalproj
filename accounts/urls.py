from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns =[
    path('login',views.signin,name='login'),
    path('signup',views.signup,name='signup'),
    path('signout',views.signout,name='signout'),
    path('otp_ver',views.otp_ver,name='otp_ver'),
    path('otpcheck/<int:phone_number>',views.otpcheck,name='otpcheck'),
    path('otp_view/',views.otp_view, name='otp_view'),
    path('otp_login/<int:phone_number>/',views.otp_login, name='otp_login'),
    path('otp_login/',views.otp_login, name='otp_login'),
    
    
]