from django.urls import path
from .import views


urlpatterns = [
    
    path('',views.userhome,name='userhome'),
    path('orderedlist',views.orderedlist,name='orderedlist'),
    path('cancelorder/<int:id>',views.cancelorder,name='cancelorder'),
    path('returnord/<int:id>',views.returnord,name='returnord'),
    path('redirect_addressadd',views.redirect_addressadd,name='redirect_addressadd'),
    path('add_address',views.add_address,name='add_address'),
    path('add_to_wishlist/<int:id>',views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist',views.view_wishlist,name='wishlist'),
    path('remove_from_wishlist/<int:id>',views.remove_wishlist,name='remove_from_wishlist'),
    path('changepassword',views.changepassword,name='changepassword'),
    path('invoice_download',views.invoice_download,name='invoice_download'),
    
]
