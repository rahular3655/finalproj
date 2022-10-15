from django.urls import path, include 
from .import views 
from django.conf import settings


urlpatterns = [
    path('apply_coupon', views.coupon_apply, name='apply_coupon'),
]

