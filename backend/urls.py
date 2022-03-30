from django.urls import path
from . import views

urlpatterns = [
    path('getProducts', views.getProducts, name='getProducts'),
    path('orders', views.orders, name='orders'),
    path('mailing', views.mailing, name='mailing'),
]
