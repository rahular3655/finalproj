from django.urls import path
from .import views

urlpatterns = [
    path('<int:id>/<slug:slug>',views.category_products,name='category_products')
]