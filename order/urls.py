from django.urls import path
from .import views

urlpatterns = [
    path('place_order/',views.place_order, name='place_order'),
    # path('addressfield/',views.addressfield, name='addressfield'),
    path('paymentpage/',views.paymentpage, name='paymentpage'),
    path('',views.payments,name='payments'),
    path('order_complete/',views.order_complete,name='order_complete'),
    path('cash_on_delivery/',views.cash_on_delivery,name='cash_on_delivery'),
    path('paymentsrazor/',views.paymentsrazor,name='paymentsrazor'),
]